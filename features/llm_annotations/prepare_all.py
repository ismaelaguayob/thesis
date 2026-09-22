"""Freeze one local annotation request for every block in the current corpus."""

from __future__ import annotations

from pathlib import Path

from features.llm_annotations.pipeline import execution_config_from_env, prepare_run
from features.manual_validation.codebook_workbook import write_codebook_json
from features.manual_validation.service import ValidationService


def main() -> None:
    project = Path.cwd()
    workbook = project / "features/codebook/codebook_v5.xlsx"
    codebook = workbook.with_suffix(".json")
    write_codebook_json(workbook, codebook)
    service = ValidationService(
        project / "data/proc_data", codebook, project / "output/validation"
    )
    selected = sorted(
        service.records,
        key=lambda record: (
            record["law_number"], record["document_uri"],
            record["utterance_order"], record["utterance_chunk_number"],
        ),
    )
    if len(selected) != sum(source["available_blocks"] for source in service.sources):
        raise ValueError("El censo no cubre todos los bloques de las fuentes")
    model, effort, retries, fallback_tokens = execution_config_from_env()
    sampling = {
        "unit": "block",
        "strategy": "census",
        "fraction": 1.0,
        "eligible_blocks": len(selected),
        "selected_blocks": len(selected),
        "eligible_interventions": len(service.utterances),
        "selected_interventions": len(service.utterances),
        "blocks_by_law": {
            source["law_number"]: source["available_blocks"]
            for source in service.sources
        },
    }
    run_dir = prepare_run(
        service,
        selected,
        sampling,
        project / "prompts/annotations_prompt_final.md",
        project / "data/proc_data/annotations_inputs",
        model=model,
        effort=effort,
        sdk_max_retries=retries,
        incomplete_retry_max_output_tokens=fallback_tokens,
    )
    print(f"Input preparado: {run_dir}")
    print(f"Bloques: {len(selected)}; modelo: {model}; razonamiento: {effort}")


if __name__ == "__main__":
    main()
