"""Read recorded API usage without creating a client or accessing credentials."""
from __future__ import annotations
import json
from pathlib import Path

import pandas as pd

from features.manual_validation.service import ValidationError, sha256_file


def read_response_ledger(run_directories: dict[str, Path]) -> pd.DataFrame:
    """One row per persisted response, with enough provenance to audit token totals."""
    rows = []
    for role, directory in run_directories.items():
        manifest = json.loads((directory / 'manifest.json').read_text())
        for path in sorted((directory / 'results').glob('*.json')):
            result = json.loads(path.read_text())
            response = result.get('response') or {}
            usage = response.get('usage')
            request = directory / 'requests' / f"{result['sample_index']:05d}.json"
            request_digest = sha256_file(request)
            if result.get('request_sha256') != request_digest:
                raise ValidationError(f'Request distinto del registrado en {path}')
            counts = usage or {}
            input_tokens = counts.get('input_tokens')
            output_tokens = counts.get('output_tokens')
            total_tokens = counts.get('total_tokens')
            if usage and total_tokens != input_tokens + output_tokens:
                raise ValidationError(f'Contabilidad de tokens inconsistente en {path}')
            details = (response.get('incomplete_details') or {})
            rows.append({
                'run_id': manifest['run_id'], 'run_role': role, 'sample_index': result['sample_index'],
                'unit_id': result['unit_id'], 'response_id': response.get('id'),
                'model': response.get('model'), 'status': result['status'],
                'api_status': response.get('status'), 'incomplete_reason': details.get('reason'),
                'usage_available': usage is not None, 'input_tokens': input_tokens,
                'cached_input_tokens': (counts.get('input_tokens_details') or {}).get('cached_tokens'),
                'output_tokens': output_tokens,
                'reasoning_tokens': (counts.get('output_tokens_details') or {}).get('reasoning_tokens'),
                'total_tokens': total_tokens, 'response_path': str(path),
                'response_sha256': sha256_file(path), 'request_sha256': request_digest,
                'started_at_utc': result.get('started_at_utc'),
                'finished_at_utc': result.get('finished_at_utc'),
            })
    ledger = pd.DataFrame(rows)
    ledger['duplicate_response_id'] = ledger.response_id.notna() & ledger.response_id.duplicated()
    return ledger
