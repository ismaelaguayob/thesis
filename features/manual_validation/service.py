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


SCHEMA_VERSION = "manual-validation-2.2.0"
DEFAULT_TIMEZONE = "America/Santiago"
DEFAULT_MIN_WORDS = 5
DEFAULT_SHORT_PARAGRAPH_WORDS = 50
DEFAULT_TARGET_BLOCK_WORDS = 100
DEFAULT_MAX_BLOCK_WORDS = 150
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


def _length_bin(words: int) -> str:
    if words <= 75:
        return "short_000_075"
    if words <= 500:
        return "medium_076_500"
    return "long_501_plus"


WORD_RE = re.compile(r"[^\W_]+(?:[-’'][^\W_]+)*", re.UNICODE)
PARAGRAPH_RE = re.compile(r"[^\r\n]+")
SENTENCE_BOUNDARY_RE = re.compile(r"[.!?…]+[\"»”’\)\]]*(?:\s+|$)")


def _count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def _paragraphs(text: str) -> list[dict[str, Any]]:
    """Split an intervention on transcript line breaks and preserve source offsets."""
    paragraphs: list[dict[str, Any]] = []
    for match in PARAGRAPH_RE.finditer(text):
        raw = match.group(0)
        content = raw.strip()
        if not content:
            continue
        left_trim = len(raw) - len(raw.lstrip())
        start_char = match.start() + left_trim
        paragraphs.append(
            {
                "content": content,
                "source_start_char": start_char,
                "source_end_char": start_char + len(content),
                "n_words": _count_words(content),
            }
        )
    return paragraphs


def _source_slice(
    source: dict[str, Any], start_char: int, end_char: int
) -> dict[str, Any]:
    """Slice a source fragment while retaining absolute offsets."""
    raw = source["content"][start_char:end_char]
    content = raw.strip()
    left_trim = len(raw) - len(raw.lstrip())
    absolute_start = source["source_start_char"] + start_char + left_trim
    return {
        "content": content,
        "source_start_char": absolute_start,
        "source_end_char": absolute_start + len(content),
        "n_words": _count_words(content),
    }


def _split_fragment_by_words(
    fragment: dict[str, Any], max_block_words: int
) -> list[dict[str, Any]]:
    """Split an overlong sentence at whitespace without losing punctuation."""
    words = list(WORD_RE.finditer(fragment["content"]))
    if len(words) <= max_block_words:
        return [fragment]
    result: list[dict[str, Any]] = []
    start_char = 0
    word_index = max_block_words
    while word_index < len(words):
        cut = words[word_index].start()
        while cut > start_char and not fragment["content"][cut - 1].isspace():
            cut -= 1
        if cut <= start_char:
            cut = words[word_index].start()
        piece = _source_slice(fragment, start_char, cut)
        if piece["content"]:
            result.append(piece)
        start_char = cut
        word_index += max_block_words
    piece = _source_slice(fragment, start_char, len(fragment["content"]))
    if piece["content"]:
        result.append(piece)
    return result


def _sentence_fragments(paragraph: dict[str, Any]) -> list[dict[str, Any]]:
    """Return sentence-like fragments with offsets relative to the source text."""
    fragments: list[dict[str, Any]] = []
    start_char = 0
    for match in SENTENCE_BOUNDARY_RE.finditer(paragraph["content"]):
        piece = _source_slice(paragraph, start_char, match.end())
        if piece["content"]:
            fragments.append(piece)
        start_char = match.end()
    if start_char < len(paragraph["content"]):
        piece = _source_slice(paragraph, start_char, len(paragraph["content"]))
        if piece["content"]:
            fragments.append(piece)
    return fragments or [dict(paragraph)]


