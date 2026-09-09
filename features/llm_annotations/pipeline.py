"""Immutable, resumable Responses API runs; exact evidence is checked locally."""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import importlib.metadata
import json
import math
import re
from pathlib import Path
from typing import Any

import jsonschema
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, APIConnectionError, APITimeoutError

from features.manual_validation.service import (
    QUALITY_FLAGS, ValidationError, ValidationService, atomic_write_json,
    sha256_file, sha256_text,
)

PIPELINE_VERSION = "llm-pilot-1.0.0"
RUN_ID_RE = re.compile(r"^pilot_[0-9a-f]{20}$")
API_POLICY_PATH = Path(__file__).resolve().parents[2] / 'data/proc_data/llm_pilots/api_policy.json'


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def allocate_quotas(counts: pd.Series, fraction: float) -> pd.Series:
    """Proportional allocation with a minimum of one and exact ceil(fraction*N)."""
    if not 0 < fraction <= 1 or counts.empty or (counts < 1).any():
        raise ValueError("Se requieren estratos no vacíos y 0 < fraction <= 1")
    target = math.ceil(int(counts.sum()) * fraction)
    if target < len(counts):
        raise ValueError("El 10% no permite representar todos los estratos; aumenta la fracción")
    ideal = counts / counts.sum() * target
    quotas = ideal.map(math.floor).clip(lower=1).astype(int)
    # Greatest deficit/excess, deterministic tie order inherited from sorted strata.
    while quotas.sum() < target:
        key = (ideal - quotas).where(quotas < counts, float('-inf')).idxmax()
        quotas.loc[key] += 1
    while quotas.sum() > target:
        key = (quotas - ideal).where(quotas > 1, float('-inf')).idxmax()
        quotas.loc[key] -= 1
    return quotas


def object_schema(properties: dict) -> dict:
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def output_schema(codebook: dict) -> dict:
    string = {"type": "string"}
    ids = [c["id"] for c in codebook["concepts"]]
    justification = object_schema({
        "criterion_reference": string, "coding": string, "stance": string,
        "alternatives": {"type": "array", "items": object_schema({
            "concept_id": {"type": "string", "enum": ids}, "reason": string})},
        "context_evidence": {"type": "array", "items": object_schema({
            "source": {"type": "string", "enum": ["previous_context", "next_context"]},
            "text": string})},
        "uncertainty": string,
    })
    annotation = object_schema({
        "evidence_text": string,
        "evidence_occurrence": {"type": "integer", "minimum": 1},
        "concept_status": {"type": "string", "enum": ["in_codebook", "review"]},
        "concept_id": {"type": ["string", "null"], "enum": ids + [None]},
        "proposed_concept": string,
        "stance": {"type": "string", "enum": ["support", "oppose"]},
        "justification": justification,
    })
    return object_schema({
        "decision": {"type": "string", "enum": ["statements", "no_statements"]},
        "annotations": {"type": "array", "maxItems": 50, "items": annotation},
        "decision_justification": string,
        "quality_flags": {"type": "array", "items": {"type": "string", "enum": list(QUALITY_FLAGS)}},
        "needs_human_review": {"type": "boolean"},
        "limitations": string,
    })


def model_input(record: dict) -> dict:
    """Same objective/adjacent blocks and public metadata exposed by the manual app."""
    context = lambda key: (None if record[key] is None else {
        "content": record[key]["content"], "same_utterance": record[key]["same_utterance"]})
    return {
        "law_number": record["law_number"], "date": record["date"],
        "constitutional_stage": record["constitutional_stage"], "title": record["title"],
        "paragraph_start": record["paragraph_start"], "paragraph_end": record["paragraph_end"],
        "paragraph_count": record["paragraph_count"], "n_words": record["n_words"],
        "previous_context": context("previous_context"),
        "target_text": record["content"], "next_context": context("next_context"),
    }


