"""Local manual-validation application for discourse coding.

The module keeps sampling, validation and persistence independent from the web
interface.  It intentionally exposes no speaker names, speaker identifiers,
party labels or gender attributes to the browser.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import mimetypes
import os
import random
import re
import uuid
from collections import defaultdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import pandas as pd

from features.political_alignment import PartyAlignment, load_party_alignment

SCHEMA_VERSION = "manual-validation-2.6.0"
CHUNK_SCHEMA_VERSION = "coding-chunks-2.1.0"
CHUNK_SCHEMA_VERSIONS = {
    "coding-chunks-1.0.0",
    "coding-chunks-2.0.0",
    CHUNK_SCHEMA_VERSION,
}
LAW_BY_BILL = {"15480-13": "21735", "14588-13": "21419", "15625-13": "21538"}
DEFAULT_TIMEZONE = "America/Santiago"
SESSION_ID_RE = re.compile(r"^validation_\d{8}T\d{12}Z_[0-9a-f]{8}$")
ALLOWED_STANCES = {"support", "oppose"}
ALLOWED_CONCEPT_STATUSES = {"in_codebook", "review"}
ALLOWED_DECISIONS = {"statements", "no_statements"}
ALLOWED_RESOLUTION_STATUSES = {"resolved", "unresolved"}
ALLOWED_STRATEGIES = {"stratified", "random"}
ALLOWED_SAMPLING_UNITS = {"block", "utterance"}
STRATIFICATION_FIELDS = {
    "law_number": "Ley",
    "chamber": "Cámara",
    "alignment": "Alineación o condición política",
    "gender": "Género",
    "actor_type": "Tipo de actor",
    "document_uri": "Discusión en Sala",
    "length_bin": "Longitud",
}
# Preserve the remote baseline coverage by law and chamber while replacing party
# with the coarser political-alignment dimension requested for stratification.
DEFAULT_EVALUATION_STRATA = ["law_number", "chamber", "alignment", "gender"]
QUALITY_FLAGS = {
    "vote": "Voto",
    "procedural": "Procedimental",
    "too_short": "Texto demasiado breve",
    "truncated": "Texto truncado",
    "insufficient_context": "Contexto insuficiente",
    "segmentation_problem": "Problema de segmentación",
    "other": "Otro problema",
}
EVALUATION_EXCLUSION_FLAGS = {"vote", "procedural"}
UNRESOLVED_REASON_FLAGS = {
    "too_short", "truncated", "insufficient_context", "segmentation_problem", "other",
}
MAX_REQUEST_BYTES = 2_000_000


def law_label(law_number: str) -> str:
    if law_number == "all":
        return "Todas las leyes"
    if law_number.isdigit():
        return f"Ley {int(law_number):,}".replace(",", ".")
    return f"Boletín {law_number}"


def _sampling_value(value: Any, missing: str = "Sin dato") -> str:
    result = _text(value).strip()
    return result if result else missing


def _actor_type(role: Any, speaker_bcn_id: Any = None, party: Any = None) -> str:
    normalized = _sampling_value(role, "").casefold()
    if "diputad" in normalized or "senador" in normalized:
        return "Parlamentario"
    if "ministr" in normalized or "subsecret" in normalized:
        return "Ejecutivo"
    if any(token in normalized for token in (
        "president", "vicepresident", "secretari", "prosecretari",
    )):
        return "Autoridad de la cámara"
    if not normalized and (
        _sampling_value(speaker_bcn_id, "") or _sampling_value(party, "")
    ):
        # Algunos documentos omiten ``role`` para parlamentarios identificados
        # por BCN; partido o ID BCN distinguen esos casos de actores desconocidos.
        return "Parlamentario"
    return "Otro o sin dato"


def _document_chambers(dataframe: pd.DataFrame) -> dict[str, str]:
    chambers: dict[str, str] = {}
    unresolved: list[tuple[str, str]] = []
    for document_uri, group in dataframe.groupby("document_uri", sort=False):
        roles = group["role"].fillna("").astype(str).str.casefold()
        senate = int(roles.str.contains("senador|senado", regex=True).sum())
        chamber = int(roles.str.contains("diputad|cámara", regex=True).sum())
        if senate == chamber:
            stages = group["constitutional_stage"].dropna().astype(str).unique().tolist()
            if len(stages) != 1:
                raise ValidationError(
                    f"No fue posible determinar la cámara de {document_uri}"
                )
            unresolved.append((str(document_uri), stages[0].casefold()))
        else:
            chambers[str(document_uri)] = "Senado" if senate > chamber else "Cámara"

    first_chambers = {
        chambers[str(document_uri)]
        for document_uri, group in dataframe.groupby("document_uri", sort=False)
        if "primer" in _text(group["constitutional_stage"].iloc[0]).casefold()
        and str(document_uri) in chambers
    }
    first_chamber = next(iter(first_chambers)) if len(first_chambers) == 1 else None
    for document_uri, stage in unresolved:
        if first_chamber and ("primer" in stage or "tercer" in stage):
            chambers[document_uri] = first_chamber
        elif first_chamber and "segundo" in stage:
            chambers[document_uri] = "Cámara" if first_chamber == "Senado" else "Senado"
        else:
            raise ValidationError(
                f"No fue posible determinar la cámara de {document_uri}"
            )
    return chambers


def _utterance_length_bin(n_words: int) -> str:
    if n_words <= 75:
        return "short_000_075"
    if n_words <= 500:
        return "medium_076_500"
    return "long_501_plus"


class ValidationError(ValueError):
    """Raised when an annotation or configuration violates the contract."""


def _clean_scalar(value: Any) -> Any:
    """Convert pandas/numpy missing scalars to JSON-safe Python values."""
    if value is None:
        return None
    try:
        if bool(pd.isna(value)):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(value, "item"):
        try:
            return value.item()
        except (AttributeError, ValueError):
            pass
    return value


def _text(value: Any) -> str:
    value = _clean_scalar(value)
    return "" if value is None else str(value)


def _limited_text(value: Any, field: str, limit: int) -> str:
    result = _text(value).strip()
    if len(result) > limit:
        raise ValidationError(f"{field} supera el máximo de {limit} caracteres")
    return result


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool):
        raise ValidationError(f"{field} debe ser un número entero")
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.fullmatch(r"[+-]?\d+", value.strip()):
        return int(value.strip())
    raise ValidationError(f"{field} debe ser un número entero")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def timestamp_pair(timezone_name: str = DEFAULT_TIMEZONE) -> dict[str, str]:
    now_utc = dt.datetime.now(dt.timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo(timezone_name))
    return {
        "utc": now_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "local": now_local.isoformat(timespec="milliseconds"),
    }


def _session_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def load_codebook(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el libro de códigos: {path}")
    with path.open(encoding="utf-8") as handle:
        codebook = json.load(handle)
    if not isinstance(codebook, dict):
        raise ValidationError("El libro de códigos debe ser un objeto JSON")
    concepts = codebook.get("concepts")
    if not isinstance(concepts, list) or not concepts:
        raise ValidationError("El libro de códigos debe incluir una lista no vacía de concepts")
    seen: set[str] = set()
    for position, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            raise ValidationError(f"El concepto {position} debe ser un objeto")
        concept_id = _limited_text(concept.get("id"), f"concepts[{position}].id", 120)
        label = _limited_text(concept.get("label"), f"concepts[{position}].label", 200)
        definition = _limited_text(
            concept.get("definition"), f"concepts[{position}].definition", 4000
        )
        orientation_anchor = _limited_text(
            concept.get("orientation_anchor"),
            f"concepts[{position}].orientation_anchor",
            4000,
        )
        if not concept_id or not label or not definition or not orientation_anchor:
            raise ValidationError(
                f"El concepto {position} requiere id, label, definition y orientation_anchor"
            )
        if not re.fullmatch(r"[a-z0-9_]+", concept_id):
            raise ValidationError(f"ID de concepto inválido: {concept_id}")
        if concept_id in seen:
            raise ValidationError(f"ID de concepto duplicado: {concept_id}")
        for criteria_field in ("include", "exclude"):
            criteria = concept.get(criteria_field, [])
            if not isinstance(criteria, list):
                raise ValidationError(
                    f"concepts[{position}].{criteria_field} debe ser una lista"
                )
            for criterion_index, criterion in enumerate(criteria):
                criterion_text = _limited_text(
                    criterion,
                    f"concepts[{position}].{criteria_field}[{criterion_index}]",
                    2000,
                )
                if not criterion_text:
                    raise ValidationError(
                        f"concepts[{position}].{criteria_field}[{criterion_index}] está vacío"
                    )
        seen.add(concept_id)
    codebook.setdefault("schema_version", "codebook-1.0.0")
    codebook.setdefault("version", "unversioned")
    codebook.setdefault("status", "draft")
    codebook.setdefault("title", "Libro de códigos")
    return codebook


def _context_record(record: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    return {
        "unit_id": record["unit_id"],
        "utterance_id": record["utterance_id"],
        "paragraph_number": record["paragraph_number"],
        "paragraph_start": record["paragraph_start"],
        "paragraph_end": record["paragraph_end"],
        "block_paragraph_count": record["block_paragraph_count"],
        "paragraph_count": record["paragraph_count"],
        "content": record["content"],
        "content_sha256": record["content_sha256"],
        "same_utterance": record["utterance_id"] == target["utterance_id"],
    }


def load_corpus_records(
    source_path: Path,
) -> list[dict[str, Any]]:
    """Load the finalized long-form chunk corpus produced by ``proc.qmd``."""
    if not source_path.exists():
        raise FileNotFoundError(f"No existe el corpus: {source_path}")
    dataframe = pd.read_parquet(source_path)
    required = {
        "chunk_id",
        "chunk_schema_version",
        "unit_id",
        "unit_kind",
        "utterance_id",
        "document_uri",
        "utterance_order",
        "document_chunk_order",
        "utterance_chunk_number",
        "utterance_chunk_count",
        "paragraph_number",
        "paragraph_start",
        "paragraph_end",
        "block_paragraph_count",
        "paragraph_count",
        "source_start_char",
        "source_end_char",
        "source_segments_json",
        "source_utterance_n_words",
        "date",
        "constitutional_stage",
        "regulatory_stage",
        "title",
        "bill_number",
        "role",
        "gender",
        "current_party",
        "party_at_date",
        "party_at_date_status",
        "militancy_at_date_status",
        "affiliation_data_status",
        "content",
        "content_sha256",
        "n_words",
        "length_bin",
        "previous_chunk_id",
        "next_chunk_id",
        "minimum_words",
        "short_paragraph_words",
        "target_block_words",
        "max_block_words",
    }
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise ValidationError(
            f"Faltan columnas requeridas en el corpus de chunks: {', '.join(missing)}"
        )
    if dataframe.empty:
        raise ValidationError("El corpus de chunks está vacío")
    if dataframe["unit_id"].duplicated().any():
        duplicates = dataframe.loc[dataframe["unit_id"].duplicated(), "unit_id"].tolist()
        raise ValidationError(f"unit_id duplicado en el corpus: {duplicates[:3]}")
    if not dataframe["chunk_id"].astype(str).eq(dataframe["unit_id"].astype(str)).all():
        raise ValidationError("chunk_id y unit_id deben identificar la misma unidad")
    if not dataframe["unit_kind"].eq("paragraph_block").all():
        raise ValidationError("unit_kind debe ser paragraph_block en todo el corpus")

    integer_fields = [
        "document_chunk_order",
        "utterance_chunk_number",
        "utterance_chunk_count",
        "paragraph_number",
        "paragraph_start",
        "paragraph_end",
        "block_paragraph_count",
        "paragraph_count",
        "source_start_char",
        "source_end_char",
        "source_utterance_n_words",
        "n_words",
        "minimum_words",
        "short_paragraph_words",
        "target_block_words",
        "max_block_words",
    ]
    for field in integer_fields:
        numeric = pd.to_numeric(dataframe[field], errors="coerce")
        if numeric.isna().any() or not numeric.mod(1).eq(0).all():
            raise ValidationError(f"{field} debe contener enteros sin valores ausentes")
        dataframe[field] = numeric.astype(int)

    for field in (
        "minimum_words",
        "short_paragraph_words",
        "target_block_words",
        "max_block_words",
        "chunk_schema_version",
        "bill_number",
    ):
        if dataframe[field].nunique(dropna=False) != 1:
            raise ValidationError(f"{field} debe tener un único valor en el corpus")
    minimum_words = int(dataframe["minimum_words"].iloc[0])
    short_paragraph_words = int(dataframe["short_paragraph_words"].iloc[0])
    target_block_words = int(dataframe["target_block_words"].iloc[0])
    max_block_words = int(dataframe["max_block_words"].iloc[0])
    chunk_schema_version = str(dataframe["chunk_schema_version"].iloc[0])
    if chunk_schema_version not in CHUNK_SCHEMA_VERSIONS:
        raise ValidationError(
            f"Versión de corpus no soportada: {chunk_schema_version}"
        )
    if not 1 <= minimum_words <= short_paragraph_words <= target_block_words <= max_block_words:
        raise ValidationError("Los parámetros de chunking del corpus son inconsistentes")

    dataframe["content"] = dataframe["content"].fillna("").astype(str)
    if dataframe["content"].str.strip().eq("").any():
        raise ValidationError("El corpus contiene chunks sin texto")
    if dataframe["n_words"].lt(minimum_words).any():
        raise ValidationError("El corpus contiene chunks bajo el mínimo de palabras")
    # La versión 2 absorbe restos breves de ambos lados del corte inicial.
    length_limit = max_block_words
    if chunk_schema_version in {"coding-chunks-2.0.0", "coding-chunks-2.1.0"}:
        length_limit += 2 * (short_paragraph_words - 1)
        short_fragments = dataframe["n_words"].lt(short_paragraph_words) & (
            dataframe["source_utterance_n_words"].ge(short_paragraph_words)
            | dataframe["utterance_chunk_count"].gt(1)
        )
        if short_fragments.any():
            raise ValidationError("El corpus contiene fragmentos breves sin unir")
    if dataframe["n_words"].gt(length_limit).any():
        raise ValidationError("El corpus contiene chunks sobre el máximo de palabras")
    expected_hashes = dataframe["content"].map(sha256_text)
    if not expected_hashes.eq(dataframe["content_sha256"].astype(str)).all():
        raise ValidationError("content_sha256 no coincide con el texto de uno o más chunks")

    dataframe = dataframe.sort_values(
        ["document_uri", "document_chunk_order"], kind="stable"
    ).reset_index(drop=True)
    if dataframe.duplicated(["document_uri", "document_chunk_order"]).any():
        raise ValidationError("document_chunk_order está duplicado dentro de un documento")
    for document_uri, group in dataframe.groupby("document_uri", sort=False):
        expected_order = list(range(1, len(group) + 1))
        if group["document_chunk_order"].tolist() != expected_order:
            raise ValidationError(
                f"document_chunk_order no es consecutivo en {document_uri}"
            )
        chunk_ids = group["chunk_id"].astype(str).tolist()
        expected_previous = [None, *chunk_ids[:-1]]
        expected_next = [*chunk_ids[1:], None]
        for field, expected_values in (
            ("previous_chunk_id", expected_previous),
            ("next_chunk_id", expected_next),
        ):
            actual_values = [_clean_scalar(value) for value in group[field]]
            if actual_values != expected_values:
                raise ValidationError(
                    f"{field} no coincide con el orden de chunks en {document_uri}"
                )
    for (document_uri, utterance_id), group in dataframe.groupby(
        ["document_uri", "utterance_id"], sort=False
    ):
        expected_count = len(group)
        expected_numbers = list(range(1, expected_count + 1))
        if group["utterance_chunk_number"].tolist() != expected_numbers:
            raise ValidationError(
                f"utterance_chunk_number no es consecutivo en {utterance_id}"
            )
        if not group["utterance_chunk_count"].eq(expected_count).all():
            raise ValidationError(
                f"utterance_chunk_count es inconsistente en {utterance_id}"
            )
        starts = group["source_start_char"].tolist()
        ends = group["source_end_char"].tolist()
        if starts != sorted(starts):
            raise ValidationError(
                f"El orden de chunks retrocede dentro de {utterance_id}"
            )
        if any(
            previous_end > next_start
            for previous_end, next_start in zip(ends, starts[1:])
        ):
            raise ValidationError(f"Hay chunks solapados dentro de {utterance_id}")
    if not dataframe["paragraph_start"].le(dataframe["paragraph_end"]).all():
        raise ValidationError("paragraph_start no puede ser mayor que paragraph_end")
    if not dataframe["paragraph_end"].le(dataframe["paragraph_count"]).all():
        raise ValidationError("paragraph_end excede paragraph_count")
    if not dataframe["source_start_char"].lt(dataframe["source_end_char"]).all():
        raise ValidationError("Los offsets de origen deben delimitar texto no vacío")

    document_chambers = _document_chambers(dataframe)
    public_fields = [
        "chunk_id",
        "unit_id",
        "unit_kind",
        "chunk_schema_version",
        "utterance_id",
        "document_uri",
        "utterance_order",
        "document_chunk_order",
        "utterance_chunk_number",
        "utterance_chunk_count",
        "paragraph_number",
        "paragraph_start",
        "paragraph_end",
        "block_paragraph_count",
        "paragraph_count",
        "source_start_char",
        "source_end_char",
        "source_utterance_n_words",
        "date",
        "constitutional_stage",
        "regulatory_stage",
        "title",
        "bill_number",
        "content",
        "content_sha256",
        "n_words",
        "length_bin",
        "previous_chunk_id",
        "next_chunk_id",
        "minimum_words",
        "short_paragraph_words",
        "target_block_words",
        "max_block_words",
    ]
    records: list[dict[str, Any]] = []
    for _, row in dataframe.iterrows():
        record = {field: _clean_scalar(row[field]) for field in public_fields}
        try:
            source_segments = json.loads(_text(row["source_segments_json"]))
        except json.JSONDecodeError as exc:
            raise ValidationError(
                f"source_segments_json inválido en {record['unit_id']}"
            ) from exc
        if not isinstance(source_segments, list) or not source_segments:
            raise ValidationError(
                f"source_segments_json debe ser una lista no vacía en {record['unit_id']}"
            )
        record["source_segments"] = source_segments
        party_status = _sampling_value(row["party_at_date_status"], "unknown")
        party = (
            "No aplica"
            if party_status == "not_applicable"
            else _sampling_value(row["party_at_date"])
        )
        record["_sampling_metadata"] = {
            "chamber": document_chambers[str(record["document_uri"])],
            "party": party,
            "gender": _sampling_value(row["gender"]),
            "actor_type": _actor_type(
                row["role"], row.get("speaker_bcn_id"), row["party_at_date"]
            ),
        }
        record["previous_context"] = None
        record["next_context"] = None
        records.append(record)

    by_id = {record["unit_id"]: record for record in records}
    for record in records:
        for id_field, context_field in (
            ("previous_chunk_id", "previous_context"),
            ("next_chunk_id", "next_context"),
        ):
            context_id = record.pop(id_field)
            if context_id is None:
                continue
            context = by_id.get(str(context_id))
            if context is None:
                raise ValidationError(
                    f"{id_field} referencia un chunk inexistente: {context_id}"
                )
            if context["document_uri"] != record["document_uri"]:
                raise ValidationError(f"{id_field} debe pertenecer al mismo documento")
            record[context_field] = _context_record(context, record)
    return records


def sample_records(
    records: list[dict[str, Any]],
    sample_size: int,
    seed: int,
    strategy: str,
) -> list[dict[str, Any]]:
    if strategy not in ALLOWED_STRATEGIES:
        raise ValidationError(f"Estrategia de muestreo inválida: {strategy}")
    if sample_size < 1:
        raise ValidationError("El tamaño de muestra debe ser mayor que cero")
    if sample_size > len(records):
        raise ValidationError(
            f"El tamaño solicitado ({sample_size}) supera las {len(records)} unidades disponibles"
        )
    rng = random.Random(seed)
    if strategy == "random":
        selected = rng.sample(records, sample_size)
    else:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in records:
            stratum = f"{record['document_uri']}||{record['length_bin']}"
            groups[stratum].append(record)
        keys = sorted(groups)
        rng.shuffle(keys)
        for key in keys:
            rng.shuffle(groups[key])
        selected = []
        while len(selected) < sample_size:
            made_progress = False
            for key in keys:
                if groups[key] and len(selected) < sample_size:
                    record = groups[key].pop()
                    record = dict(record)
                    record["sampling_stratum"] = key
                    selected.append(record)
                    made_progress = True
            if not made_progress:
                break
            rng.shuffle(keys)
        rng.shuffle(selected)
    if strategy == "random":
        selected = [dict(record, sampling_stratum="random") for record in selected]
    if len(selected) != sample_size:
        raise ValidationError("No fue posible completar el tamaño de muestra solicitado")
    return selected


def normalize_strata(raw: Any, default: list[str]) -> list[str]:
    if raw is None:
        return list(default)
    if not isinstance(raw, list):
        raise ValidationError("strata debe ser una lista")
    fields: list[str] = []
    for value in raw:
        field = _limited_text(value, "strata", 40)
        if field not in STRATIFICATION_FIELDS:
            raise ValidationError(f"Dimensión de estratificación inválida: {field}")
        if field not in fields:
            fields.append(field)
    if not fields:
        raise ValidationError("Selecciona al menos una dimensión de estratificación")
    return fields


def _stratum_values(record: dict[str, Any], fields: list[str]) -> dict[str, str]:
    return {field: _sampling_value(record.get(field)) for field in fields}


def _stratum_id(values: dict[str, str]) -> str:
    encoded = json.dumps(values, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return "stratum_" + sha256_text(encoded)[:16]


def evaluation_inclusion(
    resolution_status: str | None, quality_flags: list[str]
) -> tuple[bool | None, list[str]]:
    """Derive evaluation-denominator eligibility from the human decision."""
    if resolution_status is None:
        return None, []
    reasons: list[str] = []
    if resolution_status == "unresolved":
        reasons.append("unresolved")
    reasons.extend(
        flag for flag in QUALITY_FLAGS
        if flag in EVALUATION_EXCLUSION_FLAGS and flag in quality_flags
    )
    return not reasons, reasons


def sample_with_design(
    records: list[dict[str, Any]],
    sample_size: int,
    seed: int,
    strategy: str,
    strata: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Select primary sampling units and return their auditable design table."""
    if strategy not in ALLOWED_STRATEGIES:
        raise ValidationError(f"Estrategia de muestreo inválida: {strategy}")
    if sample_size < 1:
        raise ValidationError("El tamaño de muestra debe ser mayor que cero")
    if sample_size > len(records):
        raise ValidationError(
            f"El tamaño solicitado ({sample_size}) supera las {len(records)} unidades disponibles"
        )
    if strategy == "stratified" and not strata:
        raise ValidationError("El muestreo estratificado requiere al menos una dimensión")
    rng = random.Random(seed)
    if strategy == "random":
        probability = sample_size / len(records)
        selected = []
        for record in rng.sample(records, sample_size):
            selected.append(dict(
                record,
                sampling_stratum_id="srs",
                inclusion_probability=probability,
                selection_weight=1 / probability,
            ))
        return selected, [{
            "stratum_id": "srs",
            "values": {},
            "population_units": len(records),
            "sampled_units": sample_size,
            "inclusion_probability": probability,
        }]

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    values_by_id: dict[str, dict[str, str]] = {}
    for record in records:
        values = _stratum_values(record, strata)
        identifier = _stratum_id(values)
        groups[identifier].append(record)
        values_by_id[identifier] = values
    counts = {identifier: len(group) for identifier, group in groups.items()}
    total = len(records)
    ideal = {identifier: count * sample_size / total for identifier, count in counts.items()}
    quotas = {identifier: min(counts[identifier], math.floor(value))
              for identifier, value in ideal.items()}
    remaining = sample_size - sum(quotas.values())
    order = sorted(
        groups,
        key=lambda identifier: (
            -(ideal[identifier] - quotas[identifier]),
            json.dumps(values_by_id[identifier], sort_keys=True, ensure_ascii=False),
        ),
    )
    for identifier in order:
        if remaining == 0:
            break
        if quotas[identifier] < counts[identifier]:
            quotas[identifier] += 1
            remaining -= 1
    if remaining:
        raise ValidationError("No fue posible asignar todas las unidades de la muestra")

    selected: list[dict[str, Any]] = []
    design: list[dict[str, Any]] = []
    for identifier in sorted(groups):
        population = counts[identifier]
        sampled = quotas[identifier]
        probability = sampled / population
        design.append({
            "stratum_id": identifier,
            "values": values_by_id[identifier],
            "population_units": population,
            "sampled_units": sampled,
            "inclusion_probability": probability,
        })
        if sampled == 0:
            continue
        for record in rng.sample(groups[identifier], sampled):
            selected.append(dict(
                record,
                sampling_stratum_id=identifier,
                inclusion_probability=probability,
                selection_weight=1 / probability,
            ))
    rng.shuffle(selected)
    return selected, design


