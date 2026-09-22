"""Immutable, resumable Responses API runs; exact evidence is checked locally."""
from __future__ import annotations

import concurrent.futures
import copy
import datetime as dt
import fcntl
import importlib.metadata
import json
import math
import os
import random
import re
import threading
import time
from pathlib import Path
from typing import Any

import jsonschema
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, APIConnectionError, APITimeoutError

from features.atomic_io import atomic_write_bytes, atomic_write_parquet, atomic_write_text
from features.manual_validation.service import (
    QUALITY_FLAGS, ValidationError, ValidationService, atomic_write_json,
    sha256_file, sha256_text,
)

PIPELINE_VERSION = "llm-pilot-1.6.2"
MAX_WORKERS = 32
NON_RETRYABLE_LIMIT_CODES = frozenset({
    "project_spend_limit_exceeded", "organization_spend_limit_exceeded",
    "organization_usage_limit_exceeded", "credit_balance_exhausted",
})
DEFAULT_MODEL = "gpt-6-luna"
DEFAULT_REASONING_EFFORT = "max"
REASONING_EFFORTS = frozenset({"none", "low", "medium", "high", "xhigh", "max"})
# Includes reasoning AND visible output; see OpenAI's reasoning guide.
DEFAULT_MAX_OUTPUT_TOKENS = 32768
DEFAULT_SDK_MAX_RETRIES = 4
MAX_SDK_RETRIES = 4
DEFAULT_INCOMPLETE_RETRY_MAX_OUTPUT_TOKENS = 65536
REQUEST_TIMEOUT_SECONDS = 600
RUN_ID_RE = re.compile(r"^pilot_[0-9a-f]{20}$")
API_POLICY_PATH = Path(__file__).resolve().parents[2] / 'data/proc_data/llm_pilots/api_policy.json'


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def execution_config_from_env() -> tuple[str, str, int, int]:
    """Load selectable execution settings while keeping a bounded retry policy."""
    load_dotenv('.env', override=False)
    model = os.environ.get('ANNOTATIONS_MODEL', DEFAULT_MODEL).strip()
    if not model:
        raise ValueError("ANNOTATIONS_MODEL no puede estar vacío")
    effort = os.environ.get('REASONING_LEVEL', DEFAULT_REASONING_EFFORT).strip().lower()
    if effort not in REASONING_EFFORTS:
        raise ValueError(
            "REASONING_LEVEL debe ser none, low, medium, high, xhigh o max"
        )
    raw_retries = os.environ.get(
        'ANNOTATIONS_MAX_RETRIES', str(DEFAULT_SDK_MAX_RETRIES)
    ).strip()
    if not raw_retries.isdigit():
        raise ValueError("ANNOTATIONS_MAX_RETRIES debe ser un entero entre 0 y 4")
    max_retries = int(raw_retries)
    if not 0 <= max_retries <= MAX_SDK_RETRIES:
        raise ValueError("ANNOTATIONS_MAX_RETRIES debe ser un entero entre 0 y 4")
    raw_fallback_tokens = os.environ.get(
        'ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS',
        str(DEFAULT_INCOMPLETE_RETRY_MAX_OUTPUT_TOKENS),
    ).strip()
    if not raw_fallback_tokens.isdigit() or int(raw_fallback_tokens) < 1:
        raise ValueError(
            "ANNOTATIONS_INCOMPLETE_MAX_OUTPUT_TOKENS debe ser un entero positivo"
        )
    return model, effort, max_retries, int(raw_fallback_tokens)


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
    confidence = {"type": "string", "enum": ["high", "medium", "low"]}
    ids = [c["id"] for c in codebook["concepts"]]
    annotation = object_schema({
        "evidence_text": string,
        "evidence_occurrence": {"type": "integer", "minimum": 1},
        "concept_id": {"type": "string", "enum": ids},
        "stance": {"type": "string", "enum": ["support", "oppose"]},
        "justification": string,
        "confidence": confidence,
    })
    return object_schema({
        "decision": {"type": "string", "enum": ["statements", "no_statements"]},
        "annotations": {"type": "array", "maxItems": 50, "items": annotation},
        # Structured Outputs only accepts minItems/maxItems as array-specific
        # constraints. Duplicate flags are rejected by validate_output below.
        "quality_flags": {"type": "array",
                          "items": {"type": "string", "enum": [
                              flag for flag in QUALITY_FLAGS if flag != "other"
                          ]}},
        "decision_confidence": confidence,
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
                prompt_path: Path, root: Path, model: str = DEFAULT_MODEL,
                effort: str = DEFAULT_REASONING_EFFORT,
                max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
                sdk_max_retries: int = DEFAULT_SDK_MAX_RETRIES,
                incomplete_retry_max_output_tokens: int = (
                    DEFAULT_INCOMPLETE_RETRY_MAX_OUTPUT_TOKENS
                )) -> Path:
    """Content address freezes sample, corpus, book, prompt, schema and API settings."""
    if type(max_output_tokens) is not int or max_output_tokens < 1:
        raise ValueError("max_output_tokens debe ser un entero positivo")
    if effort not in REASONING_EFFORTS:
        raise ValueError("effort debe ser none, low, medium, high, xhigh o max")
    if model in {"gpt-5.6-luna", "gpt-6-luna"} and max_output_tokens > 128000:
        raise ValueError("Luna admite como máximo 128000 tokens de salida")
    if type(sdk_max_retries) is not int or not 0 <= sdk_max_retries <= MAX_SDK_RETRIES:
        raise ValueError("sdk_max_retries debe ser un entero entre 0 y 4")
    if (
        type(incomplete_retry_max_output_tokens) is not int
        or incomplete_retry_max_output_tokens < max_output_tokens
    ):
        raise ValueError(
            "incomplete_retry_max_output_tokens debe ser un entero no menor al límite base"
        )
    if model in {"gpt-5.6-luna", "gpt-6-luna"} and incomplete_retry_max_output_tokens > 128000:
        raise ValueError("Luna admite como máximo 128000 tokens de salida")
    if not selected:
        raise ValueError("La muestra debe contener al menos un bloque")
    prompt = prompt_path.read_text(encoding="utf-8")
    schema = output_schema(service.codebook)
    sources = [{"law_number": s["law_number"], "sha256": s["sha256"]} for s in service.sources]
    requests = [{"unit_id": r["unit_id"], "input": model_input(r)} for r in selected]
    spec = {
        "pipeline_version": PIPELINE_VERSION, "model": model, "reasoning_effort": effort,
        "max_output_tokens": max_output_tokens, "sampling": sampling,
        "sdk_max_retries": sdk_max_retries,
        "incomplete_retry_max_output_tokens": incomplete_retry_max_output_tokens,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "sources": sources, "prompt_sha256": sha256_text(prompt),
        "codebook_sha256": service.codebook_sha256, "output_schema": schema,
        "party_alignment": service.party_alignment.snapshot(),
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
    atomic_write_text(prompt, run_dir / "prompt.md")
    atomic_write_json(run_dir / "codebook.json", service.codebook)
    atomic_write_json(run_dir / "output_schema.json", schema)
    atomic_write_bytes(Path(__file__).read_bytes(), run_dir / 'pipeline.py')
    atomic_write_bytes(
        (Path(__file__).parents[1] / 'manual_validation/service.py').read_bytes(),
        run_dir / 'validation_contract.py',
    )
    # Nested contexts/segments are portable JSON strings in the canonical Parquet.
    frame = pd.DataFrame(selected)
    for column in ("previous_context", "next_context", "source_segments"):
        frame[column] = frame[column].map(canonical)
    atomic_write_parquet(frame, run_dir / "sample.parquet")
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
                                         run_dir/'output_schema.json', run_dir/'pipeline.py',
                                         run_dir/'validation_contract.py',
                                         *sorted((run_dir/'requests').glob('*.json'))]},
        "packages": {p: importlib.metadata.version(p) for p in ['openai', 'pandas', 'pyarrow']},
    }
    atomic_write_json(manifest_path, manifest)
    return run_dir


