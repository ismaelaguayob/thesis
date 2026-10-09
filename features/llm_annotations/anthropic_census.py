"""Replicate the frozen Luna-6 census with Claude Haiku 5.5 on Amazon Bedrock.

The run reuses the census' frozen sample, prompt, codebook and per-block user
content byte for byte; only the request envelope changes from the Responses API
to the Messages API. Requests are derived at run time from the census' frozen
requests and checked against per-block digests in the manifest, so the input
folder does not duplicate 3,609 request files. Validation and export are the pipeline's own functions, so
results are comparable block by block with ``openai_gpt6luna_20261002``.

Protocol choices (agreed on 2026-10-08):

- reasoning effort ``max`` with adaptive thinking, the same label as Luna-6;
- four retries, as in Luna-6, but a 65,536-token ceiling raised to 128,000 after
  ``max_tokens`` (Luna: 32,768 and 65,536). The model does not see the ceiling;
  Haiku reasons far longer, and a cut attempt is billed in full (agreed on
  2026-10-08 after a 20-block pilot where 2 blocks exceeded 32,768);
- Bedrock rejects ``maxItems`` and ``minimum`` in structured outputs, so they are
  dropped only from the schema sent to the API; local validation still applies
  the complete frozen schema;
- the instruction block is cached explicitly, which changes cost, not outputs.

Usage:
    python -m features.llm_annotations.anthropic_census --prepare     # local
    python -m features.llm_annotations.anthropic_census               # dry run
    python -m features.llm_annotations.anthropic_census --execute --pilot 20
    python -m features.llm_annotations.anthropic_census --execute
    python -m features.llm_annotations.anthropic_census --release-interrupted
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import datetime as dt
import fcntl
import importlib.metadata
import json
import math
import os
import random
import shutil
import threading
import time
from pathlib import Path
from typing import Any

import anthropic
import jsonschema
from dotenv import load_dotenv

from features.atomic_io import atomic_write_bytes
from features.llm_annotations.pipeline import (
    MAX_WORKERS, REQUEST_TIMEOUT_SECONDS, RUN_ID_RE, _authorize_api_execution,
    _discard_failed_output, _load_retry_seed, canonical, export_results, load_sample,
    validate_output,
)
from features.manual_validation.service import (
    ValidationError, atomic_write_json, sha256_file, sha256_text,
)

RUNNER_VERSION = "llm-anthropic-census-1.0.0"
SOURCE_RUN_ID = "pilot_d4e0291b4df3fc0f5343"
OUTPUT_ID = "bedrock_haiku55_20261008"
PROVIDER = "bedrock"
REGION = "us-west-2"
MODEL = "global.anthropic.claude-haiku-5-5"
EFFORT = "max"
EXPECTED_BLOCKS = 3609
BASE_MAX_TOKENS = 65536
RETRY_MAX_TOKENS = 128000  # Haiku 5.5 output limit.
# JSON Schema keywords that Bedrock structured outputs reject with a 400.
API_UNSUPPORTED_KEYWORDS = frozenset({"maxItems", "minimum"})
# Credential or entitlement failures: every further call would fail the same way.
STOP_STATUS_CODES = frozenset({401, 403})


def api_schema(schema: Any) -> Any:
    """Frozen schema minus the keywords Bedrock rejects; validation keeps them."""
    if isinstance(schema, dict):
        return {key: api_schema(value) for key, value in schema.items()
                if key not in API_UNSUPPORTED_KEYWORDS}
    if isinstance(schema, list):
        return [api_schema(value) for value in schema]
    return schema


def messages_body(source_body: dict, schema: dict) -> dict:
    """Translate one frozen Responses body without touching its texts."""
    (message,) = source_body["input"]
    if message["role"] != "user" or source_body["text"]["format"]["schema"] != schema:
        raise ValidationError("El request congelado no tiene la forma esperada")
    return {
        "model": MODEL,
        "max_tokens": BASE_MAX_TOKENS,
        "system": [{"type": "text", "text": source_body["instructions"],
                    "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": message["content"]}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": EFFORT, "format": {
            "type": "json_schema", "schema": api_schema(schema)}},
    }


def verify_frozen(run_dir: Path) -> dict:
    """Check a run's sample and hashed artifacts; return its manifest."""
    manifest = json.loads((run_dir / "manifest.json").read_text())
    if sha256_file(run_dir / "sample.parquet") != manifest["sample_sha256"]:
        raise ValidationError(f"La muestra congelada fue modificada: {run_dir.name}")
    for name, digest in manifest["artifact_sha256"].items():
        if sha256_file(run_dir / name) != digest:
            raise ValidationError(f"El artefacto congelado fue modificado: {name}")
    return manifest


