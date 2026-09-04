"""Segmentación de intervenciones con procedencia de cada fragmento.

Las reglas de selección y los límites de longitud se definen en proc.qmd.
Estas funciones conservan los offsets y hashes del texto original.
"""

import hashlib
import json
import re
from typing import Any


WORD_RE = re.compile(r"[^\W_]+(?:[-’'][^\W_]+)*", re.UNICODE)
PARAGRAPH_RE = re.compile(r"[^\r\n]+")
SENTENCE_BOUNDARY_RE = re.compile(r"[.!?…]+[\"»”’\)\]]*(?:\s+|$)")


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def paragraph_fragments(text: str) -> list[dict[str, Any]]:
    """Separa por saltos de línea y conserva offsets sobre la intervención."""
    paragraphs = []
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
                "n_words": count_words(content),
            }
        )
    return paragraphs


def source_slice(
    source: dict[str, Any], start_char: int, end_char: int
) -> dict[str, Any]:
    """Recorta un fragmento sin perder los offsets de la intervención original."""
    raw = source["content"][start_char:end_char]
    content = raw.strip()
    left_trim = len(raw) - len(raw.lstrip())
    absolute_start = source["source_start_char"] + start_char + left_trim
    return {
        "content": content,
        "source_start_char": absolute_start,
        "source_end_char": absolute_start + len(content),
        "n_words": count_words(content),
    }


def split_fragment_by_words(
    fragment: dict[str, Any], max_block_words: int
) -> list[dict[str, Any]]:
    """Aplica el corte de respaldo a una oración que por sí sola excede el máximo."""
    words = list(WORD_RE.finditer(fragment["content"]))
    if len(words) <= max_block_words:
        return [fragment]
    result = []
    start_char = 0
    word_index = max_block_words
    while word_index < len(words):
        cut = words[word_index].start()
        while cut > start_char and not fragment["content"][cut - 1].isspace():
            cut -= 1
        if cut <= start_char:
            cut = words[word_index].start()
        piece = source_slice(fragment, start_char, cut)
        if piece["content"]:
            result.append(piece)
        start_char = cut
        word_index += max_block_words
    piece = source_slice(fragment, start_char, len(fragment["content"]))
    if piece["content"]:
        result.append(piece)
    return result


def sentence_fragments(paragraph: dict[str, Any]) -> list[dict[str, Any]]:
    """Divide un párrafo por puntuación terminal, conservando la puntuación."""
    fragments = []
    start_char = 0
    for match in SENTENCE_BOUNDARY_RE.finditer(paragraph["content"]):
        piece = source_slice(paragraph, start_char, match.end())
        if piece["content"]:
            fragments.append(piece)
        start_char = match.end()
    if start_char < len(paragraph["content"]):
        piece = source_slice(paragraph, start_char, len(paragraph["content"]))
        if piece["content"]:
            fragments.append(piece)
    return fragments or [dict(paragraph)]


def split_paragraph(
    paragraph: dict[str, Any],
    target_block_words: int,
    max_block_words: int,
) -> list[dict[str, Any]]:
    """Produce segmentos legibles de un párrafo bajo un máximo estricto."""
    if paragraph["n_words"] <= max_block_words:
        segments = [dict(paragraph)]
    else:
        atoms = []
        for sentence in sentence_fragments(paragraph):
            atoms.extend(split_fragment_by_words(sentence, max_block_words))
        grouped_atoms = []
        current = []
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
        for atom_group in grouped_atoms:
            relative_start = (
                atom_group[0]["source_start_char"] - paragraph["source_start_char"]
            )
            relative_end = (
                atom_group[-1]["source_end_char"] - paragraph["source_start_char"]
            )
            segments.append(source_slice(paragraph, relative_start, relative_end))

    segment_count = len(segments)
    for segment_number, segment in enumerate(segments, start=1):
        segment["paragraph_number"] = paragraph["paragraph_number"]
        segment["paragraph_segment_number"] = segment_number
        segment["paragraph_segment_count"] = segment_count
    return segments