def validate_output(raw: dict, record: dict, codebook: dict, schema: dict) -> dict:
    jsonschema.validate(raw, schema)
    if len(raw["quality_flags"]) != len(set(raw["quality_flags"])):
        raise ValidationError("Las flags de calidad no se pueden repetir")
    if bool(raw["annotations"]) != (raw["decision"] == "statements"):
        raise ValidationError("Decisión y presencia de declaraciones inconsistentes")
    impactful_flags = {
        "too_short", "truncated", "insufficient_context",
        "segmentation_problem", "other",
    }
    legacy_contract = "needs_human_review" in raw
    if legacy_contract:
        if not raw["decision_justification"].strip():
            raise ValidationError("Falta justificación de la decisión del bloque")
        if impactful_flags.intersection(raw["quality_flags"]) and not raw["needs_human_review"]:
            raise ValidationError("Las incidencias de calidad requieren revisión humana")
        if "other" in raw["quality_flags"] and not raw["limitations"].strip():
            raise ValidationError("La flag other requiere describir la limitación")
        # Frozen legacy schemas remain valid; missing confidence is never inferred.
        if "decision_confidence" in raw:
            uncertain = raw["decision_confidence"] != "high"
            if uncertain and not raw["limitations"].strip():
                raise ValidationError("La confianza de decisión requiere explicar la limitación")
            for annotation in raw["annotations"]:
                level = annotation["confidence"]
                doubt = bool(annotation["justification"]["uncertainty"].strip())
                if doubt != (level != "high"):
                    raise ValidationError("Confianza y explicación de incertidumbre inconsistentes")
                uncertain |= level != "high"
            if uncertain and not raw["needs_human_review"]:
                raise ValidationError("La confianza media o baja requiere revisión humana")
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
        if isinstance(justification, dict):
            if not justification['coding'].strip() or not justification['stance'].strip():
                raise ValidationError("Falta fundamento de código u orientación")
            for alternative in justification['alternatives']:
                if not alternative['reason'].strip():
                    raise ValidationError("Cada alternativa requiere una razón")
                if alternative['concept_id'] == annotation['concept_id']:
                    raise ValidationError("Una alternativa no puede repetir el concepto elegido")
            reference = justification['criterion_reference']
            if annotation['concept_status'] == 'review':
                if annotation['concept_id'] is not None or not annotation['proposed_concept'].strip():
                    raise ValidationError("review requiere concept_id null y concepto propuesto")
                if reference != 'new_concept' or not raw['needs_human_review']:
                    raise ValidationError("Un concepto nuevo debe remitirse a revisión humana")
                if not (justification['uncertainty'].strip() or raw['limitations'].strip()):
                    raise ValidationError("review requiere explicar la brecha conceptual")
            else:
                concept = concepts.get(annotation['concept_id'])
                if concept is None:
                    raise ValidationError("Concepto ausente del libro")
                if annotation['proposed_concept'].strip():
                    raise ValidationError("in_codebook requiere proposed_concept vacío")
                valid_refs = {'definition', 'orientation_anchor'} | {
                    f'include:{i + 1}' for i in range(len(concept.get('include', [])))}
                if reference not in valid_refs or (reference == 'orientation_anchor' and not concept.get(reference)):
                    raise ValidationError("Referencia a criterio inexistente")
            for context in justification['context_evidence']:
                text = (record.get(context['source']) or {}).get('content', '')
                if not context['text'].strip() or context['text'] not in text:
                    raise ValidationError("La cita de contexto no coincide literalmente")
            normalized_input = annotation
        else:
            if not justification.strip():
                raise ValidationError("Falta la justificación breve del código y su orientación")
            concept = concepts.get(annotation['concept_id'])
            if concept is None:
                raise ValidationError("Concepto ausente del libro")
            # The closed-book model contract omits manual-coding fields. Inject
            # their fixed values only in the normalized representation so the
            # downstream evaluation tables remain backward compatible.
            normalized_input = {
                **annotation,
                'concept_status': 'in_codebook',
                'proposed_concept': '',
            }
        normalized_annotation = ValidationService._normalize_annotation({
            **normalized_input, 'annotation_id': f'llm_{index:03d}', 'start_char': start,
            'end_char': start + len(evidence), 'note': '',
        }, record['content'], set(concepts), {})
        identity = (
            start,
            start + len(evidence),
            annotation['concept_id'],
            annotation['stance'],
        )
        if identity in seen:
            raise ValidationError("Se repitió el mismo span, concepto y orientación")
        seen.add(identity)
        if 'confidence' in annotation:
            normalized_annotation['confidence'] = annotation['confidence']
        normalized_annotation['justification'] = justification
        normalized.append(normalized_annotation)
    stances_by_concept: dict[str, set[str]] = {}
    for annotation in normalized:
        concept_id = annotation.get('concept_id')
        if concept_id is not None:
            stances_by_concept.setdefault(concept_id, set()).add(annotation['stance'])
    mixed_concepts = sorted(
        concept_id for concept_id, stances in stances_by_concept.items()
        if stances == {'support', 'oppose'}
    )
    review_reasons = []
    if impactful_flags.intersection(raw['quality_flags']):
        review_reasons.append('quality_flag')
    if raw.get('decision_confidence') not in (None, 'high'):
        review_reasons.append('decision_confidence')
    if any(annotation.get('confidence') not in (None, 'high') for annotation in raw['annotations']):
        review_reasons.append('annotation_confidence')
    if mixed_concepts:
        review_reasons.append('opposite_stances_same_concept')
    if raw.get('needs_human_review') and not review_reasons:
        review_reasons.append('model_requested')
    return {
        **raw,
        'annotations': normalized,
        'needs_human_review': bool(review_reasons),
        'review_reasons': review_reasons,
        'opposite_stance_concepts': mixed_concepts,
    }


