from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from features.llm_annotations.stance_adjudication import StanceAdjudicationService, build_cases
from features.manual_validation.service import ValidationError


def annotations(rows):
    columns = ['unit_id', 'concept_id', 'stance', 'start_char', 'end_char',
               'evidence_text', 'justification', 'confidence']
    return pd.DataFrame([
        {'start_char': 0, 'end_char': 4, 'evidence_text': 'Texto', 'justification': 'j',
         'confidence': 'high', **row}
        for row in rows
    ], columns=columns)


PRIMARY = annotations([
    {'unit_id': 'u1', 'concept_id': 'ineficiencia_estado', 'stance': 'oppose'},   # disagreement
    {'unit_id': 'u2', 'concept_id': 'ineficiencia_estado', 'stance': 'support'},  # agreement
    {'unit_id': 'u3', 'concept_id': 'ineficiencia_estado', 'stance': 'oppose'},   # primary only
    {'unit_id': 'u4', 'concept_id': 'necesidad_material', 'stance': 'support'},   # agreement
    {'unit_id': 'u5', 'concept_id': 'necesidad_material', 'stance': 'oppose'},    # primary only, unflagged
    {'unit_id': 'u1', 'concept_id': 'identidad', 'stance': 'oppose'},             # excluded concept
])
SECONDARY = annotations([
    {'unit_id': 'u1', 'concept_id': 'ineficiencia_estado', 'stance': 'support'},
    {'unit_id': 'u2', 'concept_id': 'ineficiencia_estado', 'stance': 'support'},
    {'unit_id': 'u4', 'concept_id': 'necesidad_material', 'stance': 'support'},
    {'unit_id': 'u1', 'concept_id': 'identidad', 'stance': 'support'},
])


class StanceAdjudicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.primary = root / 'runs' / 'primary'
        self.secondary = root / 'runs' / 'secondary'
        self.inputs = root / 'inputs'
        for path in (self.primary, self.secondary, self.inputs):
            path.mkdir(parents=True)
        PRIMARY.to_parquet(self.primary / 'annotations.parquet')
        SECONDARY.to_parquet(self.secondary / 'annotations.parquet')
        pd.DataFrame({
            'unit_id': [f'u{i}' for i in range(1, 6)], 'law_number': ['21735'] * 5,
            'document_uri': ['http://x/doc/1'] * 5, 'content': ['Texto del bloque'] * 5,
            'previous_context': [json.dumps({'content': 'antes'})] * 5,
            'next_context': [None] * 5,
        }).to_parquet(self.inputs / 'sample.parquet')
        concepts = [{'id': c, 'label': c.title(), 'definition': 'd', 'orientation_anchor': 'a',
                     'include': [], 'exclude': []}
                    for c in ('ineficiencia_estado', 'necesidad_material', 'identidad')]
        (self.inputs / 'codebook.json').write_text(json.dumps({'concepts': concepts}))
        self.service = StanceAdjudicationService(self.primary, self.secondary, self.inputs,
                                                 root / 'adjudication')

    def tearDown(self):
        self.tmp.cleanup()

    def test_rule_selects_disagreements_and_unmatched_rejections_of_flagged_concepts(self):
        cases, rates = build_cases(PRIMARY, SECONDARY)
        selected = {(c['unit_id'], c['concept_id'], c['rule']) for c in cases}
        self.assertEqual(selected, {
            ('u1', 'ineficiencia_estado', 'stance_disagreement'),
            ('u3', 'ineficiencia_estado', 'primary_rejection_unmatched'),
        })
        self.assertAlmostEqual(rates['ineficiencia_estado']['rate'], 0.5)
        self.assertNotIn('identidad', rates)

    def test_queue_is_frozen_and_hides_model_identity(self):
        queue = self.service.queue()
        self.assertEqual(len(queue['cases']), 2)
        again = StanceAdjudicationService(self.primary, self.secondary, self.inputs,
                                          self.service.root).queue()
        self.assertEqual(queue['created_at_utc'], again['created_at_utc'])
        item = self.service.open_item(0)
        payload = json.dumps(item)
        self.assertNotIn('primary', payload)
        self.assertNotIn('secondary', payload)
        self.assertEqual(sorted(c['label'] for c in item['codings']), ['A', 'B'])
        self.assertEqual(item['previous_text'], 'antes')

    def test_decisions_are_validated_versioned_and_exported(self):
        with self.assertRaises(ValidationError):
            self.service.save_decision(0, {'decision': 'maybe', 'revision': 0})
        with self.assertRaises(ValidationError):
            self.service.save_decision(0, {'decision': 'concept_absent', 'note': '', 'revision': 0})
        saved = self.service.save_decision(0, {'decision': 'support', 'revision': 0})['decision']
        self.assertEqual(saved['revision'], 1)
        with self.assertRaises(ValidationError):
            self.service.save_decision(0, {'decision': 'oppose', 'revision': 0})
        self.service.save_decision(0, {'decision': 'oppose', 'revision': 1})
        table = self.service.export()
        self.assertEqual(table['decision'].tolist(), ['oppose'])
        self.assertEqual(self.service.list_items()['items'][0]['decision'], 'oppose')


if __name__ == '__main__':
    unittest.main()