def merge_segments(segments: list[dict[str, Any]]) -> dict[str, Any]:
    """Une segmentos contiguos y registra su procedencia en una forma serializable."""
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
    source_segments = [
        {
            "paragraph_number": segment["paragraph_number"],
            "paragraph_segment_number": segment["paragraph_segment_number"],
            "paragraph_segment_count": segment["paragraph_segment_count"],
            "source_start_char": segment["source_start_char"],
            "source_end_char": segment["source_end_char"],
            "n_words": segment["n_words"],
            "content_sha256": text_sha256(segment["content"]),
        }
        for segment in segments
    ]
    return {
        "_members": segments,
        "content": content,
        "content_sha256": text_sha256(content),
        "source_start_char": segments[0]["source_start_char"],
        "source_end_char": segments[-1]["source_end_char"],
        "paragraph_start": segments[0]["paragraph_number"],
        "paragraph_end": segments[-1]["paragraph_number"],
        "block_paragraph_count": len(paragraph_numbers),
        "n_words": sum(segment["n_words"] for segment in segments),
        "source_segments_json": json.dumps(
            source_segments,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
    }


def paragraph_blocks(
    paragraphs: list[dict[str, Any]],
    short_paragraph_words: int,
    target_block_words: int,
    max_block_words: int,
) -> list[dict[str, Any]]:
    """Agrupa una intervención con un máximo flexible para absorber bloques breves.

    El corte inicial usa ``max_block_words``. Después se unen los bloques de
    menos de ``short_paragraph_words`` al vecino más corto, aunque se supere ese
    máximo. Solo una intervención completa puede quedar bajo el umbral breve.
    """
    segments = []
    for paragraph in paragraphs:
        segments.extend(
            split_paragraph(paragraph, target_block_words, max_block_words)
        )

    block_members = []
    pending = []

    def pending_words() -> int:
        return sum(segment["n_words"] for segment in pending)

    def flush_pending() -> None:
        nonlocal pending
        if pending:
            block_members.append(pending)
            pending = []

    for segment in segments:
        segment_words = segment["n_words"]
        if pending:
            if segment_words >= short_paragraph_words:
                total = pending_words()
                if total < target_block_words and total + segment_words <= max_block_words:
                    pending.append(segment)
                    flush_pending()
                else:
                    flush_pending()
                    block_members.append([segment])
            else:
                if pending_words() + segment_words > max_block_words:
                    flush_pending()
                pending.append(segment)
                if pending_words() >= target_block_words:
                    flush_pending()
            continue

        if segment_words >= short_paragraph_words:
            block_members.append([segment])
            continue

        if block_members:
            previous_words = sum(member["n_words"] for member in block_members[-1])
            if previous_words + segment_words <= max_block_words:
                block_members[-1].append(segment)
                continue

        pending.append(segment)
        if pending_words() >= target_block_words:
            flush_pending()

    flush_pending()

    # Absorber los restos antes de filtrar por longitud conserva también los
    # cierres de pocas palabras. Cada llamada contiene una sola intervención.
    index = 0
    while len(block_members) > 1 and index < len(block_members):
        words = sum(member["n_words"] for member in block_members[index])
        if words >= short_paragraph_words:
            index += 1
            continue
        previous_words = (
            sum(member["n_words"] for member in block_members[index - 1])
            if index > 0 else float("inf")
        )
        next_words = (
            sum(member["n_words"] for member in block_members[index + 1])
            if index + 1 < len(block_members) else float("inf")
        )
        if previous_words <= next_words:
            block_members[index - 1].extend(block_members.pop(index))
            index -= 1
        else:
            members = block_members.pop(index)
            block_members[index][:0] = members

    return [merge_segments(members) for members in block_members]


def segment_token(segment: dict[str, Any]) -> str:
    token = f"p{segment['paragraph_number']:04d}"
    if segment["paragraph_segment_count"] > 1:
        token += f"s{segment['paragraph_segment_number']:03d}"
    return token


def length_bin(words: int) -> str:
    if words <= 75:
        return "short_000_075"
    if words <= 500:
        return "medium_076_500"
    return "long_501_plus"