def frozen_request(source_dir: Path, index: int, schema: dict) -> tuple[dict, dict, str]:
    """Census request, its Messages translation and the translation's digest."""
    request = json.loads((source_dir / "requests" / f"{index:05d}.json").read_text())
    if request["sample_index"] != index:
        raise ValidationError(f"El request {index} está desordenado")
    body = messages_body(request["body"], schema)
    return request, body, sha256_text(canonical(body))


def prepare(source_dir: Path, input_root: Path) -> Path:
    """Freeze the Anthropic run spec next to byte-identical census artifacts."""
    source_manifest = verify_frozen(source_dir)
    source_spec = source_manifest["spec"]
    if source_manifest["sample_size"] != EXPECTED_BLOCKS:
        raise ValidationError("El censo congelado no tiene 3.609 bloques")
    schema = source_spec["output_schema"]
    digests = [frozen_request(source_dir, index, schema)[2]
               for index in range(source_manifest["sample_size"])]
    runner = Path(__file__)
    spec = {
        "pipeline_version": RUNNER_VERSION, "provider": PROVIDER,
        "provider_region": REGION, "api": "anthropic_messages",
        "model": MODEL, "reasoning_effort": EFFORT, "thinking": "adaptive",
        "max_output_tokens": BASE_MAX_TOKENS,
        "sdk_max_retries": source_spec["sdk_max_retries"],
        "incomplete_retry_max_output_tokens": RETRY_MAX_TOKENS,
        "source_max_output_tokens": source_spec["max_output_tokens"],
        "source_incomplete_retry_max_output_tokens": (
            source_spec["incomplete_retry_max_output_tokens"]),
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "sampling": {**source_spec["sampling"], "source_run_id": source_dir.name},
        "sources": source_spec["sources"],
        "prompt_sha256": source_spec["prompt_sha256"],
        "codebook_sha256": source_spec["codebook_sha256"],
        "output_schema": schema,
        "api_output_schema": api_schema(schema),
        "party_alignment": source_spec["party_alignment"],
        # Same model inputs as the census; checked by the tests and below.
        "requests_sha256": source_spec["requests_sha256"],
        "source_run_id": source_dir.name,
        "source_manifest_sha256": sha256_file(source_dir / "manifest.json"),
        "anthropic_requests_sha256": sha256_text(canonical(digests)),
        "runner_sha256": sha256_file(runner),
        "validation_runner_sha256": sha256_file(runner.parent / "pipeline.py"),
        "validation_contract_sha256": sha256_file(
            runner.parents[1] / "manual_validation/service.py"),
    }
    run_id = "pilot_" + sha256_text(canonical(spec))[:20]
    run_dir = input_root / run_id
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if existing["spec"] != spec:
            raise ValidationError("La ejecución existente no coincide con la configuración")
        return run_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    for name in ("sample.parquet", "prompt.md", "codebook.json", "output_schema.json",
                 "validation_contract.py"):
        shutil.copyfile(source_dir / name, run_dir / name)
    atomic_write_bytes((runner.parent / "pipeline.py").read_bytes(), run_dir / "pipeline.py")
    atomic_write_bytes(runner.read_bytes(), run_dir / "anthropic_census.py")
    manifest = {
        "schema_version": RUNNER_VERSION, "run_id": run_id, "spec": spec,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "codebook_version": source_manifest["codebook_version"],
        "prompt_path": source_manifest["prompt_path"],
        "sample_size": source_manifest["sample_size"],
        "sample_sha256": sha256_file(run_dir / "sample.parquet"),
        "artifact_sha256": {str(path.relative_to(run_dir)): sha256_file(path)
                            for path in [run_dir / "prompt.md", run_dir / "codebook.json",
                                         run_dir / "output_schema.json",
                                         run_dir / "pipeline.py",
                                         run_dir / "anthropic_census.py",
                                         run_dir / "validation_contract.py"]},
        "request_sha256": digests,
        "packages": {p: importlib.metadata.version(p)
                     for p in ["anthropic", "pandas", "pyarrow"]},
    }
    if manifest["sample_sha256"] != source_manifest["sample_sha256"]:
        raise ValidationError("La copia de la muestra no es idéntica al censo")
    atomic_write_json(manifest_path, manifest)
    return run_dir