def load_sample(run_dir: Path) -> list[dict]:
    frame = pd.read_parquet(run_dir / 'sample.parquet')
    for column in ('previous_context', 'next_context', 'source_segments'):
        frame[column] = frame[column].map(json.loads)
    return frame.to_dict('records')


def output_run_dir(input_run_dir: Path, output_root: Path) -> Path:
    """Resolve a run's result directory below an explicitly selected output root."""
    return output_root / input_run_dir.name


def run_annotations(input_run_dir: Path, *, output_root: Path,
                    execute: bool = False, workers: int = 6,
                    limit: int | None = None) -> pd.DataFrame:
    """Execute frozen inputs and persist responses under the separate output root."""
    if limit is not None and (type(limit) is not int or limit < 0):
        raise ValueError("limit debe ser un entero no negativo")
    result_dir = output_run_dir(input_run_dir, output_root)
    result_dir.mkdir(parents=True, exist_ok=True)
    if not execute:
        return _run_annotations(input_run_dir, result_dir, False, workers, limit)
    # A process lock prevents concurrent invocations spending the same allowance.
    with (result_dir / '.execution.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValidationError("Esta ejecución ya tiene un proceso activo") from exc
        return _run_annotations(input_run_dir, result_dir, True, workers, limit)


def _load_retry_seed(run_dir: Path, index: int) -> dict[str, Any] | None:
    """Load only the small failure ledger used to continue an attempt budget."""
    path = run_dir / 'retry_seeds' / f'{index:05d}.json'
    if not path.exists():
        return None
    try:
        seed = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"El retry seed {index} no contiene JSON válido") from exc
    allowed_statuses = {'incomplete', 'invalid_output', 'error', 'transport_error'}
    if (
        not isinstance(seed, dict)
        or seed.get('sample_index') != index
        or seed.get('status') not in allowed_statuses
        or type(seed.get('attempt_count')) is not int
        or seed['attempt_count'] < 1
        or type(seed.get('last_attempt_max_output_tokens')) is not int
        or seed['last_attempt_max_output_tokens'] < 1
    ):
        raise ValidationError(f"El retry seed {index} no es válido")
    return seed