def prepare_run(service: ValidationService, selected: list[dict], sampling: dict,
                prompt_path: Path, root: Path, model: str, effort: str,
                max_output_tokens: int = 16384) -> Path:
    """Content address freezes sample, corpus, book, prompt, schema and API settings."""
    prompt = prompt_path.read_text(encoding="utf-8")
    schema = output_schema(service.codebook)
    sources = [{"law_number": s["law_number"], "sha256": s["sha256"]} for s in service.sources]
    requests = [{"unit_id": r["unit_id"], "input": model_input(r)} for r in selected]
    spec = {
        "pipeline_version": PIPELINE_VERSION, "model": model, "reasoning_effort": effort,
        "max_output_tokens": max_output_tokens, "sampling": sampling,
        "sources": sources, "prompt_sha256": sha256_text(prompt),
        "codebook_sha256": service.codebook_sha256, "output_schema": schema,
        "requests_sha256": sha256_text(canonical(requests)),
        "runner_sha256": sha256_file(Path(__file__)),
        "validation_contract_sha256": sha256_file(Path(__file__).parents[1] / 'manual_validation/service.py'),
    }
    run_id = 'pilot_' + sha256_text(canonical(spec))[:20]
    run_dir = root / run_id
    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        existing = json.loads(manifest_path.read_text())
        if existing["spec"] != spec:
            raise ValidationError("La ejecución existente no coincide con la configuración")
        if sha256_file(run_dir / 'sample.parquet') != existing['sample_sha256']:
            raise ValidationError("La muestra congelada fue modificada")
        for name, digest in existing['artifact_sha256'].items():
            if sha256_file(run_dir / name) != digest:
                raise ValidationError(f"El artefacto congelado fue modificado: {name}")
        return run_dir
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    atomic_write_json(run_dir / "codebook.json", service.codebook)
    atomic_write_json(run_dir / "output_schema.json", schema)
    (run_dir / 'pipeline.py').write_bytes(Path(__file__).read_bytes())
    (run_dir / 'validation_contract.py').write_bytes(
        (Path(__file__).parents[1] / 'manual_validation/service.py').read_bytes())
    # Nested contexts/segments are portable JSON strings in the canonical Parquet.
    frame = pd.DataFrame(selected)
    for column in ("previous_context", "next_context", "source_segments"):
        frame[column] = frame[column].map(canonical)
    frame.to_parquet(run_dir / "sample.parquet", index=False)
    instruction = prompt + "\n\nLIBRO DE CÓDIGOS (snapshot íntegro)\n" + canonical(service.codebook)
    for index, req in enumerate(requests):
        body = {"model": model, "reasoning": {"effort": effort}, "store": False,
                "instructions": instruction,
                "input": [{"role": "user", "content": canonical(req["input"])}],
                "text": {"format": {"type": "json_schema", "name": "pilot_annotation",
                                    "strict": True, "schema": schema}},
                "max_output_tokens": max_output_tokens}
        atomic_write_json(run_dir / "requests" / f"{index:05d}.json",
                          {"sample_index": index, "unit_id": req["unit_id"], "body": body})
    manifest = {
        "schema_version": PIPELINE_VERSION, "run_id": run_id, "spec": spec,
        "created_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "codebook_version": service.codebook["version"], "prompt_path": str(prompt_path),
        "sample_size": len(selected), "sample_sha256": sha256_file(run_dir / 'sample.parquet'),
        "artifact_sha256": {str(path.relative_to(run_dir)): sha256_file(path)
                            for path in [run_dir/'prompt.md', run_dir/'codebook.json',
                                         run_dir/'output_schema.json', *sorted((run_dir/'requests').glob('*.json'))]},
        "packages": {p: importlib.metadata.version(p) for p in ['openai', 'pandas', 'pyarrow']},
    }
    atomic_write_json(manifest_path, manifest)
    return run_dir