def response_record(message: Any) -> dict:
    """Message in the Responses-shaped fields that export_results reads."""
    raw = message.model_dump(mode="json")
    usage = raw.get("usage") or {}
    cache_read = usage.get("cache_read_input_tokens") or 0
    cache_write = usage.get("cache_creation_input_tokens") or 0
    stop = raw.get("stop_reason")
    status = {"end_turn": "completed", "max_tokens": "incomplete"}.get(stop, "failed")
    return {
        "id": raw.get("id"), "object": "message", "model": raw.get("model"),
        "status": status, "stop_reason": stop,
        "incomplete_details": ({"reason": "max_output_tokens"}
                               if stop == "max_tokens" else None),
        "error": None if status != "failed" else {
            "code": stop, "details": raw.get("stop_details")},
        # OpenAI counts cached tokens inside input_tokens; Anthropic does not.
        "usage": {
            "input_tokens": (usage.get("input_tokens") or 0) + cache_read + cache_write,
            "output_tokens": usage.get("output_tokens") or 0,
            "input_tokens_details": {"cached_tokens": cache_read,
                                     "cache_creation_tokens": cache_write},
            "output_tokens_details": {"reasoning_tokens": (
                usage.get("output_tokens_details") or {}).get("thinking_tokens", 0)},
        },
        "service_tier": usage.get("service_tier"),
        "message": raw,
    }


