"""Diagnostic human judgments; original LLM outputs are never modified."""
from __future__ import annotations

import datetime as dt
import json
import threading
from pathlib import Path

from features.llm_annotations.pipeline import RUN_ID_RE, load_sample
from features.manual_validation.service import ValidationError, atomic_write_json, sha256_file

VERDICTS = {'accepted', 'needs_changes', 'discard'}
ISSUES = {'span', 'concept', 'stance', 'omission', 'justification', 'context', 'segmentation', 'other'}


class AnnotationReviewService:
    def __init__(self, runs_dir: Path, reviews_dir: Path):
        self.runs_dir = runs_dir.resolve()
        self.reviews_dir = reviews_dir.resolve()
        self.lock = threading.RLock()

    def _run_dir(self, run_id: str) -> Path:
        if not RUN_ID_RE.fullmatch(run_id):
            raise ValidationError('Identificador de ejecución inválido')
        directory = self.runs_dir / run_id
        if not (directory / 'manifest.json').exists():
            raise FileNotFoundError('No existe esa ejecución')
        return directory

    def _review_path(self, run_id: str, index: int) -> Path:
        return self.reviews_dir / run_id / f'{index:05d}.json'

    def list_runs(self) -> dict:
        runs = []
        for path in sorted(self.runs_dir.glob('pilot_*/manifest.json')):
            manifest = json.loads(path.read_text())
            directory = path.parent
            reviewed = len(list((self.reviews_dir / directory.name).glob('*.json')))
            runs.append({
                'run_id': manifest['run_id'], 'created_at_utc': manifest['created_at_utc'],
                'model': manifest['spec']['model'], 'reasoning_effort': manifest['spec']['reasoning_effort'],
                'codebook_version': manifest['codebook_version'], 'sample_size': manifest['sample_size'],
                'attempted': len(list((directory / 'results').glob('*.json'))),
                'reviewed': reviewed, 'prompt_sha256': manifest['spec']['prompt_sha256'],
            })
        runs.sort(key=lambda r: r['created_at_utc'], reverse=True)
        return {'runs': runs}

    def list_items(self, run_id: str) -> dict:
        directory = self._run_dir(run_id)
        manifest = json.loads((directory / 'manifest.json').read_text())
        records = load_sample(directory)
        items = []
        for index, record in enumerate(records):
            result_path = directory / 'results' / f'{index:05d}.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else {}
            review_path = self._review_path(run_id, index)
            review = json.loads(review_path.read_text()) if review_path.exists() else {}
            normalized = result.get('normalized') or {}
            items.append({'sample_index': index, 'law_number': record['law_number'],
                          'session': record['document_uri'].rsplit('/', 1)[-1],
                          'unit_id': record['unit_id'], 'status': result.get('status', 'pending'),
                          'decision': normalized.get('decision'),
                          'n_annotations': len(normalized.get('annotations', [])),
                          'needs_human_review': normalized.get('needs_human_review', False),
                          'review_verdict': review.get('verdict')})
        return {'manifest': manifest, 'items': items}

    def open_item(self, run_id: str, index: int) -> dict:
        directory = self._run_dir(run_id)
        records = load_sample(directory)
        if index < 0 or index >= len(records):
            raise ValidationError('Índice de bloque fuera de rango')
        result_path = directory / 'results' / f'{index:05d}.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        review_path = self._review_path(run_id, index)
        return {
            'manifest': json.loads((directory / 'manifest.json').read_text()),
            'item': records[index],
            'request': json.loads((directory / 'requests' / f'{index:05d}.json').read_text()),
            'result': result, 'result_sha256': sha256_file(result_path) if result else None,
            'codebook': json.loads((directory / 'codebook.json').read_text()),
            'review': json.loads(review_path.read_text()) if review_path.exists() else None,
        }

    def save_review(self, run_id: str, index: int, payload: dict) -> dict:
        with self.lock:
            item = self.open_item(run_id, index)
            result = item['result']
            if not result:
                raise ValidationError('El bloque todavía no tiene una respuesta para revisar')
            if payload.get('result_sha256') != item['result_sha256']:
                raise ValidationError('La respuesta cambió; vuelve a abrir el bloque')
            old = item['review'] or {}
            if payload.get('revision', 0) != old.get('revision', 0):
                raise ValidationError('Otra revisión fue guardada; vuelve a abrir el bloque')
            verdict = payload.get('verdict')
            if verdict not in VERDICTS:
                raise ValidationError('Selecciona una decisión de revisión')
            if verdict == 'accepted' and result['status'] != 'completed':
                raise ValidationError('Una respuesta inválida o fallida no puede aceptarse')
            issues = payload.get('issues', [])
            if not isinstance(issues, list) or any(not isinstance(x, str) or x not in ISSUES for x in issues):
                raise ValidationError('Tipo de problema inválido')
            note = payload.get('note', '')
            reviewer = payload.get('reviewer', '')
            if not isinstance(note, str) or len(note) > 6000 or not isinstance(reviewer, str) or len(reviewer) > 120:
                raise ValidationError('Comentario o identificador inválido')
            if verdict != 'accepted' and not note.strip():
                raise ValidationError('Describe qué debe cambiar o por qué se descarta el bloque')
            annotations = payload.get('annotations', [])
            valid_ids = {a['annotation_id'] for a in (result.get('normalized') or {}).get('annotations', [])}
            if not isinstance(annotations, list) or len(annotations) != len(valid_ids):
                raise ValidationError('Revisa cada anotación, aunque el bloque también tenga un juicio global')
            seen = set()
            for entry in annotations:
                if not isinstance(entry, dict) or entry.get('annotation_id') not in valid_ids:
                    raise ValidationError('Anotación ajena a esta respuesta')
                if entry['annotation_id'] in seen or entry.get('verdict') not in VERDICTS:
                    raise ValidationError('Anotación duplicada o sin decisión')
                seen.add(entry['annotation_id'])
                if not isinstance(entry.get('note', ''), str) or len(entry.get('note', '')) > 2000:
                    raise ValidationError('Comentario de anotación inválido')
            if verdict == 'accepted' and (issues or any(a['verdict'] != 'accepted' for a in annotations)):
                raise ValidationError('Aceptar el bloque requiere aceptar sus anotaciones y no marcar problemas')
            now = dt.datetime.now(dt.timezone.utc).isoformat()
            review = {'schema_version': 'llm-diagnostic-review-1.0.0', 'run_id': run_id,
                      'sample_index': index, 'unit_id': item['item']['unit_id'],
                      'result_sha256': item['result_sha256'], 'reviewer': reviewer.strip(),
                      'verdict': verdict, 'issues': sorted(set(issues)), 'note': note.strip(),
                      'annotations': [{k: a.get(k, '') for k in ['annotation_id', 'verdict', 'note']} for a in annotations],
                      'revision': old.get('revision', 0) + 1,
                      'created_at_utc': old.get('created_at_utc', now), 'updated_at_utc': now,
                      'validation_mode': 'diagnostic_unblinded'}
            atomic_write_json(self._review_path(run_id, index), review)
            return {'review': review}
