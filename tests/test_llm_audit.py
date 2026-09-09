import json
import tempfile
import unittest
from pathlib import Path

from features.llm_annotations.audit import read_response_ledger
from features.manual_validation.service import ValidationError, sha256_file


class RecordedUsageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def record(self, run, index, response_id, input_tokens, output_tokens):
        directory = self.root / run
        (directory / 'requests').mkdir(parents=True, exist_ok=True)
        (directory / 'results').mkdir(exist_ok=True)
        (directory / 'manifest.json').write_text(json.dumps({'run_id': run}))
        request = directory / 'requests' / f'{index:05d}.json'
        request.write_text('{}')
        result = {
            'sample_index': index, 'unit_id': f'unit-{index}', 'status': 'completed',
            'request_sha256': sha256_file(request),
            'response': {'id': response_id, 'usage': {
                'input_tokens': input_tokens, 'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'input_tokens_details': {'cached_tokens': 60},
                'output_tokens_details': {'reasoning_tokens': 5},
            }},
        }
        (directory / 'results' / f'{index:05d}.json').write_text(json.dumps(result))
        return directory

    def test_unique_responses_and_usage_subsets(self):
        first = self.record('pilot', 0, 'response-1', 100, 20)
        second = self.record('copy', 0, 'response-1', 100, 20)
        self.record('copy', 1, 'response-2', 80, 10)
        ledger = read_response_ledger({'pilot': first, 'copy': second})
        counted = ledger.loc[~ledger.duplicate_response_id & ledger.usage_available]
        self.assertEqual(1, ledger.duplicate_response_id.sum())
        self.assertEqual(210, counted.total_tokens.sum())
        self.assertEqual(180, counted.input_tokens.sum())
        self.assertEqual(30, counted.output_tokens.sum())
        self.assertEqual(120, counted.cached_input_tokens.sum())
        self.assertEqual(10, counted.reasoning_tokens.sum())

    def test_modified_request_is_rejected(self):
        directory = self.record('pilot', 0, 'response-1', 100, 20)
        (directory / 'requests/00000.json').write_text('{"changed":true}')
        with self.assertRaises(ValidationError):
            read_response_ledger({'pilot': directory})

    def test_inconsistent_total_is_rejected(self):
        directory = self.record('pilot', 0, 'response-1', 100, 20)
        path = directory / 'results/00000.json'
        result = json.loads(path.read_text())
        result['response']['usage']['total_tokens'] = 125
        path.write_text(json.dumps(result))
        with self.assertRaises(ValidationError):
            read_response_ledger({'pilot': directory})


if __name__ == '__main__':
    unittest.main()
