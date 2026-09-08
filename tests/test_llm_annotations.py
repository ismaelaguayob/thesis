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


class LLMPilotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.book = {'version': 'test', 'concepts': [
            {'id': 'solidaridad', 'label': 'Solidaridad', 'definition': 'Compartir riesgos.',
             'include': ['Distribución solidaria.'], 'exclude': [], 'orientation_anchor': 'Compartir riesgos.'}]}
        self.schema = output_schema(self.book)
        self.record = dict(unit_id='u1::p1', utterance_id='u1', content='🧭 Sí. La solidaridad es necesaria. Sí.',
                           law_number='21419', document_uri='doc1', date='2026-01-01',
                           constitutional_stage='primer', title='Sesión', paragraph_start=1,
                           paragraph_end=1, paragraph_count=1, n_words=7,
                           previous_context={'content': 'Debemos compartir riesgos.', 'same_utterance': False},
                           next_context=None, source_segments=[])
        self.raw = {'decision': 'statements', 'annotations': [{
            'evidence_text': 'Sí.', 'evidence_occurrence': 2, 'concept_status': 'in_codebook',
            'concept_id': 'solidaridad', 'proposed_concept': '', 'stance': 'support',
            'justification': {'criterion_reference': 'include:1', 'coding': 'Afirma solidaridad.',
                'stance': 'La acepta.', 'alternatives': [], 'context_evidence': [], 'uncertainty': ''}}],
            'decision_justification': 'Expresa un fundamento.', 'quality_flags': [],
            'needs_human_review': False, 'limitations': ''}

    def tearDown(self):
        self.tmp.cleanup()

    def make_run(self):
        prompt = self.root / 'prompt.md'; prompt.write_text('Codifica con evidencia exacta.')
        service = SimpleNamespace(codebook=self.book, codebook_sha256=sha256_text(canonical(self.book)),
                                  sources=[{'law_number': '21419', 'sha256': 'fixture'}])
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
        self.assertEqual('review', validate_output(raw, self.record, self.book, self.schema)['annotations'][0]['concept_status'])

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
                                  sources=[{'law_number': '21419', 'sha256': 'fixture'}])
        second = prepare_run(service, [self.record], {'selected_interventions': 1}, prompt,
                             self.root / 'runs', 'gpt-5.6-luna', 'max')
        self.assertNotEqual(first, second)
        self.assertEqual('Codifica con evidencia exacta.', (first/'prompt.md').read_text())

    def test_reviews_preserve_response_and_reject_stale_or_foreign_spans(self):
        directory = self.make_run()
        with patch('features.llm_annotations.pipeline.OpenAI', return_value=self.fake_client()):
            run_annotations(directory, execute=True)
        reviewer = AnnotationReviewService(self.root/'runs', self.root/'reviews')
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
        self.assertEqual('accepted', reviewer.list_items(directory.name)['items'][0]['review_verdict'])


if __name__ == '__main__':
    unittest.main()
