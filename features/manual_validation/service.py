"""Local manual-validation application for discourse coding.

The module keeps sampling, validation and persistence independent from the web
interface.  It intentionally exposes no speaker names, speaker identifiers,
party labels or gender attributes to the browser.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
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


SCHEMA_VERSION = "manual-validation-2.4.0"
CHUNK_SCHEMA_VERSION = "coding-chunks-1.0.0"
LAW_BY_BILL = {"15480-13": "21735", "14588-13": "21419", "15625-13": "21538"}
DEFAULT_TIMEZONE = "America/Santiago"
SESSION_ID_RE = re.compile(r"^validation_\d{8}T\d{12}Z_[0-9a-f]{8}$")
ALLOWED_STANCES = {"support", "oppose"}
ALLOWED_CONCEPT_STATUSES = {"in_codebook", "review"}
ALLOWED_DECISIONS = {"statements", "no_statements"}
ALLOWED_STRATEGIES = {"stratified", "random"}
QUALITY_FLAGS = {
    "vote": "Voto",
    "procedural": "Procedimental",
    "too_short": "Texto demasiado breve",
    "truncated": "Texto truncado",
    "insufficient_context": "Contexto insuficiente",
    "segmentation_problem": "Problema de segmentación",
    "other": "Otro problema",
}
MAX_REQUEST_BYTES = 2_000_000


def law_label(law_number: str) -> str:
    if law_number == "all":
        return "Todas las leyes"
    if law_number.isdigit():
        return f"Ley {int(law_number):,}".replace(",", ".")
    return f"Boletín {law_number}"


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
        if not concept_id or not label or not definition:
            raise ValidationError(f"El concepto {position} requiere id, label y definition")
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
    if chunk_schema_version != CHUNK_SCHEMA_VERSION:
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
    if dataframe["n_words"].gt(max_block_words).any():
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
    for utterance_id, group in dataframe.groupby("utterance_id", sort=False):
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


class ValidationService:
    """State and persistence layer for the local annotation application."""

    def __init__(
        self,
        source_path: Path,
        codebook_path: Path,
        output_dir: Path,
        timezone_name: str = DEFAULT_TIMEZONE,
    ) -> None:
        self.source_path = source_path.resolve()
        self.codebook_path = codebook_path.resolve()
        self.output_dir = output_dir.resolve()
        self.timezone_name = timezone_name
        self.codebook = load_codebook(self.codebook_path)
        paths = (
            sorted(self.source_path.glob("ley_*/coding_chunks_long.parquet"))
            if self.source_path.is_dir()
            else [self.source_path]
        )
        if not paths:
            raise ValidationError("No se encontraron corpus en ley_*/coding_chunks_long.parquet")
        self.records = []
        self.sources = []
        for path in paths:
            records = load_corpus_records(path)
            bill_number = str(records[0]["bill_number"])
            law_number = LAW_BY_BILL.get(bill_number, bill_number)
            for record in records:
                record["law_number"] = law_number
            self.records.extend(records)
            self.sources.append({
                "law_number": law_number,
                "label": law_label(law_number),
                "bill_number": bill_number,
                "path": str(path),
                "sha256": sha256_file(path),
                "available_units": len(records),
            })
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
                "source_interventions": len(
                    {record["utterance_id"] for record in self.records}
                ),
                "by_document": dict(sorted(by_document.items())),
                "by_length_bin": dict(sorted(by_length.items())),
            },
            "codebook": self.codebook,
            "quality_flags": [
                {"id": flag_id, "label": label}
                for flag_id, label in QUALITY_FLAGS.items()
            ],
            "sessions": self.list_sessions(),
            "defaults": {
                "sample_size": 40,
                "seed": 20260824,
                "strategy": "stratified",
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
            "pending": len(items) - completed,
            "next_pending_index": next_pending,
            "codebook_version": session.get("codebook", {}).get("version"),
            "sampling_strategy": session.get("sampling", {}).get("strategy"),
            "sampling_seed": session.get("sampling", {}).get("seed"),
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
        try:
            sample_size = int(payload.get("sample_size", 40))
            seed = int(payload.get("seed", 20260824))
        except (TypeError, ValueError) as exc:
            raise ValidationError("sample_size y seed deben ser números enteros") from exc
        strategy = _limited_text(payload.get("strategy", "stratified"), "strategy", 30)
        coder_id = _limited_text(payload.get("coder_id", ""), "coder_id", 120)
        law_number = _limited_text(payload.get("law_number", "all"), "law_number", 30)
        if law_number != "all" and law_number not in {
            source["law_number"] for source in self.sources
        }:
            raise ValidationError("Selecciona una ley disponible o todas las leyes")
        sources = [source for source in self.sources
                   if law_number == "all" or source["law_number"] == law_number]
        eligible = [record for record in self.records
                    if law_number == "all" or record["law_number"] == law_number]
        selected = sample_records(eligible, sample_size, seed, strategy)
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
                    "title": record["title"],
                    "length_bin": record["length_bin"],
                    "n_words": record["n_words"],
                    "sampling_stratum": record["sampling_stratum"],
                    "target_text": record["content"],
                    "target_text_sha256": record["content_sha256"],
                    "previous_context": record["previous_context"],
                    "next_context": record["next_context"],
                    "status": "pending",
                    "decision": None,
                    "annotations": [],
                    "general_comment": None,
                    "quality_flags": [],
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
                "available_units": len(eligible),
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
                "unit_of_analysis": "paragraph_block",
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
                "strata": ["document_uri", "length_bin"] if strategy == "stratified" else [],
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
            "decision": item["decision"],
            "annotations": item["annotations"],
            "general_comment": item.get("general_comment"),
            "quality_flags": item.get("quality_flags", []),
            "revision": item["revision"],
        }
        return {
            "session": self._summary(session),
            "item": public_item,
            "codebook": session["codebook"],
        }

    def _normalize_annotation(
        self,
        raw: Any,
        target_text: str,
        concept_ids: set[str],
        existing: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValidationError("Cada declaración debe ser un objeto")
        annotation_id = _limited_text(raw.get("annotation_id", ""), "annotation_id", 100)
        if not annotation_id:
            annotation_id = uuid.uuid4().hex
        if not re.fullmatch(r"[A-Za-z0-9_-]+", annotation_id):
            raise ValidationError("annotation_id contiene caracteres inválidos")
        try:
            start_char = int(raw.get("start_char"))
            end_char = int(raw.get("end_char"))
        except (TypeError, ValueError) as exc:
            raise ValidationError("Los offsets del span deben ser números enteros") from exc
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
            proposed_concept = ""
        else:
            concept_id = None

        timestamps = timestamp_pair(self.timezone_name)
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
        decision = _limited_text(payload.get("decision"), "decision", 30)
        if decision not in ALLOWED_DECISIONS:
            raise ValidationError("Debe registrar declaraciones o marcar que no existen")
        raw_annotations = payload.get("annotations", [])
        if not isinstance(raw_annotations, list):
            raise ValidationError("annotations debe ser una lista")
        if len(raw_annotations) > 50:
            raise ValidationError("Un bloque no puede superar 50 declaraciones")
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
            if flag not in quality_flags:
                quality_flags.append(flag)
        general_comment = _limited_text(
            payload.get("general_comment", ""), "general_comment", 4000
        )

        concept_ids = {
            str(concept["id"]) for concept in session.get("codebook", {}).get("concepts", [])
        }
        existing = {
            annotation.get("annotation_id", ""): annotation for annotation in item["annotations"]
        }
        normalized = [
            self._normalize_annotation(raw, item["target_text"], concept_ids, existing)
            for raw in raw_annotations
        ]
        ids = [annotation["annotation_id"] for annotation in normalized]
        if len(ids) != len(set(ids)):
            raise ValidationError("annotation_id duplicado dentro de la intervención")

        timestamps = timestamp_pair(self.timezone_name)
        item["decision"] = decision
        item["annotations"] = normalized
        item["general_comment"] = general_comment or None
        item["quality_flags"] = quality_flags
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
        allowed = {"index.html", "app.js", "styles.css"}
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
            if len(parts) == 1 and parts[0] in {"app.js", "styles.css"}:
                self._send_static(parts[0])
                return
            if parts == ["api", "config"]:
                self._send_json(self.service.config())
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
