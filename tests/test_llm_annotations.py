from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import jsonschema
import pandas as pd

from features.llm_annotations.pipeline import (
    allocate_quotas, canonical, model_input, output_schema, prepare_run,
    run_annotations, validate_output,
)
from features.llm_annotations.review import AnnotationReviewService
from features.manual_validation.service import ValidationError, sha256_text
from features.political_alignment import PartyAlignment


class LLMPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        policy_patch = patch('features.llm_annotations.pipeline.API_POLICY_PATH', self.root / 'api_policy.json')
        policy_patch.start()
        self.addCleanup(policy_patch.stop)
        self.book = {'version': 'test', 'concepts': [
            {'id': 'solidaridad', 'label': 'Solidaridad', 'definition': 'Compartir riesgos.',
             'include': ['Distribución solidaria.'], 'exclude': [], 'orientation_anchor': 'Compartir riesgos.'}]}
        self.schema = output_schema(self.book)
        self.party_alignment = PartyAlignment(left=("Partido A",), right=("Partido B",))
        self.record = dict(unit_id='u1::p1', utterance_id='u1', content='🧭 Sí. La solidaridad es necesaria. Sí.',
                           law_number='21419', document_uri='doc1', date='2026-01-01',
                           constitutional_stage='primer', title='Sesión', paragraph_start=1,
                           paragraph_end=1, paragraph_count=1, n_words=7,
                           previous_context={'content': 'Debemos compartir riesgos.', 'same_utterance': False},
                           next_context=None, source_segments=[])
        self.raw = {'decision': 'statements', 'annotations': [{
            'evidence_text': 'Sí.', 'evidence_occurrence': 2, 'concept_status': 'in_codebook',
            'concept_id': 'solidaridad', 'proposed_concept': '', 'stance': 'support', 'confidence': 'high',
            'justification': {'criterion_reference': 'include:1', 'coding': 'Afirma solidaridad.',
                'stance': 'La acepta.', 'alternatives': [], 'context_evidence': [], 'uncertainty': ''}}],
            'decision_justification': 'Expresa un fundamento.', 'quality_flags': [],
            'needs_human_review': False, 'limitations': '', 'decision_confidence': 'high'}

    def tearDown(self):
        self.tmp.cleanup()

    def make_run(self):
        prompt = self.root / 'prompt.md'; prompt.write_text('Codifica con evidencia exacta.')
        service = SimpleNamespace(codebook=self.book, codebook_sha256=sha256_text(canonical(self.book)),
                                  sources=[{'law_number': '21419', 'sha256': 'fixture'}],
                                  party_alignment=self.party_alignment)
        return prepare_run(service, [self.record], {'selected_interventions': 1}, prompt,
                           self.root / 'runs', 'gpt-5.6-luna', 'max')

    def fake_client(self, raw=None, status='completed'):
        response = MagicMock()
        response.status = status
        response.output_text = json.dumps(self.raw if raw is None else raw)
        response.model_dump.return_value = {'status': status, 'model': 'gpt-5.6-luna', 'usage': {}}
        client = MagicMock(); client.responses.create.return_value = response
        return client

    def test_quota_total_representation_and_caps(self):
        counts = pd.Series([165,55,42,80,31,258,62,209,194])
        quotas = allocate_quotas(counts, .1)
        self.assertEqual(110, quotas.sum())
        self.assertTrue(quotas.ge(1).all())
        self.assertTrue(quotas.le(counts).all())
        self.assertEqual(quotas.tolist(), allocate_quotas(counts, .1).tolist())
        self.assertEqual([1,1,8], allocate_quotas(pd.Series([1,1,98]), .1).tolist())
        with self.assertRaises(ValueError): allocate_quotas(pd.Series([1,1,1]), .1)

    def test_exact_unicode_offsets_and_repeated_evidence(self):
        result = validate_output(self.raw, self.record, self.book, self.schema)
        span = result['annotations'][0]['span']
        self.assertEqual(self.record['content'].rindex('Sí.'), span['start_char'])
        self.assertEqual(span['text'], self.record['content'][span['start_char']:span['end_char']])

    def test_invalid_evidence_context_rule_code_and_decision(self):
        cases = []
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['evidence_text'] = 'Una cita inventada'; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['justification']['context_evidence'] = [{'source':'next_context','text':'inexistente'}]; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['justification']['criterion_reference'] = 'include:9'; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['concept_id'] = 'otro'; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['decision'] = 'no_statements'; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'] *= 2; cases.append(raw)
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises((ValidationError, jsonschema.ValidationError)):
                    validate_output(raw, self.record, self.book, self.schema)

    def test_missing_concept_requires_review(self):
        raw = copy.deepcopy(self.raw)
        raw['annotations'][0].update(concept_status='review', concept_id=None, proposed_concept='Nueva regla')
        raw['annotations'][0]['justification']['criterion_reference'] = 'new_concept'
        with self.assertRaises(ValidationError): validate_output(raw, self.record, self.book, self.schema)
        raw['needs_human_review'] = True
        raw['limitations'] = 'El libro no contiene esta justificación normativa.'
        self.assertEqual('review', validate_output(raw, self.record, self.book, self.schema)['annotations'][0]['concept_status'])

    def test_cross_field_validation_matches_prompt_contract(self):
        cases = []
        raw = copy.deepcopy(self.raw); raw['quality_flags'] = ['truncated']; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['quality_flags'] = ['other']; raw['needs_human_review'] = True; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['proposed_concept'] = 'No corresponde'; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['justification']['alternatives'] = [
            {'concept_id': 'solidaridad', 'reason': 'Otra lectura'}]; cases.append(raw)
        raw = copy.deepcopy(self.raw); raw['annotations'][0]['justification']['alternatives'] = [
            {'concept_id': 'solidaridad', 'reason': ''}]; cases.append(raw)
        for raw in cases:
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                validate_output(raw, self.record, self.book, self.schema)
        raw = copy.deepcopy(self.raw); raw['quality_flags'] = ['vote', 'vote']
        with self.assertRaises(jsonschema.ValidationError):
            validate_output(raw, self.record, self.book, self.schema)

    def test_input_excludes_identity_fields_and_preserves_context(self):
        payload = model_input({**self.record, 'speaker_name': 'NO ENVIAR', 'party': 'NO ENVIAR'})
        self.assertNotIn('NO ENVIAR', canonical(payload))
        self.assertEqual(self.record['content'], payload['target_text'])
        self.assertFalse(payload['previous_context']['same_utterance'])
        self.assertIsNone(payload['next_context'])

    def test_read_only_render_and_resume_never_resend(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI') as constructor:
            results = run_annotations(directory)
            constructor.assert_not_called()
            self.assertEqual('pending', results.iloc[0].status)
        client = self.fake_client()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=client):
            results = run_annotations(directory, execute=True)
            before = (directory / 'results/00000.json').read_bytes()
            run_annotations(directory, execute=True)
            self.assertEqual(1, client.responses.create.call_count)
            self.assertEqual(before, (directory / 'results/00000.json').read_bytes())
        self.assertEqual('completed', results.iloc[0].status)
        self.assertEqual(1, len(pd.read_parquet(directory / 'annotations.parquet')))

    def test_confidence_validation_and_normalization(self):
        for level in ('medium', 'low'):
            raw = copy.deepcopy(self.raw)
            raw['annotations'][0]['confidence'] = level
            raw['annotations'][0]['justification']['uncertainty'] = 'La orientación es dudosa.'
            with self.assertRaises(ValidationError):
                validate_output(raw, self.record, self.book, self.schema)
            raw['needs_human_review'] = True
            normalized = validate_output(raw, self.record, self.book, self.schema)
            self.assertEqual(level, normalized['annotations'][0]['confidence'])
        for level in (None, '', 0.8, 'alta'):
            raw = copy.deepcopy(self.raw)
            raw['annotations'][0]['confidence'] = level
            with self.assertRaises(jsonschema.ValidationError):
                validate_output(raw, self.record, self.book, self.schema)

    def test_no_statements_confidence(self):
        raw = {**self.raw, 'decision': 'no_statements', 'annotations': [],
               'decision_confidence': 'low', 'needs_human_review': True}
        with self.assertRaises(ValidationError):
            validate_output(raw, self.record, self.book, self.schema)
        raw['limitations'] = 'El objetivo está truncado.'
        self.assertEqual('low', validate_output(raw, self.record, self.book, self.schema)['decision_confidence'])
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client(raw)):
            frame = run_annotations(directory, execute=True)
        self.assertEqual('low', frame.iloc[0].decision_confidence)
        spans = pd.read_parquet(directory / 'annotations.parquet')
        self.assertTrue(spans.empty)
        self.assertIn('confidence', spans.columns)

    def test_confidence_roundtrip_and_legacy_missing_values(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client()):
            run_annotations(directory, execute=True)
        for filename, column in [('results', 'decision_confidence'), ('annotations', 'confidence')]:
            frame = pd.read_parquet(directory / f'{filename}.parquet')
            self.assertEqual('high', frame.iloc[0][column])
            frame.to_csv(directory / f'{filename}.csv', index=False)
            self.assertEqual('high', pd.read_csv(directory / f'{filename}.csv').iloc[0][column])
        legacy = copy.deepcopy(self.raw)
        del legacy['decision_confidence']
        del legacy['annotations'][0]['confidence']
        schema = copy.deepcopy(self.schema)
        for obj, key in [(schema, 'decision_confidence'),
                         (schema['properties']['annotations']['items'], 'confidence')]:
            del obj['properties'][key]
            obj['required'].remove(key)
        normalized = validate_output(legacy, self.record, self.book, schema)
        result_path = directory / 'results/00000.json'
        saved = json.loads(result_path.read_text())
        saved['normalized'] = normalized
        result_path.write_text(json.dumps(saved))
        frame = run_annotations(directory)
        self.assertTrue(pd.isna(frame.iloc[0].decision_confidence))
        self.assertTrue(pd.isna(pd.read_parquet(directory / 'annotations.parquet').iloc[0].confidence))

    def test_user_stop_policy_blocks_even_when_execute_is_true(self):
        directory = self.make_run()
        (self.root / 'api_policy.json').write_text('{"allow_api_calls": false}')
        with patch('features.llm_annotations.pipeline.OpenAI') as constructor:
            with self.assertRaises(ValidationError):
                run_annotations(directory, execute=True)
            constructor.assert_not_called()
            self.assertEqual('pending', run_annotations(directory).iloc[0].status)

    def test_invalid_and_incomplete_are_not_no_statements(self):
        for status, raw, expected in [('incomplete', self.raw, 'incomplete'),
                                     ('completed', {'bad': 'output'}, 'invalid_output')]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as name:
                self.root = Path(name); directory = self.make_run()
                with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client(raw, status)):
                    frame = run_annotations(directory, execute=True)
                self.assertEqual(expected, frame.iloc[0].status)
                self.assertIsNone(frame.iloc[0].decision)
                self.assertEqual(0, frame.iloc[0].n_annotations)

    def test_prompt_versions_keep_previous_run(self):
        first = self.make_run()
        prompt = self.root / 'prompt.md'; prompt.write_text('Otra versión.')
        service = SimpleNamespace(codebook=self.book, codebook_sha256=sha256_text(canonical(self.book)),
                                  sources=[{'law_number': '21419', 'sha256': 'fixture'}],
                                  party_alignment=self.party_alignment)
        second = prepare_run(service, [self.record], {'selected_interventions': 1}, prompt,
                             self.root / 'runs', 'gpt-5.6-luna', 'max')
        self.assertNotEqual(first, second)
        self.assertEqual('Codifica con evidencia exacta.', (first/'prompt.md').read_text())

    def test_active_prompt_documents_current_schema(self):
        root = Path(__file__).resolve().parents[1]
        report = (root / 'annotations.qmd').read_text(encoding='utf-8')
        prompt = (root / 'prompts/annotations_pilot_v1_confidence.md').read_text(
            encoding='utf-8'
        )
        self.assertIn('"prompts/annotations_pilot_v1_confidence.md"', report)
        for field in ('decision_confidence', 'confidence', 'needs_human_review',
                      'proposed_concept', 'limitations'):
            self.assertIn(f'`{field}`', prompt)
        self.assertIn('Usa únicamente estas flags, sin duplicarlas', prompt)

    def test_reviews_preserve_response_and_reject_stale_or_foreign_spans(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client()):
            run_annotations(directory, execute=True)
        reviewer = AnnotationReviewService(
            self.root/'runs', self.root/'reviews',
            {'u1::p1': {'chamber': 'Senado', 'alignment': 'centro',
                        'gender': 'F', 'actor_type': 'Parlamentario'}},
            {'21419': 'fixture'},
        )
        original = (directory/'results/00000.json').read_bytes()
        item = reviewer.open_item(directory.name, 0)
        payload = {'result_sha256': item['result_sha256'], 'verdict': 'accepted', 'revision': 0,
                   'annotations': [{'annotation_id':'llm_000', 'verdict':'accepted', 'note':''}]}
        review = reviewer.save_review(directory.name, 0, payload)['review']
        self.assertEqual(1, review['revision'])
        self.assertEqual(original, (directory/'results/00000.json').read_bytes())
        with self.assertRaises(ValidationError): reviewer.save_review(directory.name, 0, payload)
        payload['revision'] = 1; payload['annotations'][0]['annotation_id'] = 'ajena'
        with self.assertRaises(ValidationError): reviewer.save_review(directory.name, 0, payload)
        with self.assertRaises(ValidationError): reviewer.open_item('../escape', 0)
        with self.assertRaises(ValidationError): reviewer.open_item(directory.name, -1)
        listed = reviewer.list_items(directory.name)['items'][0]
        self.assertEqual('accepted', listed['review_verdict'])
        self.assertEqual('Senado', listed['strata']['chamber'])
        self.assertEqual('centro', listed['strata']['alignment'])
        self.assertNotIn('party', listed['strata'])
        self.assertTrue(listed['strata_source_matches_run'])

    def test_reviews_can_judge_each_annotation_without_global_verdict(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client()):
            run_annotations(directory, execute=True)
        reviewer = AnnotationReviewService(self.root/'runs', self.root/'reviews')
        item = reviewer.open_item(directory.name, 0)
        payload = {'result_sha256': item['result_sha256'], 'verdict': None, 'revision': 0,
                   'issues': [], 'note': '',
                   'annotations': [{'annotation_id': 'llm_000', 'verdict': 'needs_changes',
                                    'note': 'Ajustar el código propuesto.'}]}
        review = reviewer.save_review(directory.name, 0, payload)['review']
        self.assertIsNone(review['verdict'])
        listed = reviewer.list_items(directory.name)['items'][0]
        self.assertTrue(listed['review_complete'])
        self.assertEqual('annotations_reviewed', listed['review_verdict'])

    def test_diagnostic_review_records_omission_when_model_found_other_codes(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client()):
            run_annotations(directory, execute=True)
        reviewer = AnnotationReviewService(self.root/'runs', self.root/'reviews')
        item = reviewer.open_item(directory.name, 0)
        payload = {
            'result_sha256': item['result_sha256'],
            'verdict': None,
            'revision': 0,
            'issues': ['omission'],
            'note': 'Falta una declaración de necesidad material.',
            'annotations': [{
                'annotation_id': 'llm_000', 'verdict': 'accepted', 'note': ''
            }],
        }
        review = reviewer.save_review(directory.name, 0, payload)['review']
        self.assertEqual(['omission'], review['issues'])
        self.assertEqual(payload['note'], review['note'])
        self.assertIsNone(review['verdict'])

    def test_new_run_defaults_and_budget_validation(self):
        self.make_run()
        service = SimpleNamespace(
            codebook=self.book, codebook_sha256='fixture', sources=[],
            party_alignment=self.party_alignment,
        )
        directory = prepare_run(service, [self.record], {}, self.root / 'prompt.md', self.root / 'defaults')
        manifest = json.loads((directory / 'manifest.json').read_text())
        self.assertEqual(
            manifest['spec']['party_alignment'], service.party_alignment.snapshot()
        )
        request = json.loads((directory / 'requests/00000.json').read_text())['body']
        self.assertEqual('low', request['reasoning']['effort'])
        self.assertEqual(32768, request['max_output_tokens'])
        for budget in (0, -1, True, 128001):
            with self.assertRaises(ValueError):
                prepare_run(service, [self.record], {}, self.root / 'prompt.md', self.root,
                            max_output_tokens=budget)
        for limit in (-1, True, 1.5):
            with self.assertRaises(ValueError):
                run_annotations(directory, execute=True, limit=limit)

    def test_token_exhaustion_is_persisted_without_retry(self):
        directory = self.make_run()
        client = self.fake_client(status='incomplete')
        client.responses.create.return_value.output_text = ''
        client.responses.create.return_value.model_dump.return_value.update(
            incomplete_details={'reason': 'max_output_tokens'},
            usage={'output_tokens': 32768, 'output_tokens_details': {'reasoning_tokens': 32768}})
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=client) as constructor:
            frame = run_annotations(directory, execute=True)
            run_annotations(directory, execute=True)
        self.assertEqual(0, constructor.call_args.kwargs['max_retries'])
        client.models.retrieve.assert_not_called()
        self.assertEqual(1, client.responses.create.call_count)
        self.assertEqual('max_output_tokens', frame.iloc[0].incomplete_reason)
        self.assertEqual(32768, frame.iloc[0].reasoning_tokens)
        self.assertIn('max_output_tokens', frame.iloc[0].validation_errors)
        self.assertIsNone(frame.iloc[0].decision)
        client.close.assert_called_once()

    def test_interrupted_attempt_is_reserved_before_send(self):
        directory = self.make_run()
        client = self.fake_client()
        def interrupt(**kwargs):
            saved = json.loads((directory / 'results/00000.json').read_text())
            self.assertEqual('started', saved['status'])
            raise KeyboardInterrupt()
        client.responses.create.side_effect = interrupt
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=client):
            with self.assertRaises(KeyboardInterrupt):
                run_annotations(directory, execute=True)
            frame = run_annotations(directory, execute=True)
        self.assertEqual('started', frame.iloc[0].status)
        self.assertEqual(1, client.responses.create.call_count)
        client.close.assert_called_once()

    def test_scoped_authorization_checks_run_and_model(self):
        directory = self.make_run()
        grant = {'model': 'gpt-5.6-luna', 'reasoning_effort': 'max',
                 'run_dir': str(directory.resolve()), 'max_calls': 1}
        policy = {'allow_api_calls': False, 'authorized_runs': {directory.name: grant}}
        policy_path = self.root / 'api_policy.json'
        for key, value in [('model', 'other'), ('reasoning_effort', 'low'),
                           ('max_calls', 0), ('run_dir', '/tmp/other')]:
            invalid = copy.deepcopy(policy)
            invalid['authorized_runs'][directory.name][key] = value
            policy_path.write_text(json.dumps(invalid))
            with patch('features.llm_annotations.pipeline.OpenAI') as constructor:
                with self.assertRaises(ValidationError):
                    run_annotations(directory, execute=True)
                constructor.assert_not_called()
        policy_path.write_text(json.dumps(policy))
        client = self.fake_client()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=client):
            run_annotations(directory, execute=True)
            run_annotations(directory, execute=True)
        self.assertEqual(1, client.responses.create.call_count)

    def test_concurrent_run_is_rejected(self):
        import fcntl
        directory = self.make_run()
        with (directory / '.execution.lock').open('a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with patch('features.llm_annotations.pipeline.OpenAI') as constructor:
                with self.assertRaises(ValidationError):
                    run_annotations(directory, execute=True)
                constructor.assert_not_called()

    def test_api_failure_status_is_not_token_exhaustion(self):
        directory = self.make_run()
        client = self.fake_client(status='failed')
        client.responses.create.return_value.model_dump.return_value['error'] = {'code': 'server_error'}
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=client):
            frame = run_annotations(directory, execute=True)
        self.assertEqual('error', frame.iloc[0].status)
        self.assertEqual('server_error', frame.iloc[0].api_error_code)
        self.assertIsNone(frame.iloc[0].incomplete_reason)


if __name__ == '__main__':
    unittest.main()
