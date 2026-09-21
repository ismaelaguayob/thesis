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
    def __init__(self, runs_dir: Path, reviews_dir: Path,
                 unit_metadata: dict[str, dict[str, str]] | None = None,
                 source_hashes: dict[str, str] | None = None,
                 results_dir: Path | None = None):
        self.inputs_dir = runs_dir.resolve()
        self.results_dir = (results_dir or runs_dir).resolve()
        self.reviews_dir = reviews_dir.resolve()
        self.unit_metadata = unit_metadata or {}
        self.source_hashes = source_hashes
        self.lock = threading.RLock()

    def _run_dirs(self, run_id: str) -> tuple[Path, Path]:
        if not RUN_ID_RE.fullmatch(run_id):
            raise ValidationError('Identificador de ejecución inválido')
        input_directory = self.inputs_dir / run_id
        result_directory = self.results_dir / run_id
        if not (input_directory / 'manifest.json').exists():
            # Historical runs may still be self-contained below output/annotations.
            input_directory = result_directory
        if not (input_directory / 'manifest.json').exists():
            raise FileNotFoundError('No existe esa ejecución')
        if not result_directory.exists():
            result_directory = input_directory
        return input_directory, result_directory

    def _review_path(self, run_id: str, index: int) -> Path:
        return self.reviews_dir / run_id / f'{index:05d}.json'

    def list_runs(self) -> dict:
        runs = []
        manifests = {
            path.parent.name: path
            for root in (self.results_dir, self.inputs_dir)
            for path in root.glob('pilot_*/manifest.json')
        }
        for path in sorted(manifests.values()):
            manifest = json.loads(path.read_text())
            input_directory, result_directory = self._run_dirs(manifest['run_id'])
            reviewed = len(list((self.reviews_dir / input_directory.name).glob('*.json')))
            runs.append({
                'run_id': manifest['run_id'], 'created_at_utc': manifest['created_at_utc'],
                'model': manifest['spec']['model'], 'reasoning_effort': manifest['spec']['reasoning_effort'],
                'codebook_version': manifest['codebook_version'], 'sample_size': manifest['sample_size'],
                'attempted': len(list((result_directory / 'results').glob('*.json'))),
                'reviewed': reviewed, 'prompt_sha256': manifest['spec']['prompt_sha256'],
            })
        runs.sort(key=lambda r: r['created_at_utc'], reverse=True)
        return {'runs': runs}

    def list_items(self, run_id: str) -> dict:
        input_directory, result_directory = self._run_dirs(run_id)
        manifest = json.loads((input_directory / 'manifest.json').read_text())
        frozen_hashes = {
            str(source['law_number']): source['sha256']
            for source in manifest.get('spec', {}).get('sources', [])
        }
        records = load_sample(input_directory)
        items = []
        for index, record in enumerate(records):
            result_path = result_directory / 'results' / f'{index:05d}.json'
            result = json.loads(result_path.read_text()) if result_path.exists() else {}
            review_path = self._review_path(run_id, index)
            review = json.loads(review_path.read_text()) if review_path.exists() else {}
            normalized = result.get('normalized') or {}
            model_annotations = normalized.get('annotations', [])
            valid_ids = {annotation['annotation_id'] for annotation in model_annotations}
            saved_annotations = review.get('annotations', [])
            saved_ids = {annotation.get('annotation_id') for annotation in saved_annotations}
            annotations_reviewed = bool(valid_ids) and valid_ids == saved_ids and all(
                annotation.get('verdict') in VERDICTS for annotation in saved_annotations
            )
            review_complete = (
                (not valid_ids and review.get('verdict') in VERDICTS)
                or annotations_reviewed
            )
            review_verdict = review.get('verdict') if review.get('verdict') in VERDICTS else (
                'annotations_reviewed' if annotations_reviewed else None
            )
            law_number = str(record['law_number'])
            same_source = (self.source_hashes is None or
                           self.source_hashes.get(law_number) == frozen_hashes.get(law_number))
            source_strata = (
                self.unit_metadata.get(str(record['unit_id']), {}) if same_source else {}
            )
            strata = {
                'law_number': str(record['law_number']),
                'document_uri': str(record['document_uri']),
                'length_bin': str(record.get('length_bin', 'Sin dato')),
                **{
                    field: str(source_strata.get(field, 'Sin dato'))
                    for field in ('chamber', 'alignment', 'gender', 'actor_type')
                },
            }
            items.append({'sample_index': index, 'law_number': record['law_number'],
                          'session': record['document_uri'].rsplit('/', 1)[-1],
                          'unit_id': record['unit_id'], 'status': result.get('status', 'pending'),
                          'decision': normalized.get('decision'),
                          'n_annotations': len(model_annotations),
                          'needs_human_review': normalized.get('needs_human_review', False),
                          'strata': strata,
                          'strata_source_matches_run': same_source,
                          'review_verdict': review_verdict,
                          'review_complete': review_complete})
        return {'manifest': manifest, 'items': items}

    def open_item(self, run_id: str, index: int) -> dict:
        input_directory, result_directory = self._run_dirs(run_id)
        records = load_sample(input_directory)
        if index < 0 or index >= len(records):
            raise ValidationError('Índice de bloque fuera de rango')
        result_path = result_directory / 'results' / f'{index:05d}.json'
        result = json.loads(result_path.read_text()) if result_path.exists() else None
        review_path = self._review_path(run_id, index)
        return {
            'manifest': json.loads((input_directory / 'manifest.json').read_text()),
            'item': records[index],
            'request': json.loads(
                (input_directory / 'requests' / f'{index:05d}.json').read_text()
            ),
            'result': result, 'result_sha256': sha256_file(result_path) if result else None,
            'codebook': json.loads((input_directory / 'codebook.json').read_text()),
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
            verdict = payload.get('verdict') or None
            if verdict is not None and verdict not in VERDICTS:
                raise ValidationError('Decisión de revisión inválida')
            issues = payload.get('issues', [])
            if not isinstance(issues, list) or any(not isinstance(x, str) or x not in ISSUES for x in issues):
                raise ValidationError('Tipo de problema inválido')
            note = payload.get('note', '')
            reviewer = payload.get('reviewer', '')
            if not isinstance(note, str) or len(note) > 6000 or not isinstance(reviewer, str) or len(reviewer) > 120:
                raise ValidationError('Comentario o identificador inválido')
            annotations = payload.get('annotations', [])
            valid_ids = {a['annotation_id'] for a in (result.get('normalized') or {}).get('annotations', [])}
            has_annotations = bool(valid_ids)
            if not has_annotations and verdict is None:
                raise ValidationError('Selecciona una decisión para el bloque sin códigos')
            if verdict == 'accepted' and result['status'] != 'completed':
                raise ValidationError('Una respuesta inválida o fallida no puede aceptarse')
            if verdict is not None and verdict != 'accepted' and not note.strip():
                raise ValidationError('Describe qué debe cambiar o por qué se descarta el bloque')
            if not isinstance(annotations, list) or len(annotations) != len(valid_ids):
                raise ValidationError('Revisa cada código antes de guardar')
            seen = set()
            for entry in annotations:
                if not isinstance(entry, dict) or entry.get('annotation_id') not in valid_ids:
                    raise ValidationError('Anotación ajena a esta respuesta')
                if entry['annotation_id'] in seen or entry.get('verdict') not in VERDICTS:
                    raise ValidationError('Anotación duplicada o sin decisión')
                seen.add(entry['annotation_id'])
                if not isinstance(entry.get('note', ''), str) or len(entry.get('note', '')) > 2000:
                    raise ValidationError('Comentario de anotación inválido')
                if entry['verdict'] == 'accepted' and result['status'] != 'completed':
                    raise ValidationError('Una respuesta inválida o fallida no puede aceptar códigos')
                if entry['verdict'] != 'accepted' and not entry.get('note', '').strip():
                    raise ValidationError('Describe qué debe cambiar o por qué se descarta el código')
            if verdict == 'accepted' and (issues or any(a['verdict'] != 'accepted' for a in annotations)):
                raise ValidationError('Aceptar el bloque requiere aceptar sus anotaciones y no marcar problemas')
            if issues and not note.strip():
                raise ValidationError('Describe el problema general observado en el bloque')
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