def run(input_run_dir: Path, result_dir: Path, *, execute: bool, workers: int,
        indices: list[int] | None = None, client: Any = None) -> Any:
    """Send pending frozen requests; same attempt accounting as the pipeline."""
    manifest = json.loads((input_run_dir / "manifest.json").read_text())
    spec = manifest["spec"]
    if execute:
        _authorize_api_execution(input_run_dir, result_dir, manifest)
    verify_frozen(input_run_dir)
    source_dir = input_run_dir.parent / spec["source_run_id"]
    if sha256_file(source_dir / "manifest.json") != spec["source_manifest_sha256"]:
        raise ValidationError("El manifiesto del censo de origen cambió")
    verify_frozen(source_dir)
    records = load_sample(input_run_dir)
    codebook = json.loads((input_run_dir / "codebook.json").read_text())
    schema = spec["output_schema"]
    selected = range(len(records)) if indices is None else indices
    pending = [i for i in selected
               if not (result_dir / "results" / f"{i:05d}.json").exists()]
    if not (execute and pending):
        return export_results(input_run_dir, result_dir)
    max_retries = spec["sdk_max_retries"]
    fallback_token_cap = spec["incomplete_retry_max_output_tokens"]
    if client is None:
        load_dotenv(".env", override=False)
        api_key = os.environ.get("AWS_BEDROCK_API_KEY")
        if not api_key:
            raise ValidationError("Falta AWS_BEDROCK_API_KEY")
        client = anthropic.Anthropic(
            api_key=api_key,
            base_url=f"https://bedrock-runtime.{spec['provider_region']}.amazonaws.com/anthropic",
            timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0,
        )
    stop_all = threading.Event()
    runner_sha256 = sha256_file(Path(__file__))

    def annotate(index: int) -> dict | None:
        if stop_all.is_set():
            return None
        request, body, digest = frozen_request(source_dir, index, schema)
        if digest != manifest["request_sha256"][index]:
            raise ValidationError(f"El request derivado {index} no coincide con el manifiesto")
        seed = _load_retry_seed(result_dir, index)
        prior_attempts = seed["attempt_count"] if seed else 0
        if seed and seed.get("unit_id") != request["unit_id"]:
            raise ValidationError(f"El retry seed {index} no corresponde al request")
        if prior_attempts > max_retries:
            raise ValidationError(f"El bloque {index} ya agotó sus intentos")
        if seed and seed.get("incomplete_reason") == "max_output_tokens":
            body["max_tokens"] = min(seed["last_attempt_max_output_tokens"] * 2,
                                     fallback_token_cap)
        result = {"sample_index": index, "unit_id": request["unit_id"],
                  "provider": PROVIDER, "model_requested": spec["model"],
                  "request_sha256": digest,
                  "source_request_sha256": sha256_file(
                      source_dir / "requests" / f"{index:05d}.json"),
                  "started_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                  "status": "started", "validation_errors": [], "normalized": None,
                  "output_text": "", "response": None,
                  "attempt_count": prior_attempts, "max_retries": max_retries,
                  "retry_seed": seed, "runner_sha256": runner_sha256}
        path = result_dir / "results" / f"{index:05d}.json"
        # Reserve before sending: an interrupted call is never resent silently.
        atomic_write_json(path, result)
        for attempt in range(prior_attempts, max_retries + 1):
            result["attempt_count"] = attempt + 1
            result["attempt_max_output_tokens"] = body["max_tokens"]
            result["last_attempt_started_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
            atomic_write_json(path, result)
            retryable, retry_delay = False, 0.0
            try:
                with client.messages.stream(**body) as stream:
                    message = stream.get_final_message()
                result["response"] = response_record(message)
                result["output_text"] = "".join(
                    block.text for block in message.content if block.type == "text")
                if message.stop_reason == "end_turn":
                    result["normalized"] = validate_output(
                        json.loads(result["output_text"]), records[index], codebook, schema)
                    result["status"] = "completed"
                    result["validation_errors"] = []
                else:
                    # max_tokens is Responses' incomplete; refusal and any other
                    # stop count as a failed attempt within the same budget.
                    result["status"] = ("incomplete" if message.stop_reason == "max_tokens"
                                        else "error")
                    result["validation_errors"] = [f"stop_reason: {message.stop_reason}"]
                    retryable = True
                    if message.stop_reason == "max_tokens":
                        body["max_tokens"] = min(body["max_tokens"] * 2, fallback_token_cap)
            except (json.JSONDecodeError, jsonschema.ValidationError, ValidationError) as exc:
                result["status"] = "invalid_output"
                result["validation_errors"] = [str(exc)[:2000]]
                retryable = True
            except anthropic.APIStatusError as exc:
                result["status"] = "error"
                result["validation_errors"] = [
                    f"API HTTP {exc.status_code}; detail={str(exc)[:1500]}"]
                # A server error sent mid-stream arrives with the stream's
                # HTTP 200 status; it is as transient as a 5xx.
                retryable = (exc.status_code in {200, 408, 409, 429}
                             or exc.status_code >= 500)
                if exc.status_code in STOP_STATUS_CODES:
                    stop_all.set()
                elif exc.status_code in {200, 429, 503, 529}:
                    raw_delay = exc.response.headers.get("retry-after")
                    try:
                        retry_delay = float(raw_delay) if raw_delay is not None else None
                    except ValueError:
                        retry_delay = None
                    if retry_delay is None or not math.isfinite(retry_delay) or retry_delay < 0:
                        retry_delay = min(60.0, 2.0 ** attempt)
                    retry_delay += random.uniform(0.0, 0.5)
            except (anthropic.APIConnectionError, anthropic.APITimeoutError) as exc:
                result["status"] = "transport_error"
                result["validation_errors"] = [type(exc).__name__]
                retryable = True
            if result["status"] == "completed" or not retryable or attempt >= max_retries:
                break
            print(f"Bloque {index + 1}/{len(records)}: retry {attempt + 1}/{max_retries} "
                  f"tras {result['status']}; próximo max_tokens={body['max_tokens']}",
                  flush=True)
            result.update(status="started", validation_errors=[], normalized=None,
                          output_text="", response=None)
            if retry_delay > 0:
                time.sleep(retry_delay)
        result = _discard_failed_output(result)
        result["finished_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        atomic_write_json(path, result)
        print(f"Bloque {index + 1}/{len(records)}: {result['status']}", flush=True)
        return result

    try:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
            list(pool.map(annotate, pending))
    finally:
        client.close()
    return export_results(input_run_dir, result_dir)


def pilot_indices(total: int, size: int) -> list[int]:
    """Evenly spaced blocks, so a pilot spans laws and sessions."""
    return sorted({math.floor(i * total / size) for i in range(size)})


def release_interrupted(result_dir: Path, base_max_tokens: int) -> list[int]:
    """Turn in-flight reservations into retry seeds that keep their attempt count."""
    released = []
    for path in sorted((result_dir / "results").glob("*.json")):
        result = json.loads(path.read_text())
        if result.get("status") != "started":
            continue
        index = result["sample_index"]
        atomic_write_json(result_dir / "retry_seeds" / f"{index:05d}.json", {
            "source_run": OUTPUT_ID, "sample_index": index, "unit_id": result["unit_id"],
            "status": "transport_error",
            "attempt_count": int(result.get("attempt_count") or 1),
            "incomplete_reason": None,
            "last_attempt_max_output_tokens": int(
                result.get("attempt_max_output_tokens", base_max_tokens)),
            "released_reason": "proceso interrumpido con la llamada en curso",
            "released_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
        destination = result_dir / "interrupted" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        path.replace(destination)
        released.append(index)
    return released


def release_stream_errors(result_dir: Path, max_retries: int) -> list[int]:
    """Reopen blocks that a mid-stream server error closed after one attempt.

    Runner versions before the fix treated those errors (reported with HTTP 200)
    as final. The failed result moves to ``stream_errors/`` for audit and a retry
    seed keeps its attempt count, so the frozen five-attempt limit still applies.
    """
    released = []
    for path in sorted((result_dir / "results").glob("*.json")):
        result = json.loads(path.read_text())
        errors = result.get("validation_errors") or []
        attempts = int(result.get("attempt_count") or 1)
        if (result.get("status") != "error" or attempts > max_retries
                or not any(error.startswith("API HTTP 200;") for error in errors)):
            continue
        index = result["sample_index"]
        atomic_write_json(result_dir / "retry_seeds" / f"{index:05d}.json", {
            "source_run": OUTPUT_ID, "sample_index": index, "unit_id": result["unit_id"],
            "status": "error", "attempt_count": attempts, "incomplete_reason": None,
            "last_attempt_max_output_tokens": int(result["attempt_max_output_tokens"]),
            "released_reason": "error del servidor durante el streaming, no reintentado",
            "released_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        })
        destination = result_dir / "stream_errors" / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        path.replace(destination)
        released.append(index)
    return released


def write_census_manifest(input_run_dir: Path, result_dir: Path) -> Path | None:
    """Mark a fully completed census as the definitive Haiku output."""
    manifest = json.loads((input_run_dir / "manifest.json").read_text())
    results = [json.loads((result_dir / "results" / f"{i:05d}.json").read_text())
               if (result_dir / "results" / f"{i:05d}.json").exists() else {}
               for i in range(manifest["sample_size"])]
    if any(result.get("status") != "completed" for result in results):
        return None
    path = result_dir / "haiku_census_manifest.json"
    atomic_write_json(path, {
        "schema_version": "haiku-census-1.0.0",
        "run_id": result_dir.name,
        "input_run_id": input_run_dir.name,
        "input_manifest_sha256": sha256_file(input_run_dir / "manifest.json"),
        "source_run_id": manifest["spec"]["source_run_id"],
        "provider": PROVIDER, "model_requested": manifest["spec"]["model"],
        "total_completed": len(results),
        "attempts": {str(k): v for k, v in sorted(collections.Counter(
            result["attempt_count"] for result in results).items())},
        "stream_error_recoveries": sorted(
            int(p.stem) for p in (result_dir / "stream_errors").glob("*.json")),
        "runner_sha256": sorted({result.get("runner_sha256")
                                 or manifest["spec"]["runner_sha256"] for result in results}),
        "results_parquet_sha256": sha256_file(result_dir / "results.parquet"),
        "annotations_parquet_sha256": sha256_file(result_dir / "annotations.parquet"),
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
    })
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--prepare", action="store_true", help="Congelar los requests (local)")
    parser.add_argument("--execute", action="store_true", help="Enviar los pendientes a Bedrock")
    parser.add_argument("--pilot", type=int, default=None,
                        help="Enviar solo N bloques espaciados uniformemente")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--release-interrupted", action="store_true",
                        help="Reintentar bloques interrumpidos en estado started")
    parser.add_argument("--release-stream-errors", action="store_true",
                        help="Reintentar bloques cerrados por un error durante el streaming")
    args = parser.parse_args()

    project = Path.cwd()
    input_root = project / "data/proc_data/annotations_inputs"
    source_dir = input_root / SOURCE_RUN_ID
    result_dir = project / "output/annotations" / OUTPUT_ID
    if args.prepare:
        input_dir = prepare(source_dir, input_root)
        print(json.dumps({"input_run_dir": str(input_dir)}, ensure_ascii=False))
        return
    candidates = [path for path in input_root.iterdir()
                  if RUN_ID_RE.fullmatch(path.name) and (path / "anthropic_census.py").exists()]
    if len(candidates) != 1:
        raise ValidationError("Se esperaba exactamente un input preparado; usa --prepare")
    input_dir = candidates[0]
    spec = json.loads((input_dir / "manifest.json").read_text())["spec"]
    if args.release_interrupted:
        released = release_interrupted(result_dir, spec["max_output_tokens"])
        print(json.dumps({"released_interrupted": released}, ensure_ascii=False))
    if args.release_stream_errors:
        released = release_stream_errors(result_dir, spec["sdk_max_retries"])
        print(json.dumps({"released_stream_errors": released}, ensure_ascii=False))
    indices = None if args.pilot is None else pilot_indices(EXPECTED_BLOCKS, args.pilot)
    result_dir.mkdir(parents=True, exist_ok=True)
    if args.execute:
        with (result_dir / ".execution.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ValidationError("Esta ejecución ya tiene un proceso activo") from exc
            frame = run(input_dir, result_dir, execute=True, workers=args.workers,
                        indices=indices)
    else:
        frame = run(input_dir, result_dir, execute=False, workers=args.workers)
    counts = {str(k): int(v) for k, v in frame["status"].value_counts().items()}
    if indices is None and write_census_manifest(input_dir, result_dir):
        print(f"Censo Haiku completo en {result_dir}")
    print(json.dumps({"input_run_dir": str(input_dir), "output_run_dir": str(result_dir),
                      "counts": counts}, ensure_ascii=False))


if __name__ == "__main__":
    main()