def _discard_failed_output(result: dict[str, Any]) -> dict[str, Any]:
    """Keep failure accounting and diagnostics without retaining an invalid body."""
    if result.get('status') == 'completed':
        return result
    response = result.get('response') or {}
    metadata_keys = (
        'id', 'object', 'created_at', 'status', 'model', 'incomplete_details',
        'error', 'usage', 'service_tier',
    )
    result['response'] = {
        key: response[key] for key in metadata_keys if key in response
    } or None
    result['output_text'] = ''
    result['failed_output_discarded'] = True
    return result


def _authorize_api_execution(input_run_dir: Path, result_dir: Path,
                             manifest: dict[str, Any]) -> None:
    """Require a valid, narrowly scoped authorization before creating an API client."""
    if not API_POLICY_PATH.is_file():
        raise ValidationError(
            f"Falta la política obligatoria de API: {API_POLICY_PATH}"
        )
    try:
        policy = json.loads(API_POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError("La política de API debe contener JSON válido") from exc
    if not isinstance(policy, dict) or policy.get("allow_api_calls") is not True:
        raise ValidationError(
            "Las llamadas de anotación a la API están desactivadas por la política local"
        )
    grants = policy.get("authorized_runs")
    if not isinstance(grants, dict):
        raise ValidationError("La política de API debe declarar authorized_runs")
    grant = grants.get(input_run_dir.name)
    if not isinstance(grant, dict):
        raise ValidationError("La ejecución no tiene una autorización explícita de API")
    spec = manifest.get("spec")
    if not isinstance(spec, dict):
        raise ValidationError("El manifiesto de ejecución no tiene una especificación válida")
    max_calls = grant.get("max_calls")
    total_attempts = spec.get('sdk_max_retries', 0) + 1
    maximum_attempts = 0
    for index in range(manifest.get('sample_size', 0)):
        if (result_dir / 'results' / f'{index:05d}.json').exists():
            continue
        seed = _load_retry_seed(result_dir, index)
        prior_attempts = seed['attempt_count'] if seed else 0
        maximum_attempts += max(0, total_attempts - prior_attempts)
    authorized_input = grant.get('input_run_dir', grant.get('run_dir'))
    authorized_output = grant.get('output_run_dir', authorized_input)
    if (
        grant.get("model") != spec.get("model")
        or grant.get("reasoning_effort") != spec.get("reasoning_effort")
        or authorized_input != str(input_run_dir.resolve())
        or authorized_output != str(result_dir.resolve())
        or type(max_calls) is not int
        or max_calls < maximum_attempts
    ):
        raise ValidationError(
            "La autorización de API no coincide con la ejecución, modelo, esfuerzo o límite"
        )


def _run_annotations(input_run_dir: Path, result_dir: Path, execute: bool, workers: int,
                     limit: int | None) -> pd.DataFrame:
    manifest = json.loads((input_run_dir / 'manifest.json').read_text())
    if execute:
        _authorize_api_execution(input_run_dir, result_dir, manifest)
    if sha256_file(input_run_dir / 'sample.parquet') != manifest['sample_sha256']:
        raise ValidationError('La muestra congelada fue modificada')
    for name, digest in manifest['artifact_sha256'].items():
        if sha256_file(input_run_dir / name) != digest:
            raise ValidationError(f'El artefacto congelado fue modificado: {name}')
    records = load_sample(input_run_dir)
    codebook = json.loads((input_run_dir / 'codebook.json').read_text())
    schema = manifest['spec']['output_schema']
    pending = [
        i for i in range(len(records))
        if not (result_dir / 'results' / f'{i:05d}.json').exists()
    ]
    if limit is not None:
        pending = pending[:limit]
    if execute and pending:
        load_dotenv('.env', override=False)
        max_retries = manifest['spec'].get('sdk_max_retries', 0)
        fallback_token_cap = manifest['spec'].get(
            'incomplete_retry_max_output_tokens',
            manifest['spec']['max_output_tokens'],
        )
        # Retries are controlled here so the same bound covers transport/API
        # failures, incomplete responses and locally invalid structured output.
        client = OpenAI(timeout=REQUEST_TIMEOUT_SECONDS, max_retries=0)
        # No model preflight request: every network call belongs to an annotation.

        stop_for_account_limit = threading.Event()

        def annotate(index: int) -> dict | None:
            if stop_for_account_limit.is_set():
                return None
            request_path = input_run_dir / 'requests' / f'{index:05d}.json'
            request = json.loads(request_path.read_text())
            attempt_body = copy.deepcopy(request['body'])
            retry_seed = _load_retry_seed(result_dir, index)
            prior_attempts = retry_seed['attempt_count'] if retry_seed else 0
            if retry_seed and retry_seed.get('unit_id') != request['unit_id']:
                raise ValidationError(f"El retry seed {index} no corresponde al request")
            if prior_attempts > max_retries:
                raise ValidationError(f"El bloque {index} ya agotó sus intentos")
            if (
                retry_seed
                and retry_seed['status'] == 'incomplete'
                and retry_seed.get('incomplete_reason') == 'max_output_tokens'
            ):
                attempt_body['max_output_tokens'] = min(
                    retry_seed['last_attempt_max_output_tokens'] * 2,
                    fallback_token_cap,
                )
            result = {'sample_index': index, 'unit_id': request['unit_id'],
                      'request_sha256': sha256_file(request_path),
                      'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                      'status': 'started', 'validation_errors': [], 'normalized': None,
                      'output_text': '', 'response': None,
                      'attempt_count': prior_attempts, 'max_retries': max_retries,
                      'retry_seed': retry_seed}
            # Reserve the attempt before sending. An interrupted/uncertain request
            # remains visible and will not be silently billed again on resume.
            atomic_write_json(result_dir / 'results' / f'{index:05d}.json', result)
            for attempt in range(prior_attempts, max_retries + 1):
                result['attempt_count'] = attempt + 1
                result['attempt_max_output_tokens'] = attempt_body['max_output_tokens']
                result['last_attempt_started_at_utc'] = dt.datetime.now(
                    dt.timezone.utc
                ).isoformat()
                atomic_write_json(result_dir / 'results' / f'{index:05d}.json', result)
                retryable = False
                retry_delay = 0.0
                try:
                    response = client.responses.create(**attempt_body)
                    result['response'] = response.model_dump(mode='json')
                    result['output_text'] = response.output_text
                    if response.status != 'completed':
                        result['status'] = (
                            'incomplete' if response.status == 'incomplete' else 'error'
                        )
                        details = result['response'].get('incomplete_details') or {}
                        error = result['response'].get('error') or {}
                        reason = details.get('reason') or error.get('code') or 'unknown'
                        result['validation_errors'] = [
                            f'API status: {response.status}; reason: {reason}'
                        ]
                        retryable = True
                        if reason == 'max_output_tokens':
                            attempt_body['max_output_tokens'] = min(
                                attempt_body['max_output_tokens'] * 2,
                                fallback_token_cap,
                            )
                    else:
                        raw = json.loads(response.output_text)
                        result['normalized'] = validate_output(
                            raw, records[index], codebook, schema
                        )
                        result['status'] = 'completed'
                        result['validation_errors'] = []
                except (json.JSONDecodeError, jsonschema.ValidationError, ValidationError) as exc:
                    result['status'] = 'invalid_output'
                    result['validation_errors'] = [str(exc)[:2000]]
                    retryable = True
                except APIStatusError as exc:
                    body = exc.body if isinstance(exc.body, dict) else {}
                    nested_error = body.get('error') if isinstance(body.get('error'), dict) else {}
                    api_code = exc.code or body.get('code') or nested_error.get('code')
                    result['status'] = 'error'
                    result['validation_errors'] = [
                        f'API HTTP {exc.status_code}; code={api_code}; detail={str(exc)[:1500]}'
                    ]
                    retryable = (
                        exc.status_code in {408, 409, 429} or exc.status_code >= 500
                    )
                    if api_code in NON_RETRYABLE_LIMIT_CODES:
                        retryable = False
                        stop_for_account_limit.set()
                    elif exc.status_code in {429, 503}:
                        raw_delay = exc.response.headers.get('retry-after')
                        try:
                            retry_delay = float(raw_delay) if raw_delay is not None else None
                        except ValueError:
                            retry_delay = None
                        if retry_delay is None or not math.isfinite(retry_delay) or retry_delay < 0:
                            retry_delay = min(60.0, 2.0 ** attempt)
                        retry_delay += random.uniform(0.0, 0.5)
                except (APIConnectionError, APITimeoutError) as exc:
                    result['status'] = 'transport_error'
                    result['validation_errors'] = [type(exc).__name__]
                    retryable = True
                if result['status'] == 'completed' or not retryable or attempt >= max_retries:
                    break
                print(
                    f"Bloque {index + 1}/{len(records)}: retry "
                    f"{attempt + 1}/{max_retries} tras {result['status']}; "
                    f"próximo max_output_tokens={attempt_body['max_output_tokens']}",
                    flush=True,
                )
                # Do not persist intermediate erroneous responses. Keep only the
                # reserved state and aggregate attempt count until a final result.
                result.update(
                    status='started', validation_errors=[], normalized=None,
                    output_text='', response=None,
                )
                if retry_delay > 0:
                    time.sleep(retry_delay)
            result = _discard_failed_output(result)
            result['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
            atomic_write_json(result_dir / 'results' / f'{index:05d}.json', result)
            print(f"Bloque {index + 1}/{len(records)}: {result['status']}", flush=True)
            return result

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(workers, MAX_WORKERS))) as pool:
                list(pool.map(annotate, pending))
        finally:
            client.close()
    return export_results(input_run_dir, result_dir)


