"""Combine the original census and its Bedrock remainder without API calls."""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from features.atomic_io import atomic_write_parquet
from features.llm_annotations.pipeline import export_results, load_sample
from features.manual_validation.service import atomic_write_json, sha256_file


OPENAI_RUN_ID = 'pilot_d4e0291b4df3fc0f5343'
BEDROCK_RUN_ID = 'pilot_46d9e036e93e09278292'
COMBINED_ID = 'combined_gpt6luna_20260922'


def main() -> None:
    project = Path.cwd()
    input_root = project / 'data/proc_data/annotations_inputs'
    output_root = project / 'output/annotations'
    openai_input = input_root / OPENAI_RUN_ID
    bedrock_input = input_root / BEDROCK_RUN_ID
    openai_output = output_root / OPENAI_RUN_ID
    bedrock_output = output_root / BEDROCK_RUN_ID
    combined = output_root / COMBINED_ID
    records = load_sample(openai_input)
    bedrock_manifest = json.loads((bedrock_input / 'manifest.json').read_text())
    source_indices = bedrock_manifest['spec']['sampling']['source_indices']
    if len(records) != 3609 or len(source_indices) != 796 or len(set(source_indices)) != 796:
        raise ValueError('El mapa entre el censo y Bedrock no es válido')
    bedrock_lookup = {full_index: local_index for local_index, full_index in enumerate(source_indices)}
    sources = {'openai': 0, 'bedrock': 0}
    for full_index, record in enumerate(records):
        if full_index in bedrock_lookup:
            provider = 'bedrock'
            source_index = bedrock_lookup[full_index]
            source_input = bedrock_input
            source_output = bedrock_output
            source_run_id = BEDROCK_RUN_ID
        else:
            provider = 'openai'
            source_index = full_index
            source_input = openai_input
            source_output = openai_output
            source_run_id = OPENAI_RUN_ID
        source_request = source_input / 'requests' / f'{source_index:05d}.json'
        source_result = source_output / 'results' / f'{source_index:05d}.json'
        if not source_result.exists():
            raise ValueError(f'Falta el bloque {full_index} de {provider}')
        result = json.loads(source_result.read_text())
        if (
            result.get('status') != 'completed'
            or result.get('unit_id') != record['unit_id']
            or result.get('request_sha256') != sha256_file(source_request)
        ):
            raise ValueError(f'El bloque {full_index} de {provider} no es válido')
        if provider == 'bedrock' and result.get('provider') != 'bedrock':
            raise ValueError(f'El bloque {full_index} carece de procedencia Bedrock')
        result.update(
            sample_index=full_index,
            source_sample_index=source_index,
            source_run_id=source_run_id,
            provider=provider,
            model_requested=('global.openai.gpt-6-luna' if provider == 'bedrock' else 'gpt-6-luna'),
            source_result_sha256=sha256_file(source_result),
        )
        path = combined / 'results' / f'{full_index:05d}.json'
        if path.exists():
            existing = json.loads(path.read_text())
            if existing != result:
                raise ValueError(f'El resultado combinado {full_index} ya existe y difiere')
        else:
            atomic_write_json(path, result)
        sources[provider] += 1
    frame = export_results(openai_input, combined)
    if frame['status'].value_counts().to_dict() != {'completed': 3609}:
        raise ValueError('El censo combinado no está completo')
    frame['source_run_id'] = frame['provider'].map({
        'openai': OPENAI_RUN_ID, 'bedrock': BEDROCK_RUN_ID,
    })
    atomic_write_parquet(frame, combined / 'results.parquet')
    import pandas as pd
    spans = pd.read_parquet(combined / 'annotations.parquet')
    spans['source_run_id'] = spans['provider'].map({
        'openai': OPENAI_RUN_ID, 'bedrock': BEDROCK_RUN_ID,
    })
    atomic_write_parquet(spans, combined / 'annotations.parquet')
    manifest = {
        'schema_version': 'combined-annotations-1.0.0',
        'run_id': COMBINED_ID,
        'input_census_run_id': OPENAI_RUN_ID,
        'source_runs': {
            'openai': OPENAI_RUN_ID,
            'bedrock': BEDROCK_RUN_ID,
        },
        'source_manifest_sha256': {
            'openai': sha256_file(openai_input / 'manifest.json'),
            'bedrock': sha256_file(bedrock_input / 'manifest.json'),
        },
        'source_counts': sources,
        'total_completed': len(frame),
        'results_parquet_sha256': sha256_file(combined / 'results.parquet'),
        'annotations_parquet_sha256': sha256_file(combined / 'annotations.parquet'),
        'created_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    atomic_write_json(combined / 'combined_manifest.json', manifest)
    atomic_write_json(combined / 'status.json', {
        'run_id': COMBINED_ID,
        'counts': {'completed': 3609},
        'source_counts': sources,
        'updated_at_utc': manifest['created_at_utc'],
    })
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == '__main__':
    main()
