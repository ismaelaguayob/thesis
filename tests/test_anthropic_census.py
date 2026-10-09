from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import features.llm_annotations.anthropic_census as census
import features.llm_annotations.pipeline as pipeline
from features.llm_annotations.pipeline import canonical, output_schema, prepare_run
from features.manual_validation.service import sha256_text
from features.political_alignment import PartyAlignment


class AnthropicCensusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for target, value in [
            ('features.llm_annotations.pipeline.API_POLICY_PATH', self.root / 'api_policy.json'),
            ('features.llm_annotations.anthropic_census.EXPECTED_BLOCKS', 1),
        ]:
            patcher = patch(target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.book = {'version': 'test', 'concepts': [
            {'id': 'solidaridad', 'label': 'Solidaridad', 'definition': 'Compartir riesgos.',
             'include': [], 'exclude': [], 'orientation_anchor': 'Compartir riesgos.'}]}
        self.record = dict(unit_id='u1::p1', utterance_id='u1', content='La solidaridad es necesaria.',
                           law_number='21419', document_uri='doc1', date='2026-01-01',
                           constitutional_stage='primer', title='Sesión', paragraph_start=1,
                           paragraph_end=1, paragraph_count=1, n_words=4,
                           previous_context=None, next_context=None, source_segments=[])
        self.raw = {'decision': 'statements', 'annotations': [{
            'evidence_text': 'La solidaridad es necesaria.', 'evidence_occurrence': 1,
            'concept_id': 'solidaridad', 'stance': 'support', 'confidence': 'high',
            'justification': 'Afirma un deber de compartir riesgos.'}],
            'quality_flags': [], 'decision_confidence': 'high'}
        prompt = self.root / 'prompt.md'
        prompt.write_text('Codifica con evidencia exacta.')
        service = SimpleNamespace(
            codebook=self.book, codebook_sha256=sha256_text(canonical(self.book)),
            sources=[{'law_number': '21419', 'sha256': 'fixture'}],
            party_alignment=PartyAlignment(left=('A',), center=('C',), right=('B',),
                                           nonpartisan=('I',)))
        self.source = prepare_run(service, [self.record], {'selected_interventions': 1},
                                  prompt, self.root / 'inputs', 'gpt-6-luna', 'max')
        self.input = census.prepare(self.source, self.root / 'inputs')
        self.output = self.root / 'outputs' / 'haiku'
        spec = json.loads((self.input / 'manifest.json').read_text())['spec']
        pipeline.API_POLICY_PATH.write_text(json.dumps({
            'allow_api_calls': True, 'authorized_runs': {self.input.name: {
                'provider': 'bedrock', 'provider_region': 'us-west-2',
                'model': spec['model'], 'reasoning_effort': 'max',
                'input_run_dir': str(self.input.resolve()),
                'output_run_dir': str(self.output.resolve()), 'max_calls': 5}}}))

    def fake_client(self, *messages):
        client = MagicMock()
        streams = []
        for stop_reason, text in messages:
            message = MagicMock()
            message.stop_reason = stop_reason
            message.content = [SimpleNamespace(type='thinking', thinking=''),
                               SimpleNamespace(type='text', text=text)]
            message.model_dump.return_value = {
                'id': 'msg_1', 'model': 'claude-haiku-5-5', 'stop_reason': stop_reason,
                'usage': {'input_tokens': 10, 'cache_read_input_tokens': 900,
                          'cache_creation_input_tokens': 0, 'output_tokens': 50,
                          'output_tokens_details': {'thinking_tokens': 40}}}
            stream = MagicMock()
            stream.__enter__.return_value.get_final_message.return_value = message
            streams.append(stream)
        client.messages.stream.side_effect = streams
        return client

    def test_requests_keep_frozen_texts_and_drop_only_unsupported_keywords(self):
        source = json.loads((self.source / 'requests/00000.json').read_text())['body']
        manifest = json.loads((self.input / 'manifest.json').read_text())
        _, body, digest = census.frozen_request(
            self.source, 0, manifest['spec']['output_schema'])
        self.assertEqual([digest], manifest['request_sha256'])
        self.assertFalse((self.input / 'requests').exists())
        self.assertEqual(source['instructions'], body['system'][0]['text'])
        self.assertEqual(source['input'][0]['content'], body['messages'][0]['content'])
        self.assertEqual(65536, body['max_tokens'])
        self.assertEqual(128000, manifest['spec']['incomplete_retry_max_output_tokens'])
        self.assertEqual({'effort': 'max', 'format': {
            'type': 'json_schema', 'schema': census.api_schema(source['text']['format']['schema'])}},
            body['output_config'])
        sent = json.dumps(body['output_config'])
        self.assertNotIn('maxItems', sent)
        self.assertNotIn('minimum', sent)
        frozen = output_schema(self.book)
        frozen['properties']['annotations'].pop('maxItems')
        frozen['properties']['annotations']['items']['properties']['evidence_occurrence'].pop('minimum')
        self.assertEqual(frozen, census.api_schema(output_schema(self.book)))
        self.assertEqual(
            (self.source / 'sample.parquet').read_bytes(),
            (self.input / 'sample.parquet').read_bytes())
        self.assertEqual(self.input, census.prepare(self.source, self.root / 'inputs'))

    def test_completed_response_is_validated_and_exported(self):
        client = self.fake_client(('end_turn', json.dumps(self.raw)))
        frame = census.run(self.input, self.output, execute=True, workers=1, client=client)
        row = frame.iloc[0]
        self.assertEqual('completed', row.status)
        self.assertEqual('bedrock', row.provider)
        self.assertEqual(census.MODEL, row.model_requested)
        self.assertEqual(910, row.input_tokens)
        self.assertEqual(900, row.cached_input_tokens)
        self.assertEqual(40, row.reasoning_tokens)
        client.close.assert_called_once()

    def test_frozen_schema_is_still_enforced_locally(self):
        bad = json.loads(json.dumps(self.raw))
        bad['annotations'][0]['evidence_occurrence'] = 0
        client = self.fake_client(*[('end_turn', json.dumps(bad))] * 5)
        frame = census.run(self.input, self.output, execute=True, workers=1, client=client)
        self.assertEqual('invalid_output', frame.iloc[0].status)
        self.assertEqual(5, client.messages.stream.call_count)

    def test_max_tokens_doubles_once_and_refusal_uses_the_same_budget(self):
        client = self.fake_client(('max_tokens', ''), ('refusal', ''),
                                  ('end_turn', json.dumps(self.raw)))
        frame = census.run(self.input, self.output, execute=True, workers=1, client=client)
        limits = [call.kwargs['max_tokens'] for call in client.messages.stream.call_args_list]
        self.assertEqual([65536, 128000, 128000], limits)
        self.assertEqual('completed', frame.iloc[0].status)
        self.assertEqual(3, frame.iloc[0].attempt_count)

    def test_changed_census_request_is_rejected_before_sending(self):
        path = self.source / 'requests/00000.json'
        path.write_text(path.read_text().replace('Codifica', 'Anota'))
        client = self.fake_client(('end_turn', json.dumps(self.raw)))
        with self.assertRaises(Exception):
            census.run(self.input, self.output, execute=True, workers=1, client=client)
        client.messages.stream.assert_not_called()

    def test_mid_stream_server_error_is_retried(self):
        error = census.anthropic.APIStatusError(
            'Internal server error', response=MagicMock(status_code=200, headers={}),
            body={'type': 'error', 'error': {'type': 'api_error'}})
        client = self.fake_client(('end_turn', json.dumps(self.raw)))
        client.messages.stream.side_effect = [error, *client.messages.stream.side_effect]
        with patch('features.llm_annotations.anthropic_census.time.sleep'):
            frame = census.run(self.input, self.output, execute=True, workers=1, client=client)
        self.assertEqual('completed', frame.iloc[0].status)
        self.assertEqual(2, frame.iloc[0].attempt_count)

    def test_stream_errors_from_old_runner_can_be_released(self):
        path = self.output / 'results/00000.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({
            'sample_index': 0, 'unit_id': 'u1::p1', 'status': 'error', 'attempt_count': 1,
            'attempt_max_output_tokens': 65536,
            'validation_errors': ["API HTTP 200; detail={'type': 'error'}"]}))
        self.assertEqual([0], census.release_stream_errors(self.output, 4))
        self.assertTrue((self.output / 'stream_errors/00000.json').exists())
        client = self.fake_client(('end_turn', json.dumps(self.raw)))
        frame = census.run(self.input, self.output, execute=True, workers=1, client=client)
        self.assertEqual('completed', frame.iloc[0].status)
        self.assertEqual(2, frame.iloc[0].attempt_count)

    def test_unauthorized_run_never_creates_client(self):
        pipeline.API_POLICY_PATH.write_text(json.dumps({'allow_api_calls': False}))
        with patch('features.llm_annotations.anthropic_census.anthropic.Anthropic') as constructor:
            with self.assertRaises(Exception):
                census.run(self.input, self.output, execute=True, workers=1)
            constructor.assert_not_called()

    def test_pilot_spans_the_census(self):
        self.assertEqual([0, 180, 360], census.pilot_indices(3609, 20)[:3])
        self.assertEqual(20, len(census.pilot_indices(3609, 20)))


if __name__ == '__main__':
    unittest.main()
