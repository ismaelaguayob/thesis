"""Human adjudication of stance disagreements between two complete LLM censuses.

The queue is built with a fixed rule and frozen on first use, so the cases do
not depend on which results look surprising. Original annotations are never
modified: decisions are stored separately and applied by the analysis code.

Rule (docs/decisiones-validacion.md, section 5):

1. Every block × concept that both runs annotated with different stance sets.
2. For concepts whose stance-disagreement rate between runs exceeds
   ``threshold``, every rejection by the primary run on a block × concept that
   the secondary run did not annotate.

Concepts excluded from the analysis by the inclusion rule are left out.

Second round (docs/decisiones-validacion.md, section 5, second round):

3. For the same flagged concepts, every block × concept in which both runs
   agree on a rejection (alone or together with support). Shared orientation
   errors cannot appear as disagreements, so they are reviewed here. The
   reviewer sees the cited passages but not the stance or the justification
   the models gave, so the agreement does not anchor the decision.

Each round is a separate frozen queue; the first round keeps its identifier.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import threading
from pathlib import Path

import pandas as pd

from features.manual_validation.service import ValidationError, atomic_write_json, sha256_file

SCHEMA_VERSION = 'stance-adjudication-1.0.0'
DECISIONS = {'support', 'oppose', 'both', 'concept_absent', 'unresolved'}
NOTE_REQUIRED = {'concept_absent', 'unresolved'}
RULE_BOTH = 'stance_disagreement'
RULE_PRIMARY_ONLY = 'primary_rejection_unmatched'
RULE_AGREED_REJECTION = 'agreed_rejection_flagged'
ROUND_RULES = {
    1: 'Rule (1) and (2): stance disagreements and unmatched primary rejections.',
    2: 'Rule (3): rejections both runs agree on, in the concepts flagged in round 1.',
}
DEFAULT_THRESHOLD = 0.05
DEFAULT_EXCLUDED = ('identidad', 'control_responsabilidad_individual')


def _stance_set(stances) -> str:
    """Canonical label of the stances a coder gave a block × concept."""
    values = set(stances)
    if values == {'support', 'oppose'}:
        return 'both'
    return values.pop()


def _context_text(raw) -> str:
    if not isinstance(raw, str) or not raw:
        return ''
    try:
        return json.loads(raw).get('content', '') or ''
    except json.JSONDecodeError:
        return ''


def build_cases(primary: pd.DataFrame, secondary: pd.DataFrame, *,
                threshold: float = DEFAULT_THRESHOLD,
                excluded: tuple[str, ...] = DEFAULT_EXCLUDED,
                round_number: int = 1) -> tuple[list[dict], dict[str, dict]]:
    """Return the adjudication cases and the per-concept disagreement rates."""
    key = ['unit_id', 'concept_id']
    primary = primary.loc[~primary['concept_id'].isin(excluded)]
    secondary = secondary.loc[~secondary['concept_id'].isin(excluded)]
    p_sets = primary.groupby(key)['stance'].agg(_stance_set).rename('primary')
    s_sets = secondary.groupby(key)['stance'].agg(_stance_set).rename('secondary')
    both = pd.concat([p_sets, s_sets], axis=1, join='inner').reset_index()
    both['disagree'] = both['primary'] != both['secondary']
    rates = {
        concept: {'pairs': int(len(group)), 'disagreements': int(group['disagree'].sum()),
                  'rate': float(group['disagree'].mean())}
        for concept, group in both.groupby('concept_id')
    }
    flagged = {concept for concept, rate in rates.items() if rate['rate'] > threshold}
    if round_number == 2:
        agreed = both.loc[~both['disagree'] & both['concept_id'].isin(flagged)
                          & both['primary'].isin(['oppose', 'both'])]
        cases = [
            {'unit_id': row.unit_id, 'concept_id': row.concept_id, 'rule': RULE_AGREED_REJECTION,
             'primary_stances': row.primary, 'secondary_stances': row.secondary}
            for row in agreed.itertuples()
        ]
        return cases, rates
    if round_number != 1:
        raise ValueError(f'Unknown adjudication round: {round_number}')
    cases = [
        {'unit_id': row.unit_id, 'concept_id': row.concept_id, 'rule': RULE_BOTH,
         'primary_stances': row.primary, 'secondary_stances': row.secondary}
        for row in both.loc[both['disagree']].itertuples()
    ]
    p_only = p_sets.reset_index().merge(s_sets.reset_index(), on=key, how='left')
    p_only = p_only.loc[p_only['secondary'].isna()
                        & p_only['concept_id'].isin(flagged)
                        & p_only['primary'].isin(['oppose', 'both'])]
    cases += [
        {'unit_id': row.unit_id, 'concept_id': row.concept_id, 'rule': RULE_PRIMARY_ONLY,
         'primary_stances': row.primary, 'secondary_stances': None}
        for row in p_only.itertuples()
    ]
    return cases, rates


class StanceAdjudicationService:
    def __init__(self, primary_run_dir: Path, secondary_run_dir: Path, input_dir: Path,
                 adjudication_dir: Path, threshold: float = DEFAULT_THRESHOLD,
                 excluded: tuple[str, ...] = DEFAULT_EXCLUDED, round_number: int = 1):
        if round_number not in ROUND_RULES:
            raise ValueError(f'Unknown adjudication round: {round_number}')
        self.primary_run_dir = primary_run_dir.resolve()
        self.secondary_run_dir = secondary_run_dir.resolve()
        self.input_dir = input_dir.resolve()
        self.root = adjudication_dir.resolve()
        self.threshold = threshold
        self.excluded = tuple(excluded)
        self.round_number = round_number
        self.lock = threading.RLock()
        self._queue = None
        self._records = None
        self._annotations = {}

    # ----- frozen queue ---------------------------------------------------
    def _sources(self) -> dict:
        return {
            'primary_run': self.primary_run_dir.name,
            'secondary_run': self.secondary_run_dir.name,
            'primary_annotations_sha256': sha256_file(self.primary_run_dir / 'annotations.parquet'),
            'secondary_annotations_sha256': sha256_file(self.secondary_run_dir / 'annotations.parquet'),
            'sample_sha256': sha256_file(self.input_dir / 'sample.parquet'),
            'codebook_sha256': sha256_file(self.input_dir / 'codebook.json'),
        }

    @property
    def queue_id(self) -> str:
        fields = {**self._sources(), 'threshold': self.threshold,
                  'excluded': sorted(self.excluded), 'schema': SCHEMA_VERSION}
        # The first round predates rounds; adding the key would change its identifier.
        if self.round_number != 1:
            fields['round'] = self.round_number
        payload = json.dumps(fields, sort_keys=True)
        return 'stance_' + hashlib.sha256(payload.encode()).hexdigest()[:12]

    @property
    def queue_dir(self) -> Path:
        return self.root / self.queue_id

    def queue(self) -> dict:
        with self.lock:
            if self._queue is not None:
                return self._queue
            path = self.queue_dir / 'queue.json'
            if path.exists():
                self._queue = json.loads(path.read_text())
                return self._queue
            primary = pd.read_parquet(self.primary_run_dir / 'annotations.parquet')
            secondary = pd.read_parquet(self.secondary_run_dir / 'annotations.parquet')
            cases, rates = build_cases(primary, secondary, threshold=self.threshold,
                                       excluded=self.excluded, round_number=self.round_number)
            order = {unit: i for i, unit in enumerate(self.records().index)}
            cases.sort(key=lambda c: (order.get(c['unit_id'], len(order)), c['concept_id']))
            for index, case in enumerate(cases):
                case['case_index'] = index
                # Which run is shown as "A" is fixed per case and hidden from the UI,
                # so the reviewer does not know which model is the primary one.
                digest = hashlib.sha256(f"{case['unit_id']}|{case['concept_id']}".encode()).digest()
                case['primary_label'] = 'A' if digest[0] % 2 == 0 else 'B'
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            self._queue = {
                'schema_version': SCHEMA_VERSION, 'queue_id': self.queue_id,
                'created_at_utc': now, 'sources': self._sources(),
                'round': self.round_number,
                'rule': {'threshold': self.threshold, 'excluded_concepts': sorted(self.excluded),
                         'description': ROUND_RULES[self.round_number]},
                'concept_disagreement': rates,
                'flagged_concepts': sorted(c for c, r in rates.items() if r['rate'] > self.threshold),
                'cases': cases,
            }
            atomic_write_json(path, self._queue)
            return self._queue

    def _check_sources(self) -> None:
        if self.queue()['sources'] != self._sources():
            raise ValidationError('Las anotaciones o la muestra cambiaron desde que se creó la cola')

    def records(self) -> pd.DataFrame:
        if self._records is None:
            sample = pd.read_parquet(self.input_dir / 'sample.parquet')
            self._records = sample.set_index('unit_id', drop=False)
        return self._records

    def _codebook(self) -> dict:
        return json.loads((self.input_dir / 'codebook.json').read_text())

    # ----- items ----------------------------------------------------------
    def _decision_path(self, index: int) -> Path:
        return self.queue_dir / 'decisions' / f'{index:05d}.json'

    def _case(self, index: int) -> dict:
        cases = self.queue()['cases']
        if index < 0 or index >= len(cases):
            raise ValidationError('Índice de caso fuera de rango')
        return cases[index]

    def list_items(self) -> dict:
        queue = self.queue()
        labels = {c['id']: c['label'] for c in self._codebook()['concepts']}
        records = self.records()
        items = []
        for case in queue['cases']:
            path = self._decision_path(case['case_index'])
            decision = json.loads(path.read_text())['decision'] if path.exists() else None
            items.append({'case_index': case['case_index'],
                          'law_number': str(records.loc[case['unit_id'], 'law_number']),
                          'concept_id': case['concept_id'],
                          'concept_label': labels.get(case['concept_id'], case['concept_id']),
                          'rule': case['rule'], 'decision': decision})
        return {'queue_id': queue['queue_id'], 'round': queue.get('round', 1), 'rule': queue['rule'],
                'flagged_concepts': queue['flagged_concepts'], 'items': items}

    def _codings(self, case: dict) -> list[dict]:
        """Annotations of each run for the case concept, labelled A/B without run names."""
        codings = []
        for run_dir, is_primary in ((self.primary_run_dir, True), (self.secondary_run_dir, False)):
            if run_dir not in self._annotations:
                self._annotations[run_dir] = pd.read_parquet(run_dir / 'annotations.parquet')
            frame = self._annotations[run_dir]
            frame = frame.loc[(frame['unit_id'] == case['unit_id'])
                              & (frame['concept_id'] == case['concept_id'])]
            label = case['primary_label'] if is_primary else ('B' if case['primary_label'] == 'A' else 'A')
            codings.append({
                'label': label,
                'annotations': [
                    # In round 2 both runs agree on a rejection: hide what would anchor it.
                    {'start_char': int(r.start_char), 'end_char': int(r.end_char),
                     'text': r.evidence_text,
                     'stance': r.stance if self.round_number == 1 else None,
                     'justification': r.justification if self.round_number == 1 else None,
                     'confidence': r.confidence}
                    for r in frame.itertuples()
                ],
            })
        return sorted(codings, key=lambda c: c['label'])

    def open_item(self, index: int) -> dict:
        self._check_sources()
        case = self._case(index)
        record = self.records().loc[case['unit_id']]
        concept = next(c for c in self._codebook()['concepts'] if c['id'] == case['concept_id'])
        path = self._decision_path(index)
        return {
            'case_index': index, 'n_cases': len(self.queue()['cases']),
            'law_number': str(record['law_number']),
            'session': str(record['document_uri']).rsplit('/', 1)[-1],
            'target_text': record['content'],
            'previous_text': _context_text(record.get('previous_context')),
            'next_text': _context_text(record.get('next_context')),
            'concept': {k: concept.get(k) for k in
                        ('id', 'label', 'definition', 'orientation_anchor', 'include', 'exclude')},
            'codings': self._codings(case),
            'decision': json.loads(path.read_text()) if path.exists() else None,
        }

    def save_decision(self, index: int, payload: dict) -> dict:
        with self.lock:
            self._check_sources()
            case = self._case(index)
            decision = payload.get('decision')
            if decision not in DECISIONS:
                raise ValidationError('Decisión de postura inválida')
            note = payload.get('note', '')
            reviewer = payload.get('reviewer', '')
            if not isinstance(note, str) or len(note) > 3000:
                raise ValidationError('Comentario inválido')
            if not isinstance(reviewer, str) or len(reviewer) > 120:
                raise ValidationError('Identificador del revisor inválido')
            if decision in NOTE_REQUIRED and not note.strip():
                raise ValidationError('Explica por qué el concepto no corresponde o no puede resolverse')
            path = self._decision_path(index)
            old = json.loads(path.read_text()) if path.exists() else {}
            if payload.get('revision', 0) != old.get('revision', 0):
                raise ValidationError('Otra decisión fue guardada; vuelve a abrir el caso')
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            record = {
                'schema_version': SCHEMA_VERSION, 'queue_id': self.queue_id,
                'case_index': index, 'unit_id': case['unit_id'], 'concept_id': case['concept_id'],
                'rule': case['rule'], 'primary_stances': case['primary_stances'],
                'secondary_stances': case['secondary_stances'],
                'decision': decision, 'note': note.strip(), 'reviewer': reviewer.strip(),
                'revision': old.get('revision', 0) + 1,
                'created_at_utc': old.get('created_at_utc', now), 'updated_at_utc': now,
                'round': self.round_number,
                'validation_mode': ('adjudication_unblinded_to_text_blinded_to_model'
                                    if self.round_number == 1 else
                                    'adjudication_unblinded_to_text_blinded_to_model_stance'),
            }
            atomic_write_json(path, record)
            return {'decision': record}

    def export(self) -> pd.DataFrame:
        """Decisions as a table, one row per adjudicated block × concept."""
        rows = [json.loads(p.read_text()) for p in sorted((self.queue_dir / 'decisions').glob('*.json'))]
        columns = ['case_index', 'unit_id', 'concept_id', 'rule', 'primary_stances',
                   'secondary_stances', 'decision', 'note', 'reviewer', 'updated_at_utc']
        return pd.DataFrame(rows, columns=columns) if rows else pd.DataFrame(columns=columns)