def validate_output(raw: dict, record: dict, codebook: dict, schema: dict) -> dict:
    jsonschema.validate(raw, schema)
    if bool(raw["annotations"]) != (raw["decision"] == "statements"):
        raise ValidationError("Decisión y presencia de declaraciones inconsistentes")
    if not raw["decision_justification"].strip():
        raise ValidationError("Falta justificación de la decisión del bloque")
    concepts = {c["id"]: c for c in codebook["concepts"]}
    normalized = []
    seen = set()
    for index, annotation in enumerate(raw["annotations"]):
        evidence = annotation["evidence_text"]
        if not evidence.strip():
            raise ValidationError("La evidencia está vacía")
        positions = [m.start() for m in re.finditer('(?=' + re.escape(evidence) + ')', record['content'])]
        occurrence = annotation["evidence_occurrence"]
        if occurrence > len(positions):
            raise ValidationError(f"La cita {index + 1} no existe literalmente en el objetivo")
        start = positions[occurrence - 1]
        justification = annotation["justification"]
        if not justification['coding'].strip() or not justification['stance'].strip():
            raise ValidationError("Falta fundamento de código u orientación")
        reference = justification['criterion_reference']
        if annotation['concept_status'] == 'review':
            if annotation['concept_id'] is not None or not annotation['proposed_concept'].strip():
                raise ValidationError("review requiere concept_id null y concepto propuesto")
            if reference != 'new_concept' or not raw['needs_human_review']:
                raise ValidationError("Un concepto nuevo debe remitirse a revisión humana")
        else:
            concept = concepts.get(annotation['concept_id'])
            if concept is None:
                raise ValidationError("Concepto ausente del libro")
            valid_refs = {'definition', 'orientation_anchor'} | {
                f'include:{i + 1}' for i in range(len(concept.get('include', [])))}
            if reference not in valid_refs or (reference == 'orientation_anchor' and not concept.get(reference)):
                raise ValidationError("Referencia a criterio inexistente")
        for context in justification['context_evidence']:
            text = (record.get(context['source']) or {}).get('content', '')
            if not context['text'].strip() or context['text'] not in text:
                raise ValidationError("La cita de contexto no coincide literalmente")
        normalized_annotation = ValidationService._normalize_annotation({
            **annotation, 'annotation_id': f'llm_{index:03d}', 'start_char': start,
            'end_char': start + len(evidence), 'note': '',
        }, record['content'], set(concepts), {})
        identity = (start, start + len(evidence), annotation['concept_id'], annotation['proposed_concept'])
        if identity in seen:
            raise ValidationError("Se repitió el mismo span/concepto")
        seen.add(identity)
        normalized_annotation['justification'] = justification
        normalized.append(normalized_annotation)
    return {**raw, 'annotations': normalized}


def load_sample(run_dir: Path) -> list[dict]:
    frame = pd.read_parquet(run_dir / 'sample.parquet')
    for column in ('previous_context', 'next_context', 'source_segments'):
        frame[column] = frame[column].map(json.loads)
    return frame.to_dict('records')


def run_annotations(run_dir: Path, execute: bool = False, workers: int = 6,
                    limit: int | None = None) -> pd.DataFrame:
    """Never resends existing attempts automatically, including failures/incomplete output."""
    if execute and API_POLICY_PATH.exists():
        policy = json.loads(API_POLICY_PATH.read_text(encoding='utf-8'))
        if policy.get('allow_api_calls') is not True:
            raise ValidationError('Las llamadas de anotación a la API están desactivadas por instrucción del usuario')
    manifest = json.loads((run_dir / 'manifest.json').read_text())
    if sha256_file(run_dir / 'sample.parquet') != manifest['sample_sha256']:
        raise ValidationError('La muestra congelada fue modificada')
    for name, digest in manifest['artifact_sha256'].items():
        if sha256_file(run_dir / name) != digest:
            raise ValidationError(f'El artefacto congelado fue modificado: {name}')
    records = load_sample(run_dir)
    codebook = json.loads((run_dir / 'codebook.json').read_text())
    schema = manifest['spec']['output_schema']
    pending = [i for i in range(len(records)) if not (run_dir / 'results' / f'{i:05d}.json').exists()]
    if limit is not None:
        pending = pending[:limit]
    if execute and pending:
        load_dotenv('.env', override=False)
        client = OpenAI(timeout=240, max_retries=2)
        # Check access before launching paid requests. No substitute model is allowed.
        client.models.retrieve(manifest['spec']['model'])

        def annotate(index: int) -> dict:
            request_path = run_dir / 'requests' / f'{index:05d}.json'
            request = json.loads(request_path.read_text())
            result = {'sample_index': index, 'unit_id': request['unit_id'],
                      'request_sha256': sha256_file(request_path),
                      'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                      'status': 'error', 'validation_errors': [], 'normalized': None,
                      'output_text': '', 'response': None}
            try:
                response = client.responses.create(**request['body'])
                result['response'] = response.model_dump(mode='json')
                result['output_text'] = response.output_text
                result['status'] = 'received'
                atomic_write_json(run_dir / 'results' / f'{index:05d}.json', result)
                if response.status != 'completed':
                    result['status'] = 'incomplete'
                    result['validation_errors'] = [f'API status: {response.status}']
                else:
                    raw = json.loads(response.output_text)
                    result['normalized'] = validate_output(raw, records[index], codebook, schema)
                    result['status'] = 'completed'
            except (json.JSONDecodeError, jsonschema.ValidationError, ValidationError) as exc:
                result['status'] = 'invalid_output'
                result['validation_errors'] = [str(exc)[:2000]]
            except APIStatusError as exc:
                result['validation_errors'] = [f'API HTTP {exc.status_code}; code={exc.code}']
            except (APIConnectionError, APITimeoutError) as exc:
                result['status'] = 'transport_error'
                result['validation_errors'] = [type(exc).__name__]
            result['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
            atomic_write_json(run_dir / 'results' / f'{index:05d}.json', result)
            print(f"Bloque {index + 1}/{len(records)}: {result['status']}", flush=True)
            return result

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, 16))) as pool:
            list(pool.map(annotate, pending))
        client.close()
    return export_results(run_dir)