def _split_paragraph(
    paragraph: dict[str, Any],
    target_block_words: int,
    max_block_words: int,
) -> list[dict[str, Any]]:
    """Split one paragraph into sentence-aware segments under a strict ceiling."""
    if paragraph["n_words"] <= max_block_words:
        segments = [dict(paragraph)]
    else:
        atoms: list[dict[str, Any]] = []
        for sentence in _sentence_fragments(paragraph):
            atoms.extend(_split_fragment_by_words(sentence, max_block_words))
        grouped_atoms: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        current_words = 0
        for atom in atoms:
            if current and (
                current_words >= target_block_words
                or current_words + atom["n_words"] > max_block_words
            ):
                grouped_atoms.append(current)
                current = []
                current_words = 0
            current.append(atom)
            current_words += atom["n_words"]
        if current:
            grouped_atoms.append(current)

        segments = []
        for atoms_group in grouped_atoms:
            relative_start = (
                atoms_group[0]["source_start_char"] - paragraph["source_start_char"]
            )
            relative_end = (
                atoms_group[-1]["source_end_char"] - paragraph["source_start_char"]
            )
            segments.append(_source_slice(paragraph, relative_start, relative_end))

    segment_count = len(segments)
    for segment_number, segment in enumerate(segments, start=1):
        segment["paragraph_number"] = paragraph["paragraph_number"]
        segment["paragraph_segment_number"] = segment_number
        segment["paragraph_segment_count"] = segment_count
    return segments


def _merge_segments(segments: list[dict[str, Any]]) -> dict[str, Any]:
    content_parts = [segments[0]["content"]]
    for previous, current in zip(segments, segments[1:], strict=False):
        separator = (
            " "
            if previous["paragraph_number"] == current["paragraph_number"]
            else "\n\n"
        )
        content_parts.extend([separator, current["content"]])
    content = "".join(content_parts)
    paragraph_numbers = {segment["paragraph_number"] for segment in segments}
    return {
        "_members": segments,
        "content": content,
        "content_sha256": sha256_text(content),
        "source_start_char": segments[0]["source_start_char"],
        "source_end_char": segments[-1]["source_end_char"],
        "paragraph_start": segments[0]["paragraph_number"],
        "paragraph_end": segments[-1]["paragraph_number"],
        "block_paragraph_count": len(paragraph_numbers),
        "n_words": sum(segment["n_words"] for segment in segments),
        "source_segments": [
            {
                "paragraph_number": segment["paragraph_number"],
                "paragraph_segment_number": segment["paragraph_segment_number"],
                "paragraph_segment_count": segment["paragraph_segment_count"],
                "source_start_char": segment["source_start_char"],
                "source_end_char": segment["source_end_char"],
                "n_words": segment["n_words"],
                "content_sha256": sha256_text(segment["content"]),
            }
            for segment in segments
        ],
    }


def _paragraph_blocks(
    paragraphs: list[dict[str, Any]],
    short_paragraph_words: int,
    target_block_words: int,
    max_block_words: int,
) -> list[dict[str, Any]]:
    """Build readable blocks while enforcing an absolute word ceiling.

    Short paragraphs preferentially attach to the preceding block.  This keeps
    enumerations and brief qualifications with the proposition they elaborate.
    At the start of an utterance, short paragraphs accumulate forward toward the
    target.  A paragraph above the ceiling is split on sentence boundaries (and,
    only when necessary, on a word boundary).
    """
    segments: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        segments.extend(
            _split_paragraph(paragraph, target_block_words, max_block_words)
        )

    block_members: list[list[dict[str, Any]]] = []
    pending: list[dict[str, Any]] = []

    def pending_words() -> int:
        return sum(segment["n_words"] for segment in pending)

    def flush_pending() -> None:
        nonlocal pending
        if pending:
            block_members.append(pending)
            pending = []

    for segment in segments:
        segment_words = segment["n_words"]
        if segment_words >= short_paragraph_words:
            if pending:
                total = pending_words()
                if total < target_block_words and total + segment_words <= max_block_words:
                    pending.append(segment)
                    flush_pending()
                else:
                    flush_pending()
                    block_members.append([segment])
            else:
                block_members.append([segment])
            continue

        if block_members:
            previous_words = sum(
                member["n_words"] for member in block_members[-1]
            )
            if previous_words + segment_words <= max_block_words:
                block_members[-1].append(segment)
                continue

        if pending and pending_words() + segment_words > max_block_words:
            flush_pending()
        pending.append(segment)
        if pending_words() >= target_block_words:
            flush_pending()

    flush_pending()
    blocks = [_merge_segments(members) for members in block_members]
    if any(block["n_words"] > max_block_words for block in blocks):
        raise ValidationError(
            f"La segmentación produjo un bloque sobre {max_block_words} palabras"
        )
    return blocks