def discard_stored_failed_outputs(input_run_dir: Path,
                                  result_dir: Path | None = None) -> int:
    """Remove bodies of already persisted failures while preserving their audit data."""
    result_dir = result_dir or input_run_dir
    manifest = json.loads((input_run_dir / 'manifest.json').read_text())
    discarded = 0
    for index in range(manifest['sample_size']):
        path = result_dir / 'results' / f'{index:05d}.json'
        if not path.exists():
            continue
        result = json.loads(path.read_text())
        if result.get('status') == 'completed' or result.get('failed_output_discarded'):
            continue
        result = _discard_failed_output(result)
        result['failed_output_discarded_at_utc'] = dt.datetime.now(
            dt.timezone.utc
        ).isoformat()
        atomic_write_json(path, result)
        discarded += 1
    export_results(input_run_dir, result_dir)
    return discarded


def reuse_completed_results(source_dir: Path, destination_dir: Path, *,
                            source_result_dir: Path | None = None,
                            destination_result_dir: Path | None = None) -> int:
    """Reuse only validated completed responses in a compatible successor run."""
    source_result_dir = source_result_dir or source_dir
    destination_result_dir = destination_result_dir or destination_dir
    destination_result_dir.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads((source_dir / 'manifest.json').read_text())
    destination_manifest = json.loads((destination_dir / 'manifest.json').read_text())
    source_spec = source_manifest['spec']
    destination_spec = destination_manifest['spec']
    comparable = (
        'model', 'reasoning_effort', 'max_output_tokens', 'sampling', 'sources',
        'prompt_sha256', 'codebook_sha256', 'output_schema', 'party_alignment',
        'requests_sha256',
    )
    if (
        source_manifest['sample_sha256'] != destination_manifest['sample_sha256']
        or source_manifest['sample_size'] != destination_manifest['sample_size']
        or any(source_spec.get(key) != destination_spec.get(key) for key in comparable)
    ):
        raise ValidationError("Las ejecuciones no son compatibles para reutilizar resultados")
    records = load_sample(destination_dir)
    codebook = json.loads((destination_dir / 'codebook.json').read_text())
    schema = destination_spec['output_schema']
    reused = 0
    for index, record in enumerate(records):
        source_result_path = source_result_dir / 'results' / f'{index:05d}.json'
        destination_result_path = destination_result_dir / 'results' / f'{index:05d}.json'
        if not source_result_path.exists() or destination_result_path.exists():
            continue
        source_result = json.loads(source_result_path.read_text())
        if source_result.get('status') != 'completed':
            continue
        source_request = source_dir / 'requests' / f'{index:05d}.json'
        destination_request = destination_dir / 'requests' / f'{index:05d}.json'
        request_digest = sha256_file(destination_request)
        if (
            sha256_file(source_request) != request_digest
            or source_result.get('request_sha256') != request_digest
            or source_result.get('unit_id') != record['unit_id']
        ):
            raise ValidationError(f"El resultado {index} no corresponde al request de destino")
        raw = json.loads(source_result['output_text'])
        normalized = validate_output(raw, record, codebook, schema)
        reused_result = {
            **source_result,
            'normalized': normalized,
            'reused_from_run': source_dir.name,
            'reused_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        }
        atomic_write_json(destination_result_path, reused_result)
        reused += 1
    export_results(destination_dir, destination_result_dir)
    return reused


def seed_failed_results(source_dir: Path, destination_dir: Path, *,
                        source_result_dir: Path | None = None,
                        destination_result_dir: Path | None = None) -> int:
    """Carry attempt counts, but no erroneous response bodies, to a successor run."""
    source_result_dir = source_result_dir or source_dir
    destination_result_dir = destination_result_dir or destination_dir
    destination_result_dir.mkdir(parents=True, exist_ok=True)
    source_manifest = json.loads((source_dir / 'manifest.json').read_text())
    destination_manifest = json.loads((destination_dir / 'manifest.json').read_text())
    source_spec = source_manifest['spec']
    destination_spec = destination_manifest['spec']
    comparable = (
        'model', 'reasoning_effort', 'max_output_tokens', 'sampling', 'sources',
        'prompt_sha256', 'codebook_sha256', 'output_schema', 'party_alignment',
        'requests_sha256',
    )
    if (
        source_manifest['sample_sha256'] != destination_manifest['sample_sha256']
        or source_manifest['sample_size'] != destination_manifest['sample_size']
        or any(source_spec.get(key) != destination_spec.get(key) for key in comparable)
    ):
        raise ValidationError("Las ejecuciones no son compatibles para continuar reintentos")
    allowed_statuses = {'incomplete', 'invalid_output', 'error', 'transport_error'}
    maximum_attempts = destination_spec.get('sdk_max_retries', 0) + 1
    seeded = 0
    for index in range(destination_manifest['sample_size']):
        source_result_path = source_result_dir / 'results' / f'{index:05d}.json'
        destination_result_path = destination_result_dir / 'results' / f'{index:05d}.json'
        seed_path = destination_result_dir / 'retry_seeds' / f'{index:05d}.json'
        if (
            not source_result_path.exists()
            or destination_result_path.exists()
            or seed_path.exists()
        ):
            continue
        result = json.loads(source_result_path.read_text())
        attempts = result.get('attempt_count', 1)
        if (
            result.get('status') not in allowed_statuses
            or type(attempts) is not int
            or not 0 < attempts < maximum_attempts
        ):
            continue
        source_request = source_dir / 'requests' / f'{index:05d}.json'
        destination_request = destination_dir / 'requests' / f'{index:05d}.json'
        request_digest = sha256_file(destination_request)
        if (
            sha256_file(source_request) != request_digest
            or result.get('request_sha256') != request_digest
        ):
            raise ValidationError(f"El fallo {index} no corresponde al request de destino")
        response = result.get('response') or {}
        incomplete_reason = (response.get('incomplete_details') or {}).get('reason')
        seed = {
            'source_run': source_dir.name,
            'sample_index': index,
            'unit_id': result.get('unit_id'),
            'status': result['status'],
            'attempt_count': attempts,
            'incomplete_reason': incomplete_reason,
            'last_attempt_max_output_tokens': result.get(
                'attempt_max_output_tokens', source_spec['max_output_tokens']
            ),
        }
        atomic_write_json(seed_path, seed)
        seeded += 1
    return seeded


def export_results(input_run_dir: Path,
                   result_dir: Path | None = None) -> pd.DataFrame:
    """Build result tables from frozen inputs and separately stored responses."""
    result_dir = result_dir or input_run_dir
    result_dir.mkdir(parents=True, exist_ok=True)
    records = load_sample(input_run_dir)
    spec = json.loads((input_run_dir / 'manifest.json').read_text())['spec']
    rows, spans = [], []
    for i, record in enumerate(records):
        path = result_dir / 'results' / f'{i:05d}.json'
        result = json.loads(path.read_text()) if path.exists() else {'status': 'pending'}
        output = result.get('normalized') or {}
        response = result.get('response') or {}
        usage = response.get('usage') or {}
        annotations = output.get('annotations', [])
        row = {k: record[k] for k in ['unit_id', 'utterance_id', 'law_number', 'document_uri']}
        row.update(sample_index=i, status=result['status'], model=response.get('model'),
                   decision=output.get('decision'), n_annotations=len(annotations),
                   response_status=response.get('status'),
                   incomplete_reason=(response.get('incomplete_details') or {}).get('reason'),
                   api_error_code=(response.get('error') or {}).get('code'),
                   attempt_count=result.get('attempt_count', 0),
                   base_max_output_tokens=spec['max_output_tokens'],
                   max_output_tokens=result.get(
                       'attempt_max_output_tokens', spec['max_output_tokens']
                   ),
                   reasoning_effort=spec['reasoning_effort'],
                   needs_human_review=output.get('needs_human_review'),
                   review_reasons=canonical(output.get('review_reasons', [])),
                   decision_justification=output.get('decision_justification'),
                   limitations=output.get('limitations'),
                   decision_confidence=output.get('decision_confidence'),
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
                          'confidence': annotation.get('confidence'),
                          'justification': (
                              annotation['justification']
                              if isinstance(annotation['justification'], str)
                              else canonical(annotation['justification'])
                          )})
    frame = pd.DataFrame(rows)
    atomic_write_parquet(frame, result_dir / 'results.parquet')
    span_frame = pd.DataFrame(spans, columns=['sample_index','unit_id','utterance_id','law_number',
        'document_uri','annotation_id','concept_status','concept_id','proposed_concept','stance',
        'start_char','end_char','evidence_text','justification','confidence'])
    atomic_write_parquet(span_frame, result_dir / 'annotations.parquet')
    atomic_write_json(result_dir / 'status.json', {'run_id': input_run_dir.name,
        'counts': {str(k): int(v) for k,v in frame['status'].value_counts().items()},
        'updated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat()})
    return frame