class ValidationService:
    """State and persistence layer for the local annotation application."""

    def __init__(
        self,
        source_path: Path,
        codebook_path: Path,
        output_dir: Path,
        timezone_name: str = DEFAULT_TIMEZONE,
        party_alignment: PartyAlignment | None = None,
    ) -> None:
        self.source_path = source_path.resolve()
        self.codebook_path = codebook_path.resolve()
        self.output_dir = output_dir.resolve()
        self.timezone_name = timezone_name
        try:
            self.party_alignment = party_alignment or load_party_alignment(
                Path(__file__).resolve().parents[2] / ".env"
            )
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        self.codebook = load_codebook(self.codebook_path)
        paths = (
            sorted(self.source_path.glob("ley_*/coding_chunks_long.parquet"))
            if self.source_path.is_dir()
            else [self.source_path]
        )
        if not paths:
            raise ValidationError("No se encontraron corpus en ley_*/coding_chunks_long.parquet")
        self.records: list[dict[str, Any]] = []
        self.sources: list[dict[str, Any]] = []
        self.sampling_metadata_by_unit: dict[str, dict[str, str]] = {}
        for path in paths:
            records = load_corpus_records(path)
            bill_number = str(records[0]["bill_number"])
            law_number = LAW_BY_BILL.get(bill_number, bill_number)
            for record in records:
                record["law_number"] = law_number
                private_metadata = record.pop("_sampling_metadata")
                party = private_metadata["party"]
                actor_type = private_metadata["actor_type"]
                if actor_type in {"Ejecutivo", "Autoridad de la cámara"}:
                    alignment = "No aplica"
                elif party in {"Sin dato", "No aplica"}:
                    alignment = party
                else:
                    alignment = self.party_alignment.classify(party)
                self.sampling_metadata_by_unit[str(record["unit_id"])] = {
                    "law_number": law_number,
                    "chamber": private_metadata["chamber"],
                    "party": party,
                    "alignment": alignment,
                    "gender": private_metadata["gender"],
                    "actor_type": actor_type,
                    "document_uri": str(record["document_uri"]),
                    "length_bin": str(record["length_bin"]),
                }
            self.records.extend(records)
            self.sources.append(
                {
                    "law_number": law_number,
                    "label": law_label(law_number),
                    "bill_number": bill_number,
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "available_units": len(records),
                    "available_blocks": len(records),
                    "available_interventions": len(
                        {
                            (record["document_uri"], record["utterance_id"])
                            for record in records
                        }
                    ),
                }
            )
        if len({record["unit_id"] for record in self.records}) != len(self.records):
            raise ValidationError("Hay unit_id duplicados entre los corpus de las leyes")
        if len({source["law_number"] for source in self.sources}) != len(self.sources):
            raise ValidationError("Hay más de un corpus para la misma ley")
        first_record = self.records[0]
        self.chunk_schema_version = str(first_record["chunk_schema_version"])
        self.bill_number = self.sources[0]["bill_number"] if len(self.sources) == 1 else None
        self.min_words = int(first_record["minimum_words"])
        self.short_paragraph_words = int(first_record["short_paragraph_words"])
        self.target_block_words = int(first_record["target_block_words"])
        self.max_block_words = int(first_record["max_block_words"])
        for field in ("chunk_schema_version", "minimum_words", "short_paragraph_words",
                      "target_block_words", "max_block_words"):
            if any(record[field] != first_record[field] for record in self.records):
                raise ValidationError(f"Los corpus de las leyes difieren en {field}")
        self.records_by_id = {
            str(record["unit_id"]): record for record in self.records
        }
        self.utterances = self._build_utterance_units()
        self.source_sha256 = self._source_fingerprint(self.sources)
        self.codebook_sha256 = sha256_file(self.codebook_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def concept_ids(self) -> set[str]:
        return {str(concept["id"]) for concept in self.codebook["concepts"]}

    @staticmethod
    def _source_fingerprint(sources: list[dict[str, Any]]) -> str:
        if len(sources) == 1:
            return sources[0]["sha256"]
        return sha256_text(json.dumps(sources, sort_keys=True, ensure_ascii=False))

    def _build_utterance_units(self) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
        for record in self.records:
            grouped[
                (
                    str(record["law_number"]),
                    str(record["document_uri"]),
                    str(record["utterance_id"]),
                )
            ].append(record)
        units: list[dict[str, Any]] = []
        for (law_number, document_uri, utterance_id), blocks in grouped.items():
            blocks.sort(key=lambda record: int(record["document_chunk_order"]))
            metadata_rows = [
                self.sampling_metadata_by_unit[str(block["unit_id"])] for block in blocks
            ]
            stable_fields = (
                "chamber", "party", "alignment", "gender", "actor_type", "document_uri"
            )
            for field in stable_fields:
                if len({metadata[field] for metadata in metadata_rows}) != 1:
                    raise ValidationError(
                        f"{field} cambia dentro de la intervención {utterance_id}"
                    )
            n_words = int(blocks[0]["source_utterance_n_words"])
            units.append(
                {
                    "unit_id": f"{law_number}||{document_uri}||{utterance_id}",
                    "utterance_id": utterance_id,
                    "law_number": law_number,
                    "chamber": metadata_rows[0]["chamber"],
                    "party": metadata_rows[0]["party"],
                    "alignment": metadata_rows[0]["alignment"],
                    "gender": metadata_rows[0]["gender"],
                    "actor_type": metadata_rows[0]["actor_type"],
                    "document_uri": document_uri,
                    "length_bin": _utterance_length_bin(n_words),
                    "n_words": n_words,
                    "unit_ids": [str(block["unit_id"]) for block in blocks],
                }
            )
        units.sort(key=lambda unit: (unit["law_number"], unit["document_uri"], unit["unit_id"]))
        return units

    def sampling_metadata(self, unit_id: str) -> dict[str, str]:
        """Return category metadata for diagnostic filtering, without identity fields."""
        return dict(self.sampling_metadata_by_unit.get(unit_id, {}))

    def block_sampling_units(self, law_number: str = "all") -> list[dict[str, Any]]:
        """Return block-level primary units using the app's stratification metadata."""
        return [
            {
                **record,
                **self.sampling_metadata_by_unit[str(record["unit_id"])],
            }
            for record in self.records
            if law_number == "all" or record["law_number"] == law_number
        ]

    def config(self) -> dict[str, Any]:
        by_document: dict[str, int] = defaultdict(int)
        by_length: dict[str, int] = defaultdict(int)
        for record in self.records:
            by_document[record["document_uri"]] += 1
            by_length[record["length_bin"]] += 1
        return {
            "schema_version": SCHEMA_VERSION,
            "bill_number": self.bill_number,
            "laws": self.sources,
            "corpus": {
                "path": str(self.source_path),
                "sha256": self.source_sha256,
                "chunk_schema_version": self.chunk_schema_version,
                "unit_of_analysis": "paragraph_block",
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
                "available_units": len(self.records),
                "available_paragraph_blocks": len(self.records),
                "source_interventions": len(self.utterances),
                "by_document": dict(sorted(by_document.items())),
                "by_length_bin": dict(sorted(by_length.items())),
            },
            "codebook": self.codebook,
            "quality_flags": [
                {"id": flag_id, "label": label}
                for flag_id, label in QUALITY_FLAGS.items()
            ],
            "stratification": {
                "fields": [
                    {"id": field, "label": label}
                    for field, label in STRATIFICATION_FIELDS.items()
                ],
                "sampling_units": [
                    {"id": "utterance", "label": "Intervenciones completas"},
                    {"id": "block", "label": "Bloques de párrafos"},
                ],
            },
            "sessions": self.list_sessions(),
            "defaults": {
                "sample_size": 40,
                "seed": 20260824,
                "strategy": "stratified",
                "sampling_unit": "block",
                "strata": DEFAULT_EVALUATION_STRATA,
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
            },
        }

    def _session_path(self, session_id: str) -> Path:
        if not SESSION_ID_RE.fullmatch(session_id):
            raise ValidationError("Identificador de sesión inválido")
        return self.output_dir / f"{session_id}.json"

    def _load_session(self, session_id: str) -> dict[str, Any]:
        path = self._session_path(session_id)
        if not path.exists():
            raise FileNotFoundError(f"No existe la sesión {session_id}")
        with path.open(encoding="utf-8") as handle:
            session = json.load(handle)
        if session.get("session_id") != session_id:
            raise ValidationError("El archivo de sesión tiene un identificador inconsistente")
        return session

    def _save_session(self, session: dict[str, Any]) -> None:
        timestamps = timestamp_pair(self.timezone_name)
        session["updated_at_utc"] = timestamps["utc"]
        session["updated_at_local"] = timestamps["local"]
        atomic_write_json(self._session_path(session["session_id"]), session)

    @staticmethod
    def _summary(session: dict[str, Any]) -> dict[str, Any]:
        items = session.get("items", [])
        completed = sum(item.get("status") == "completed" for item in items)
        unresolved = sum(
            item.get("status") == "completed"
            and item.get("resolution_status") == "unresolved"
            for item in items
        )
        evaluation_excluded = sum(
            item.get("status") == "completed"
            and evaluation_inclusion(
                item.get("resolution_status") or (
                    "resolved" if item.get("decision") in ALLOWED_DECISIONS else None
                ),
                item.get("quality_flags", []),
            )[0] is False
            for item in items
        )
        next_pending = next(
            (index for index, item in enumerate(items) if item.get("status") != "completed"),
            None,
        )
        law_number = session.get("law_number") or LAW_BY_BILL.get(
            session.get("bill_number"), session.get("bill_number") or "all"
        )
        return {
            "session_id": session["session_id"],
            "coder_id": session.get("coder_id", ""),
            "created_at_utc": session.get("created_at_utc"),
            "updated_at_utc": session.get("updated_at_utc"),
            "sample_size": len(items),
            "completed": completed,
            "resolved": completed - unresolved,
            "unresolved": unresolved,
            "evaluation_excluded": evaluation_excluded,
            "pending": len(items) - completed,
            "next_pending_index": next_pending,
            "codebook_version": session.get("codebook", {}).get("version"),
            "sampling_strategy": session.get("sampling", {}).get("strategy"),
            "sampling_seed": session.get("sampling", {}).get("seed"),
            "sampling_unit": session.get("sampling", {}).get("sampling_unit", "block"),
            "selected_primary_units": session.get("sampling", {}).get(
                "selected_primary_units", len(items)
            ),
            "law_number": law_number,
            "law_label": law_label(law_number),
        }

    def list_sessions(self) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for path in sorted(self.output_dir.glob("validation_*.json"), reverse=True):
            try:
                with path.open(encoding="utf-8") as handle:
                    session = json.load(handle)
                summaries.append(self._summary(session))
            except (OSError, json.JSONDecodeError, KeyError, TypeError):
                continue
        return summaries

    def create_session(self, payload: dict[str, Any]) -> dict[str, Any]:
        sample_size = _integer(payload.get("sample_size", 40), "sample_size")
        seed = _integer(payload.get("seed", 20260824), "seed")
        strategy = _limited_text(payload.get("strategy", "stratified"), "strategy", 30)
        sampling_unit = _limited_text(
            payload.get("sampling_unit", "block"), "sampling_unit", 30
        )
        if sampling_unit not in ALLOWED_SAMPLING_UNITS:
            raise ValidationError("sampling_unit debe ser block o utterance")
        coder_id = _limited_text(payload.get("coder_id", ""), "coder_id", 120)
        law_number = _limited_text(payload.get("law_number", "all"), "law_number", 30)
        if law_number != "all" and law_number not in {
            source["law_number"] for source in self.sources
        }:
            raise ValidationError("Selecciona una ley disponible o todas las leyes")
        sources = [source for source in self.sources
                   if law_number == "all" or source["law_number"] == law_number]
        eligible_blocks = [
            record for record in self.records
            if law_number == "all" or record["law_number"] == law_number
        ]
        if sampling_unit == "utterance":
            eligible_primary = [
                unit for unit in self.utterances
                if law_number == "all" or unit["law_number"] == law_number
            ]
            default_strata = DEFAULT_EVALUATION_STRATA
        else:
            eligible_primary = self.block_sampling_units(law_number)
            default_strata = DEFAULT_EVALUATION_STRATA
        strata = normalize_strata(payload.get("strata"), default_strata) if (
            strategy == "stratified"
        ) else []
        selected_primary, design = sample_with_design(
            eligible_primary, sample_size, seed, strategy, strata
        )
        selected: list[dict[str, Any]] = []
        for primary in selected_primary:
            unit_ids = primary.get("unit_ids", [primary["unit_id"]])
            for unit_id in unit_ids:
                selected.append(
                    {
                        **self.records_by_id[str(unit_id)],
                        "sampling_stratum_id": primary["sampling_stratum_id"],
                        "inclusion_probability": primary["inclusion_probability"],
                        "selection_weight": primary["selection_weight"],
                    }
                )
        timestamps = timestamp_pair(self.timezone_name)
        session_id = f"validation_{_session_timestamp()}_{uuid.uuid4().hex[:8]}"
        items: list[dict[str, Any]] = []
        for index, record in enumerate(selected):
            items.append(
                {
                    "sample_index": index,
                    "law_number": record["law_number"],
                    "bill_number": record["bill_number"],
                    "chunk_id": record["chunk_id"],
                    "unit_id": record["unit_id"],
                    "unit_kind": record["unit_kind"],
                    "utterance_id": record["utterance_id"],
                    "document_uri": record["document_uri"],
                    "utterance_order": record["utterance_order"],
                    "paragraph_number": record["paragraph_number"],
                    "paragraph_start": record["paragraph_start"],
                    "paragraph_end": record["paragraph_end"],
                    "block_paragraph_count": record["block_paragraph_count"],
                    "paragraph_count": record["paragraph_count"],
                    "source_start_char": record["source_start_char"],
                    "source_end_char": record["source_end_char"],
                    "source_segments": record["source_segments"],
                    "source_utterance_n_words": record["source_utterance_n_words"],
                    "date": record["date"],
                    "constitutional_stage": record["constitutional_stage"],
                    "regulatory_stage": record["regulatory_stage"],
                    "title": record["title"],
                    "length_bin": record["length_bin"],
                    "n_words": record["n_words"],
                    "sampling_stratum_id": record["sampling_stratum_id"],
                    "inclusion_probability": record["inclusion_probability"],
                    "selection_weight": record["selection_weight"],
                    "target_text": record["content"],
                    "target_text_sha256": record["content_sha256"],
                    "previous_context": record["previous_context"],
                    "next_context": record["next_context"],
                    "status": "pending",
                    "resolution_status": None,
                    "decision": None,
                    "annotations": [],
                    "general_comment": None,
                    "quality_flags": [],
                    "evaluation_included": None,
                    "evaluation_exclusion_reasons": [],
                    "revision": 0,
                    "first_opened_at_utc": None,
                    "first_opened_at_local": None,
                    "last_opened_at_utc": None,
                    "last_opened_at_local": None,
                    "completed_at_utc": None,
                    "completed_at_local": None,
                    "updated_at_utc": None,
                    "updated_at_local": None,
                }
            )
        session = {
            "schema_version": SCHEMA_VERSION,
            "session_id": session_id,
            "timezone": self.timezone_name,
            "coder_id": coder_id,
            "law_number": law_number,
            "law_numbers": [source["law_number"] for source in sources],
            "bill_number": sources[0]["bill_number"] if len(sources) == 1 else None,
            "created_at_utc": timestamps["utc"],
            "created_at_local": timestamps["local"],
            "updated_at_utc": timestamps["utc"],
            "updated_at_local": timestamps["local"],
            "source": {
                "path": sources[0]["path"] if len(sources) == 1 else str(self.source_path),
                "sha256": self._source_fingerprint(sources),
                "files": sources,
                "chunk_schema_version": self.chunk_schema_version,
                "unit_of_analysis": "paragraph_block",
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
                "available_units": len(eligible_primary),
                "available_blocks": len(eligible_blocks),
                "available_interventions": len({
                    (record["law_number"], record["document_uri"], record["utterance_id"])
                    for record in eligible_blocks
                }),
            },
            "codebook": {
                **self.codebook,
                "source_path": str(self.codebook_path),
                "sha256": self.codebook_sha256,
            },
            "sampling": {
                "law_number": law_number,
                "strategy": strategy,
                "seed": seed,
                "requested_size": sample_size,
                "actual_size": len(items),
                "sampling_unit": sampling_unit,
                "selected_primary_units": len(selected_primary),
                "selected_blocks": len(items),
                "unit_of_analysis": "paragraph_block",
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
                "strata": strata,
                "party_alignment": self.party_alignment.snapshot(),
                "strata_table": [
                    {
                        "stratum_id": row["stratum_id"],
                        "values": row["values"],
                        "population_units": row["population_units"],
                        "sampled_units": row["sampled_units"],
                        "inclusion_probability": row["inclusion_probability"],
                    }
                    for row in design
                ],
            },
            "items": items,
        }
        atomic_write_json(self._session_path(session_id), session)
        return self._summary(session)

    def session_summary(self, session_id: str) -> dict[str, Any]:
        return self._summary(self._load_session(session_id))

    def open_item(self, session_id: str, index: int) -> dict[str, Any]:
        session = self._load_session(session_id)
        items = session["items"]
        if index < 0 or index >= len(items):
            raise ValidationError("Índice de unidad fuera de rango")
        item = items[index]
        timestamps = timestamp_pair(self.timezone_name)
        if item.get("first_opened_at_utc") is None:
            item["first_opened_at_utc"] = timestamps["utc"]
            item["first_opened_at_local"] = timestamps["local"]
        item["last_opened_at_utc"] = timestamps["utc"]
        item["last_opened_at_local"] = timestamps["local"]
        self._save_session(session)
        resolution_status = item.get("resolution_status") or (
            "resolved" if item.get("decision") in ALLOWED_DECISIONS else None
        )
        evaluation_included, evaluation_exclusion_reasons = evaluation_inclusion(
            resolution_status, item.get("quality_flags", [])
        )
        public_item = {
            "law_label": law_label(item.get("law_number") or LAW_BY_BILL.get(
                session.get("bill_number"), session.get("bill_number") or "all"
            )),
            "sample_index": item["sample_index"],
            "chunk_id": item.get(
                "chunk_id", item.get("unit_id", item.get("utterance_id", ""))
            ),
            "unit_id": item.get("unit_id", item.get("utterance_id", "")),
            "unit_kind": item.get("unit_kind", "intervention"),
            "date": item["date"],
            "constitutional_stage": item["constitutional_stage"],
            "title": item["title"],
            "n_words": item["n_words"],
            "paragraph_number": item.get("paragraph_number"),
            "paragraph_start": item.get("paragraph_start", item.get("paragraph_number")),
            "paragraph_end": item.get("paragraph_end", item.get("paragraph_number")),
            "block_paragraph_count": item.get("block_paragraph_count", 1),
            "paragraph_count": item.get("paragraph_count"),
            "target_text": item["target_text"],
            "previous_text": (
                item["previous_context"]["content"] if item.get("previous_context") else ""
            ),
            "has_previous": item.get("previous_context") is not None,
            "previous_same_utterance": bool(
                (item.get("previous_context") or {}).get("same_utterance")
            ),
            "next_text": (
                item["next_context"]["content"] if item.get("next_context") else ""
            ),
            "has_next": item.get("next_context") is not None,
            "next_same_utterance": bool(
                (item.get("next_context") or {}).get("same_utterance")
            ),
            "status": item["status"],
            "resolution_status": resolution_status,
            "decision": item["decision"],
            "annotations": item["annotations"],
            "general_comment": item.get("general_comment"),
            "quality_flags": item.get("quality_flags", []),
            "evaluation_included": item.get(
                "evaluation_included", evaluation_included
            ),
            "evaluation_exclusion_reasons": item.get(
                "evaluation_exclusion_reasons", evaluation_exclusion_reasons
            ),
            "revision": item["revision"],
        }
        return {
            "session": self._summary(session),
            "item": public_item,
            "codebook": session["codebook"],
        }

    @staticmethod
    def _normalize_annotation(
        raw: Any,
        target_text: str,
        concept_ids: set[str],
        existing: dict[str, dict[str, Any]],
        timezone_name: str = DEFAULT_TIMEZONE,
    ) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValidationError("Cada declaración debe ser un objeto")
        annotation_id = _limited_text(raw.get("annotation_id", ""), "annotation_id", 100)
        if not annotation_id:
            annotation_id = uuid.uuid4().hex
        if not re.fullmatch(r"[A-Za-z0-9_-]+", annotation_id):
            raise ValidationError("annotation_id contiene caracteres inválidos")
        start_char = _integer(raw.get("start_char"), "start_char")
        end_char = _integer(raw.get("end_char"), "end_char")
        if start_char < 0 or end_char <= start_char or end_char > len(target_text):
            raise ValidationError("El span está fuera de los límites del bloque")
        evidence_text = _text(raw.get("evidence_text"))
        exact = target_text[start_char:end_char]
        if evidence_text != exact:
            raise ValidationError("La evidencia no coincide exactamente con el span seleccionado")
        if not evidence_text.strip():
            raise ValidationError("La evidencia seleccionada está vacía")

        stance = _limited_text(raw.get("stance"), "stance", 30)
        if stance not in ALLOWED_STANCES:
            raise ValidationError("La orientación debe ser support u oppose")
        concept_status = _limited_text(raw.get("concept_status"), "concept_status", 30)
        if concept_status not in ALLOWED_CONCEPT_STATUSES:
            raise ValidationError("concept_status debe ser in_codebook o review")
        concept_id_value = raw.get("concept_id")
        concept_id = None if concept_id_value is None else _limited_text(
            concept_id_value, "concept_id", 120
        )
        proposed_concept = _limited_text(raw.get("proposed_concept", ""), "proposed_concept", 300)
        note = _limited_text(raw.get("note", ""), "note", 2000)
        if concept_status == "in_codebook":
            if concept_id not in concept_ids:
                raise ValidationError(f"Concepto ausente del libro de códigos: {concept_id}")
            if proposed_concept:
                raise ValidationError(
                    "Un concepto del libro no puede incluir proposed_concept"
                )
        else:
            if concept_id is not None:
                raise ValidationError("review requiere concept_id null")
            concept_id = None
            if not proposed_concept:
                raise ValidationError("review requiere una justificación propuesta")

        timestamps = timestamp_pair(timezone_name)
        old = existing.get(annotation_id, {})
        return {
            "annotation_id": annotation_id,
            "span": {
                "start_char": start_char,
                "end_char": end_char,
                "text": evidence_text,
                "sha256": sha256_text(evidence_text),
            },
            "concept_status": concept_status,
            "concept_id": concept_id,
            "proposed_concept": proposed_concept or None,
            "stance": stance,
            "note": note or None,
            "selected_at_client": _limited_text(
                raw.get("selected_at_client", ""), "selected_at_client", 80
            )
            or None,
            "created_at_utc": old.get("created_at_utc", timestamps["utc"]),
            "created_at_local": old.get("created_at_local", timestamps["local"]),
            "updated_at_utc": timestamps["utc"],
            "updated_at_local": timestamps["local"],
        }

    def save_item(self, session_id: str, index: int, payload: dict[str, Any]) -> dict[str, Any]:
        session = self._load_session(session_id)
        items = session["items"]
        if index < 0 or index >= len(items):
            raise ValidationError("Índice de unidad fuera de rango")
        item = items[index]
        resolution_status = _limited_text(
            payload.get("resolution_status", "resolved"), "resolution_status", 30
        )
        if resolution_status not in ALLOWED_RESOLUTION_STATUSES:
            raise ValidationError("resolution_status debe ser resolved o unresolved")
        raw_decision = payload.get("decision")
        decision = (
            None if raw_decision is None
            else _limited_text(raw_decision, "decision", 30)
        )
        if resolution_status == "resolved" and decision not in ALLOWED_DECISIONS:
            raise ValidationError("Debe registrar declaraciones o marcar que no existen")
        if resolution_status == "unresolved" and decision not in {None, ""}:
            raise ValidationError("Un bloque irresoluble no puede registrar una decisión")
        raw_annotations = payload.get("annotations", [])
        if not isinstance(raw_annotations, list):
            raise ValidationError("annotations debe ser una lista")
        if len(raw_annotations) > 50:
            raise ValidationError("Un bloque no puede superar 50 declaraciones")
        if resolution_status == "unresolved" and raw_annotations:
            raise ValidationError("Un bloque irresoluble no puede incluir spans")
        if decision == "no_statements" and raw_annotations:
            raise ValidationError("Un bloque sin declaraciones no puede incluir spans")
        if decision == "statements" and not raw_annotations:
            raise ValidationError("Agregue al menos una declaración")

        raw_quality_flags = payload.get("quality_flags", [])
        if not isinstance(raw_quality_flags, list):
            raise ValidationError("quality_flags debe ser una lista")
        if len(raw_quality_flags) > len(QUALITY_FLAGS):
            raise ValidationError("Se recibieron demasiadas flags de calidad")
        quality_flags: list[str] = []
        for raw_flag in raw_quality_flags:
            flag = _limited_text(raw_flag, "quality_flags", 60)
            if flag not in QUALITY_FLAGS:
                raise ValidationError(f"Flag de calidad inválida: {flag}")
            if flag in quality_flags:
                raise ValidationError(f"Flag de calidad duplicada: {flag}")
            quality_flags.append(flag)
        general_comment = _limited_text(
            payload.get("general_comment", ""), "general_comment", 4000
        )
        if (
            resolution_status == "unresolved"
            and not UNRESOLVED_REASON_FLAGS.intersection(quality_flags)
        ):
            raise ValidationError(
                "Un caso irresoluble requiere una flag que explique la falta de evidencia"
            )

        concept_ids = {
            str(concept["id"]) for concept in session.get("codebook", {}).get("concepts", [])
        }
        existing = {
            annotation.get("annotation_id", ""): annotation for annotation in item["annotations"]
        }
        normalized = [
            self._normalize_annotation(raw, item["target_text"], concept_ids, existing,
                                       timezone_name=self.timezone_name)
            for raw in raw_annotations
        ]
        ids = [annotation["annotation_id"] for annotation in normalized]
        if len(ids) != len(set(ids)):
            raise ValidationError("annotation_id duplicado dentro de la intervención")
        semantic_ids = [
            (
                annotation["span"]["start_char"],
                annotation["span"]["end_char"],
                annotation["concept_id"],
                " ".join((annotation["proposed_concept"] or "").casefold().split()),
            )
            for annotation in normalized
        ]
        if len(semantic_ids) != len(set(semantic_ids)):
            raise ValidationError("La misma evidencia y concepto están duplicados")

        timestamps = timestamp_pair(self.timezone_name)
        evaluation_included, evaluation_exclusion_reasons = evaluation_inclusion(
            resolution_status, quality_flags
        )
        item["resolution_status"] = resolution_status
        item["decision"] = decision or None
        item["annotations"] = normalized
        item["general_comment"] = general_comment or None
        item["quality_flags"] = quality_flags
        item["evaluation_included"] = evaluation_included
        item["evaluation_exclusion_reasons"] = evaluation_exclusion_reasons
        item["status"] = "completed"
        item["revision"] = int(item.get("revision", 0)) + 1
        item["updated_at_utc"] = timestamps["utc"]
        item["updated_at_local"] = timestamps["local"]
        item["completed_at_utc"] = item.get("completed_at_utc") or timestamps["utc"]
        item["completed_at_local"] = item.get("completed_at_local") or timestamps["local"]
        self._save_session(session)
        return self.open_item(session_id, index)


class ValidationRequestHandler(BaseHTTPRequestHandler):
    """HTTP routes for the dependency-free local web application."""

    service: ValidationService
    static_dir: Path

    def log_message(self, format_string: str, *args: Any) -> None:
        print(f"[validation-ui] {self.address_string()} {format_string % args}")

    def _send_security_headers(self) -> None:
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; connect-src 'self'; base-uri 'none'; "
            "form-action 'self'; frame-ancestors 'none'",
        )
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _send_static(self, filename: str) -> None:
        allowed = {"index.html", "app.js", "styles.css", "llm.html", "llm.js", "llm.css"}
        if filename not in allowed:
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        path = self.static_dir / filename
        if not path.exists():
            self.send_error(HTTPStatus.NOT_FOUND.value)
            return
        data = path.read_bytes()
        content_type, _ = mimetypes.guess_type(path.name)
        self.send_response(HTTPStatus.OK.value)
        self.send_header("Content-Type", f"{content_type or 'application/octet-stream'}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(data)

    def _read_payload(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValidationError("Content-Length inválido") from exc
        if length < 1 or length > MAX_REQUEST_BYTES:
            raise ValidationError("Tamaño de request inválido")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("El cuerpo debe ser JSON válido") from exc
        if not isinstance(payload, dict):
            raise ValidationError("El cuerpo JSON debe ser un objeto")
        return payload

    def _route_parts(self) -> list[str]:
        return [part for part in urlparse(self.path).path.split("/") if part]

    @staticmethod
    def _item_index(value: str) -> int:
        try:
            return int(value)
        except ValueError as exc:
            raise ValidationError("El índice de unidad debe ser un número entero") from exc

    def _handle_error(self, exc: Exception) -> None:
        if isinstance(exc, ValidationError):
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        elif isinstance(exc, FileNotFoundError):
            self._send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        else:
            self.log_error("Unexpected error: %r", exc)
            self._send_json({"error": "Error interno de la aplicación"}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_GET(self) -> None:  # noqa: N802
        try:
            parts = self._route_parts()
            if not parts:
                self._send_static("index.html")
                return
            if len(parts) == 1 and parts[0] in {"app.js", "styles.css", "llm.html", "llm.js", "llm.css"}:
                self._send_static(parts[0])
                return
            if parts == ["api", "config"]:
                self._send_json(self.service.config())
                return
            if parts == ["api", "llm", "runs"]:
                self._send_json(self.service.llm_review.list_runs())
                return
            if len(parts) == 5 and parts[:3] == ["api", "llm", "runs"] and parts[4] == "items":
                self._send_json(self.service.llm_review.list_items(parts[3]))
                return
            if len(parts) == 6 and parts[:3] == ["api", "llm", "runs"] and parts[4] == "items":
                self._send_json(self.service.llm_review.open_item(parts[3], self._item_index(parts[5])))
                return
            if len(parts) == 3 and parts[:2] == ["api", "sessions"]:
                self._send_json(self.service.session_summary(parts[2]))
                return
            if (
                len(parts) == 5
                and parts[:2] == ["api", "sessions"]
                and parts[3] == "items"
            ):
                self._send_json(self.service.open_item(parts[2], self._item_index(parts[4])))
                return
            self._send_json({"error": "Ruta inexistente"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._handle_error(exc)

    def do_POST(self) -> None:  # noqa: N802
        try:
            parts = self._route_parts()
            if parts == ["api", "sessions"]:
                summary = self.service.create_session(self._read_payload())
                self._send_json(summary, HTTPStatus.CREATED)
                return
            self._send_json({"error": "Ruta inexistente"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._handle_error(exc)

    def do_PUT(self) -> None:  # noqa: N802
        try:
            parts = self._route_parts()
            if len(parts) == 7 and parts[:3] == ["api", "llm", "runs"] and parts[4] == "items" and parts[6] == "review":
                self._send_json(self.service.llm_review.save_review(
                    parts[3], self._item_index(parts[5]), self._read_payload()))
                return
            if (
                len(parts) == 5
                and parts[:2] == ["api", "sessions"]
                and parts[3] == "items"
            ):
                result = self.service.save_item(
                    parts[2], self._item_index(parts[4]), self._read_payload()
                )
                self._send_json(result)
                return
            self._send_json({"error": "Ruta inexistente"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._handle_error(exc)


def create_server(
    service: ValidationService,
    static_dir: Path,
    host: str,
    port: int,
) -> ThreadingHTTPServer:
    class BoundHandler(ValidationRequestHandler):
        pass

    BoundHandler.service = service
    BoundHandler.static_dir = static_dir.resolve()
    return ThreadingHTTPServer((host, port), BoundHandler)