def _segment_token(segment: dict[str, Any]) -> str:
    token = f"p{segment['paragraph_number']:04d}"
    if segment["paragraph_segment_count"] > 1:
        token += f"s{segment['paragraph_segment_number']:03d}"
    return token


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
    bill_number: str,
    min_words: int = DEFAULT_MIN_WORDS,
    short_paragraph_words: int = DEFAULT_SHORT_PARAGRAPH_WORDS,
    target_block_words: int = DEFAULT_TARGET_BLOCK_WORDS,
    max_block_words: int = DEFAULT_MAX_BLOCK_WORDS,
) -> list[dict[str, Any]]:
    """Build paragraph blocks and attach adjacent blocks as context."""
    if min_words < 1:
        raise ValidationError("El mínimo de palabras debe ser mayor que cero")
    if short_paragraph_words < 1:
        raise ValidationError("El umbral de párrafo breve debe ser mayor que cero")
    if target_block_words < short_paragraph_words:
        raise ValidationError(
            "El objetivo del bloque debe ser igual o mayor que el umbral de párrafo breve"
        )
    if max_block_words < target_block_words:
        raise ValidationError(
            "El máximo del bloque debe ser igual o mayor que su extensión objetivo"
        )
    if not source_path.exists():
        raise FileNotFoundError(f"No existe el corpus: {source_path}")
    dataframe = pd.read_parquet(source_path)
    required = {
        "utterance_id",
        "document_uri",
        "utterance_order",
        "kind",
        "content",
    }
    missing = sorted(required.difference(dataframe.columns))
    if missing:
        raise ValidationError(f"Faltan columnas requeridas en el corpus: {', '.join(missing)}")

    mask = dataframe["kind"].eq("participation")
    if "bill_number" in dataframe.columns:
        mask &= dataframe["bill_number"].astype(str).eq(bill_number)
    if "analysis_included" in dataframe.columns:
        analysis_included = dataframe["analysis_included"].fillna(False).astype(bool)
        if "section_name" in dataframe.columns:
            section_names = dataframe["section_name"].fillna("").astype(str).str.casefold()
            is_voting_section = section_names.isin({"votacion", "votación"})
            analysis_included |= is_voting_section
        mask &= analysis_included
    if "is_preamble" in dataframe.columns:
        mask &= ~dataframe["is_preamble"].fillna(False).astype(bool)
    filtered = dataframe.loc[mask].copy()
    filtered["content"] = filtered["content"].fillna("").astype(str)
    filtered = filtered.loc[filtered["content"].str.strip().ne("")].copy()
    if filtered.empty:
        raise ValidationError("El filtro no produjo intervenciones codificables")
    if filtered["utterance_id"].duplicated().any():
        duplicates = filtered.loc[filtered["utterance_id"].duplicated(), "utterance_id"].tolist()
        raise ValidationError(f"utterance_id duplicado en el corpus: {duplicates[:3]}")

    filtered["_document_sort"] = filtered["document_uri"].fillna("").astype(str)
    filtered["_order_sort"] = pd.to_numeric(filtered["utterance_order"], errors="coerce")
    filtered["_order_sort"] = filtered["_order_sort"].fillna(math.inf)
    filtered = filtered.sort_values(["_document_sort", "_order_sort"], kind="stable")

    records: list[dict[str, Any]] = []
    for _, group in filtered.groupby("_document_sort", sort=False, dropna=False):
        document_blocks: list[dict[str, Any]] = []
        for _, row in group.iterrows():
            content = _text(row.get("content"))
            n_words_value = _clean_scalar(row.get("n_words"))
            try:
                intervention_n_words = (
                    int(n_words_value) if n_words_value is not None else _count_words(content)
                )
            except (TypeError, ValueError):
                intervention_n_words = _count_words(content)
            paragraphs = _paragraphs(content)
            utterance_id = _text(row.get("utterance_id"))
            for paragraph_index, paragraph in enumerate(paragraphs, start=1):
                paragraph["paragraph_number"] = paragraph_index
            blocks = _paragraph_blocks(
                paragraphs,
                short_paragraph_words=short_paragraph_words,
                target_block_words=target_block_words,
                max_block_words=max_block_words,
            )
            for block in blocks:
                first_segment = block["_members"][0]
                last_segment = block["_members"][-1]
                start_token = _segment_token(first_segment)
                end_token = _segment_token(last_segment)
                unit_suffix = (
                    start_token
                    if start_token == end_token
                    else f"{start_token}-{end_token}"
                )
                document_blocks.append(
                    {
                        "unit_id": f"{utterance_id}::{unit_suffix}",
                        "unit_kind": "paragraph_block",
                        "utterance_id": utterance_id,
                        "document_uri": _text(row.get("document_uri")),
                        "utterance_order": _clean_scalar(row.get("utterance_order")),
                        "paragraph_number": block["paragraph_start"],
                        "paragraph_start": block["paragraph_start"],
                        "paragraph_end": block["paragraph_end"],
                        "block_paragraph_count": block["block_paragraph_count"],
                        "paragraph_count": len(paragraphs),
                        "source_start_char": block["source_start_char"],
                        "source_end_char": block["source_end_char"],
                        "source_segments": block["source_segments"],
                        "source_utterance_n_words": intervention_n_words,
                        "date": _text(row.get("date")),
                        "constitutional_stage": _text(row.get("constitutional_stage")),
                        "title": _text(row.get("title")),
                        "content": block["content"],
                        "content_sha256": block["content_sha256"],
                        "n_words": block["n_words"],
                        "length_bin": _length_bin(block["n_words"]),
                        "previous_context": None,
                        "next_context": None,
                    }
                )
        for index, record in enumerate(document_blocks):
            if index > 0:
                record["previous_context"] = _context_record(
                    document_blocks[index - 1], record
                )
            if index + 1 < len(document_blocks):
                record["next_context"] = _context_record(
                    document_blocks[index + 1], record
                )
            if record["n_words"] >= min_words:
                records.append(record)
    if not records:
        raise ValidationError(
            f"El filtro no produjo bloques de al menos {min_words} palabras"
        )
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
        bill_number: str = "15480-13",
        timezone_name: str = DEFAULT_TIMEZONE,
        min_words: int = DEFAULT_MIN_WORDS,
        short_paragraph_words: int = DEFAULT_SHORT_PARAGRAPH_WORDS,
        target_block_words: int = DEFAULT_TARGET_BLOCK_WORDS,
        max_block_words: int = DEFAULT_MAX_BLOCK_WORDS,
    ) -> None:
        self.source_path = source_path.resolve()
        self.codebook_path = codebook_path.resolve()
        self.output_dir = output_dir.resolve()
        self.bill_number = bill_number
        self.timezone_name = timezone_name
        self.min_words = min_words
        self.short_paragraph_words = short_paragraph_words
        self.target_block_words = target_block_words
        self.max_block_words = max_block_words
        self.codebook = load_codebook(self.codebook_path)
        self.records = load_corpus_records(
            self.source_path,
            bill_number,
            min_words,
            short_paragraph_words,
            target_block_words,
            max_block_words,
        )
        self.source_sha256 = sha256_file(self.source_path)
        self.codebook_sha256 = sha256_file(self.codebook_path)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def concept_ids(self) -> set[str]:
        return {str(concept["id"]) for concept in self.codebook["concepts"]}

    def config(self) -> dict[str, Any]:
        by_document: dict[str, int] = defaultdict(int)
        by_length: dict[str, int] = defaultdict(int)
        for record in self.records:
            by_document[record["document_uri"]] += 1
            by_length[record["length_bin"]] += 1
        return {
            "schema_version": SCHEMA_VERSION,
            "bill_number": self.bill_number,
            "corpus": {
                "path": str(self.source_path),
                "sha256": self.source_sha256,
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
        selected = sample_records(self.records, sample_size, seed, strategy)
        timestamps = timestamp_pair(self.timezone_name)
        session_id = f"validation_{_session_timestamp()}_{uuid.uuid4().hex[:8]}"
        items: list[dict[str, Any]] = []
        for index, record in enumerate(selected):
            items.append(
                {
                    "sample_index": index,
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
            "bill_number": self.bill_number,
            "created_at_utc": timestamps["utc"],
            "created_at_local": timestamps["local"],
            "updated_at_utc": timestamps["utc"],
            "updated_at_local": timestamps["local"],
            "source": {
                "path": str(self.source_path),
                "sha256": self.source_sha256,
                "unit_of_analysis": "paragraph_block",
                "minimum_words": self.min_words,
                "short_paragraph_words": self.short_paragraph_words,
                "target_block_words": self.target_block_words,
                "max_block_words": self.max_block_words,
                "available_units": len(self.records),
            },
            "codebook": {
                **self.codebook,
                "source_path": str(self.codebook_path),
                "sha256": self.codebook_sha256,
            },
            "sampling": {
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
            "sample_index": item["sample_index"],
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
