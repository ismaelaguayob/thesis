"""Freeze only the unfinished census blocks for a Bedrock continuation."""

from __future__ import annotations

import copy
import datetime as dt
import json
from pathlib import Path
from types import SimpleNamespace

from features.llm_annotations.pipeline import (
    DEFAULT_BEDROCK_REGION,
    canonical,
    export_results,
    load_sample,
    prepare_run,
    validate_output,
)
from features.manual_validation.service import atomic_write_json, sha256_file


SOURCE_RUN_ID = "pilot_d4e0291b4df3fc0f5343"
BEDROCK_MODEL = "global.openai.gpt-6-luna"
PROBE_INDICES = (2813, 3264)


def main() -> None:
    project = Path.cwd()
    input_root = project / 'data/proc_data/annotations_inputs'
    output_root = project / 'output/annotations'
    source = input_root / SOURCE_RUN_ID
    source_results = output_root / SOURCE_RUN_ID / 'results'
    source_manifest = json.loads((source / 'manifest.json').read_text())
    spec = source_manifest['spec']
    records = load_sample(source)
    pending_indices = [
        index for index in range(len(records))
        if not (source_results / f'{index:05d}.json').exists()
    ]
    if len(records) != 3609 or len(pending_indices) != 796:
        raise ValueError('Cambió el estado del censo; revisar antes de preparar Bedrock')
    if {records[index]['law_number'] for index in pending_indices} != {'21735'}:
        raise ValueError('Los pendientes no corresponden exclusivamente a la ley 21735')
    book = json.loads((source / 'codebook.json').read_text())
    service = SimpleNamespace(
        codebook=book,
        codebook_sha256=spec['codebook_sha256'],
        sources=spec['sources'],
        party_alignment=SimpleNamespace(snapshot=lambda: spec['party_alignment']),
    )
    sampling = {
        'unit': 'block',
        'strategy': 'remaining_after_openai_spend_limit',
        'source_run_id': SOURCE_RUN_ID,
        'source_indices': pending_indices,
        'eligible_blocks': len(records),
        'selected_blocks': len(pending_indices),
        'blocks_by_law': {'21735': len(pending_indices)},
    }
    bedrock = prepare_run(
        service,
        [records[index] for index in pending_indices],
        sampling,
        source / 'prompt.md',
        input_root,
        model=BEDROCK_MODEL,
        effort=spec['reasoning_effort'],
        max_output_tokens=spec['max_output_tokens'],
        sdk_max_retries=spec['sdk_max_retries'],
        incomplete_retry_max_output_tokens=spec['incomplete_retry_max_output_tokens'],
        provider='bedrock',
        provider_region=DEFAULT_BEDROCK_REGION,
    )
    probe_path = project / 'output/annotations_checks/bedrock_structured_probe_2026-09-22.json'
    probes = {int(p['index']): p for p in json.loads(probe_path.read_text())}
    if set(probes) != set(PROBE_INDICES):
        raise ValueError('Faltan las dos pruebas estructuradas de Bedrock')
    output = output_root / bedrock.name
    for source_index in PROBE_INDICES:
        local_index = pending_indices.index(source_index)
        probe = probes[source_index]
        source_request = json.loads((source / 'requests' / f'{source_index:05d}.json').read_text())
        destination_request_path = bedrock / 'requests' / f'{local_index:05d}.json'
        destination_request = json.loads(destination_request_path.read_text())
        expected_body = copy.deepcopy(source_request['body'])
        expected_body['model'] = BEDROCK_MODEL
        if (
            destination_request['body'] != expected_body
            or destination_request['unit_id'] != source_request['unit_id']
            or probe['unit_id'] != source_request['unit_id']
            or probe['model_requested'] != BEDROCK_MODEL
            or probe['api_status'] != 'completed'
            or probe['local_validation'] != 'passed'
        ):
            raise ValueError(f'La prueba {source_index} no coincide con el request congelado')
        record = records[source_index]
        normalized = validate_output(
            json.loads(probe['output_text']), record, book, spec['output_schema']
        )
        result = {
            'sample_index': local_index,
            'source_sample_index': source_index,
            'unit_id': record['unit_id'],
            'request_sha256': sha256_file(destination_request_path),
            'started_at_utc': probe['at_utc'],
            'finished_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'status': 'completed',
            'provider': 'bedrock',
            'model_requested': BEDROCK_MODEL,
            'validation_errors': [],
            'normalized': normalized,
            'output_text': probe['output_text'],
            'response': probe['response'],
            'attempt_count': 1,
            'max_retries': spec['sdk_max_retries'],
            'attempt_max_output_tokens': spec['max_output_tokens'],
            'imported_from_probe': str(probe_path.relative_to(project)),
        }
        path = output / 'results' / f'{local_index:05d}.json'
        if path.exists():
            if json.loads(path.read_text())['response']['id'] != probe['response']['id']:
                raise ValueError(f'Ya existe otro resultado para {local_index}')
        else:
            atomic_write_json(path, result)
    frame = export_results(bedrock, output)
    counts = frame['status'].value_counts().to_dict()
    if counts != {'pending': 794, 'completed': 2}:
        raise ValueError(f'Conteo inesperado: {counts}')
    print(json.dumps({
        'input_run_dir': str(bedrock),
        'output_run_dir': str(output),
        'counts': counts,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