def export_results(run_dir: Path) -> pd.DataFrame:
    records = load_sample(run_dir)
    rows, spans = [], []
    for i, record in enumerate(records):
        path = run_dir / 'results' / f'{i:05d}.json'
        result = json.loads(path.read_text()) if path.exists() else {'status': 'pending'}
        output = result.get('normalized') or {}
        response = result.get('response') or {}
        usage = response.get('usage') or {}
        annotations = output.get('annotations', [])
        row = {k: record[k] for k in ['unit_id', 'utterance_id', 'law_number', 'document_uri']}
        row.update(sample_index=i, status=result['status'], model=response.get('model'),
                   decision=output.get('decision'), n_annotations=len(annotations),
                   needs_human_review=output.get('needs_human_review'),
                   decision_justification=output.get('decision_justification'),
                   limitations=output.get('limitations'),
                   quality_flags=canonical(output.get('quality_flags', [])),
                   validation_errors=canonical(result.get('validation_errors', [])),
                   input_tokens=usage.get('input_tokens', 0), output_tokens=usage.get('output_tokens', 0),
                   cached_input_tokens=(usage.get('input_tokens_details') or {}).get('cached_tokens', 0),
                   reasoning_tokens=(usage.get('output_tokens_details') or {}).get('reasoning_tokens', 0))
        rows.append(row)
        for annotation in annotations:
            spans.append({**{k: row[k] for k in ['sample_index','unit_id','utterance_id','law_number','document_uri']},
                          'annotation_id': annotation['annotation_id'],
                          'concept_status': annotation['concept_status'], 'concept_id': annotation['concept_id'],
                          'proposed_concept': annotation['proposed_concept'], 'stance': annotation['stance'],
                          'start_char': annotation['span']['start_char'], 'end_char': annotation['span']['end_char'],
                          'evidence_text': annotation['span']['text'],
                          'justification': canonical(annotation['justification'])})
    frame = pd.DataFrame(rows)
    frame.to_parquet(run_dir / 'results.parquet', index=False)
    span_frame = pd.DataFrame(spans, columns=['sample_index','unit_id','utterance_id','law_number',
        'document_uri','annotation_id','concept_status','concept_id','proposed_concept','stance',
        'start_char','end_char','evidence_text','justification'])
    span_frame.to_parquet(run_dir / 'annotations.parquet', index=False)
    atomic_write_json(run_dir / 'status.json', {'run_id': run_dir.name,
        'counts': {str(k): int(v) for k,v in frame['status'].value_counts().items()},
        'updated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()})
    return frame
