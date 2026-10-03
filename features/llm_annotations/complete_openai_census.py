"""Complete the OpenAI census in a new output folder, replacing the Bedrock remainder.

The 22-09 census stopped at the OpenAI spend limit after 2,813 blocks and its 796
remaining blocks were annotated on Bedrock. This script builds a single-provider
census instead: it reuses the 2,813 validated OpenAI responses and sends only the
796 never-attempted blocks to OpenAI, with the census' own frozen requests. The
original run folders are not modified.

Usage:
    python -m features.llm_annotations.complete_openai_census            # dry run
    python -m features.llm_annotations.complete_openai_census --execute --limit 2
    python -m features.llm_annotations.complete_openai_census --execute
    python -m features.llm_annotations.complete_openai_census --release-interrupted

A block left in ``started`` means the process stopped while its call was in flight;
the pipeline never resends it on its own because the call may have been billed.
``--release-interrupted`` is the explicit decision to retry such blocks: it moves the
reserved result to ``interrupted/`` for audit and writes a retry seed that counts the
uncertain attempt, so the frozen attempt limit still applies.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
from pathlib import Path

from features.llm_annotations.pipeline import (
    _run_annotations,
    export_results,
    load_sample,
    reuse_completed_results,
)
from features.manual_validation.service import atomic_write_json, sha256_file


CENSUS_RUN_ID = "pilot_d4e0291b4df3fc0f5343"
BEDROCK_RUN_ID = "pilot_46d9e036e93e09278292"
OUTPUT_ID = "openai_gpt6luna_20261002"
EXPECTED_BLOCKS = 3609
EXPECTED_REUSED = 2813


def release_interrupted(result_dir: Path, max_output_tokens: int) -> list[int]:
    """Turn interrupted reservations into retry seeds that keep their attempt count."""
    released = []
    for path in sorted((result_dir / "results").glob("*.json")):
        result = json.loads(path.read_text())
        if result.get("status") != "started":
            continue
        index = result["sample_index"]
        attempts = int(result.get("attempt_count") or 1)
        atomic_write_json(result_dir / "retry_seeds" / f"{index:05d}.json", {
            "source_run": OUTPUT_ID,
            "sample_index": index,
            "unit_id": result["unit_id"],
            "status": "transport_error",
            "attempt_count": attempts,
            "incomplete_reason": None,
            "last_attempt_max_output_tokens": int(
                result.get("attempt_max_output_tokens", max_output_tokens)
            ),
            "released_reason": "proceso interrumpido con la llamada en curso",
            "released_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
        destination = result_dir / "interrupted" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        path.replace(destination)
        released.append(index)
    return released


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--execute", action="store_true", help="Enviar los pendientes a OpenAI")
    parser.add_argument("--limit", type=int, default=None, help="Máximo de bloques a enviar")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--release-interrupted", action="store_true",
                        help="Reintentar bloques interrumpidos en estado started")
    args = parser.parse_args()

    project = Path.cwd()
    input_dir = project / "data/proc_data/annotations_inputs" / CENSUS_RUN_ID
    original_output = project / "output/annotations" / CENSUS_RUN_ID
    result_dir = project / "output/annotations" / OUTPUT_ID
    records = load_sample(input_dir)
    if len(records) != EXPECTED_BLOCKS:
        raise ValueError("El censo congelado no tiene 3.609 bloques")
    if args.release_interrupted:
        spec = json.loads((input_dir / "manifest.json").read_text())["spec"]
        released = release_interrupted(result_dir, spec["max_output_tokens"])
        print(json.dumps({"released_interrupted": released}, ensure_ascii=False))

    reused = reuse_completed_results(
        input_dir, input_dir,
        source_result_dir=original_output,
        destination_result_dir=result_dir,
    )
    present = {
        index for index in range(len(records))
        if (result_dir / "results" / f"{index:05d}.json").exists()
    }
    pending = sorted(set(range(len(records))) - present)
    bedrock_manifest = json.loads(
        (project / "data/proc_data/annotations_inputs" / BEDROCK_RUN_ID / "manifest.json").read_text()
    )
    bedrock_indices = sorted(bedrock_manifest["spec"]["sampling"]["source_indices"])
    reused_total = sum(
        1 for index in present
        if json.loads((result_dir / "results" / f"{index:05d}.json").read_text()).get(
            "reused_from_run"
        ) == CENSUS_RUN_ID
    )
    if reused_total != EXPECTED_REUSED:
        raise ValueError(f"Se esperaban {EXPECTED_REUSED} respuestas reutilizadas; hay {reused_total}")
    if not set(pending) <= set(bedrock_indices):
        raise ValueError("Hay pendientes que no corresponden a los bloques enviados a Bedrock")
    print(json.dumps({
        "reused_now": reused, "reused_total": reused_total,
        "present": len(present), "pending": len(pending),
    }, ensure_ascii=False))

    if args.execute and pending:
        result_dir.mkdir(parents=True, exist_ok=True)
        # Same guard as run_annotations: one process per output folder.
        with (result_dir / ".execution.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _run_annotations(input_dir, result_dir, True, args.workers, args.limit)

    frame = export_results(input_dir, result_dir)
    counts = {str(k): int(v) for k, v in frame["status"].value_counts().items()}
    print(json.dumps({"counts": counts}, ensure_ascii=False))
    if counts == {"completed": EXPECTED_BLOCKS}:
        if set(frame["provider"]) != {"openai"}:
            raise ValueError("La carpeta contiene respuestas de otro proveedor")
        reused_flags = []
        for index in range(len(records)):
            result = json.loads((result_dir / "results" / f"{index:05d}.json").read_text())
            reused_flags.append(result.get("reused_from_run") == CENSUS_RUN_ID)
        atomic_write_json(result_dir / "openai_census_manifest.json", {
            "schema_version": "openai-census-1.0.0",
            "run_id": OUTPUT_ID,
            "input_run_id": CENSUS_RUN_ID,
            "input_manifest_sha256": sha256_file(input_dir / "manifest.json"),
            "provider": "openai",
            "model_requested": json.loads((input_dir / "manifest.json").read_text())["spec"]["model"],
            "reused_from": {"run_id": CENSUS_RUN_ID, "blocks": sum(reused_flags)},
            "new_calls": {"blocks": len(reused_flags) - sum(reused_flags),
                          "replaces_run_id": BEDROCK_RUN_ID},
            "total_completed": len(frame),
            "results_parquet_sha256": sha256_file(result_dir / "results.parquet"),
            "annotations_parquet_sha256": sha256_file(result_dir / "annotations.parquet"),
            "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
        print(f"Censo OpenAI completo en {result_dir}")


if __name__ == "__main__":
    main()
