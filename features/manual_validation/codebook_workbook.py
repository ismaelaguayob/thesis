"""Read the editable XLSX codebook and generate its canonical JSON derivative.

The XLSX reader uses only the Python standard library so the conversion command
does not add a spreadsheet-engine dependency to the thesis environment.
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import uuid
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONCEPT_ID_RE = re.compile(r"^[a-z0-9_]+$")
CRITERION_COLUMN_RE = re.compile(r"^(include|exclude)_(\d+)$")


class CodebookWorkbookError(ValueError):
    """Raised when the workbook cannot be converted without ambiguity."""


def _column_index(cell_reference: str) -> int:
    letters = "".join(character for character in cell_reference if character.isalpha())
    value = 0
    for character in letters.upper():
        value = value * 26 + ord(character) - ord("A") + 1
    return value - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return [
        "".join(node.text or "" for node in item.iter(f"{{{MAIN_NS}}}t"))
        for item in root.findall(f"{{{MAIN_NS}}}si")
    ]


def _sheet_paths(archive: zipfile.ZipFile) -> dict[str, str]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {
        relation.attrib["Id"]: relation.attrib["Target"]
        for relation in relationships.findall(f"{{{PACKAGE_REL_NS}}}Relationship")
    }
    result: dict[str, str] = {}
    for sheet in workbook.findall(f".//{{{MAIN_NS}}}sheet"):
        relationship_id = sheet.attrib[f"{{{OFFICE_REL_NS}}}id"]
        target = targets[relationship_id]
        path = (
            target.lstrip("/")
            if target.startswith("/")
            else posixpath.normpath(posixpath.join("xl", target))
        )
        result[sheet.attrib["name"]] = path
    return result


def _cell_value(cell: ET.Element, shared: list[str]) -> Any:
    cell_type = cell.attrib.get("t", "")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{{{MAIN_NS}}}t"))
    value_node = cell.find(f"{{{MAIN_NS}}}v")
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if cell_type == "s":
        try:
            return shared[int(raw)]
        except (IndexError, ValueError) as exc:
            raise CodebookWorkbookError("Índice inválido en sharedStrings.xml") from exc
    if cell_type == "b":
        return raw == "1"
    if cell_type in {"str", "e"}:
        return raw
    try:
        numeric = float(raw)
    except ValueError:
        return raw
    return int(numeric) if numeric.is_integer() else numeric


def _read_rows(
    archive: zipfile.ZipFile,
    path: str,
    shared: list[str],
) -> list[list[Any]]:
    root = ET.fromstring(archive.read(path))
    rows: list[list[Any]] = []
    for row in root.findall(f".//{{{MAIN_NS}}}sheetData/{{{MAIN_NS}}}row"):
        values: dict[int, Any] = {}
        for cell in row.findall(f"{{{MAIN_NS}}}c"):
            values[_column_index(cell.attrib.get("r", "A1"))] = _cell_value(cell, shared)
        if not values:
            continue
        width = max(values) + 1
        rendered = [values.get(index, "") for index in range(width)]
        if any(str(value).strip() for value in rendered):
            rows.append(rendered)
    return rows


def _header(value: Any) -> str:
    return re.sub(r"\s+", "_", str(value).strip().casefold())


def _records(rows: list[list[Any]], sheet_name: str) -> list[dict[str, Any]]:
    if not rows:
        raise CodebookWorkbookError(f"La hoja {sheet_name} está vacía")
    headers = [_header(value) for value in rows[0]]
    if not all(headers):
        raise CodebookWorkbookError(f"La hoja {sheet_name} contiene encabezados vacíos")
    if len(headers) != len(set(headers)):
        raise CodebookWorkbookError(f"La hoja {sheet_name} contiene encabezados duplicados")
    result: list[dict[str, Any]] = []
    for row in rows[1:]:
        padded = row + [""] * (len(headers) - len(row))
        record = dict(zip(headers, padded[: len(headers)], strict=True))
        if any(str(value).strip() for value in record.values()):
            result.append(record)
    return result


def _text(value: Any) -> str:
    return "" if value is None else str(value).strip()


def _order(value: Any, fallback: int) -> float:
    if value in (None, ""):
        return float(fallback)
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise CodebookWorkbookError(f"Orden inválido en la fila {fallback}: {value}") from exc


def read_codebook_workbook(path: Path) -> dict[str, Any]:
    """Return the JSON-shaped codebook represented by an XLSX workbook."""
    if not path.exists():
        raise FileNotFoundError(f"No existe el libro de códigos XLSX: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            shared = _shared_strings(archive)
            sheet_paths = _sheet_paths(archive)
            missing = sorted({"Metadatos", "Conceptos"}.difference(sheet_paths))
            if missing:
                raise CodebookWorkbookError(
                    f"Faltan hojas requeridas: {', '.join(missing)}"
                )
            metadata_rows = _records(
                _read_rows(archive, sheet_paths["Metadatos"], shared), "Metadatos"
            )
            concept_rows = _records(
                _read_rows(archive, sheet_paths["Conceptos"], shared), "Conceptos"
            )
    except zipfile.BadZipFile as exc:
        raise CodebookWorkbookError(f"El archivo no es un XLSX válido: {path}") from exc

    if not metadata_rows or not {"campo", "valor"}.issubset(metadata_rows[0]):
        raise CodebookWorkbookError("Metadatos requiere las columnas campo y valor")
    metadata = {
        _text(row.get("campo")): _text(row.get("valor")) for row in metadata_rows
    }
    required_metadata = {"schema_version", "version", "status", "title"}
    missing_metadata = sorted(
        field for field in required_metadata if not metadata.get(field)
    )
    if missing_metadata:
        raise CodebookWorkbookError(
            f"Faltan metadatos requeridos: {', '.join(missing_metadata)}"
        )

    required_columns = {"id", "label", "definition"}
    if not concept_rows or not required_columns.issubset(concept_rows[0]):
        raise CodebookWorkbookError(
            "Conceptos requiere las columnas id, label y definition"
        )
    criterion_columns = sorted(
        (
            (match.group(1), int(match.group(2)), column)
            for column in concept_rows[0]
            if (match := CRITERION_COLUMN_RE.fullmatch(column))
        ),
        key=lambda item: (item[0], item[1]),
    )
    ordered_rows = sorted(
        enumerate(concept_rows, start=2),
        key=lambda item: _order(item[1].get("orden"), item[0]),
    )
    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for spreadsheet_row, row in ordered_rows:
        concept_id = _text(row.get("id"))
        label = _text(row.get("label"))
        definition = _text(row.get("definition"))
        if not concept_id or not label or not definition:
            raise CodebookWorkbookError(
                f"La fila {spreadsheet_row} de Conceptos requiere id, label y definition"
            )
        if not CONCEPT_ID_RE.fullmatch(concept_id):
            raise CodebookWorkbookError(f"ID de concepto inválido: {concept_id}")
        if concept_id in seen:
            raise CodebookWorkbookError(f"ID de concepto duplicado: {concept_id}")
        criteria = {"include": [], "exclude": []}
        for criterion_type, _criterion_order, column in criterion_columns:
            criterion = _text(row.get(column))
            if criterion:
                criteria[criterion_type].append(criterion)
        concept: dict[str, Any] = {
            "id": concept_id,
            "label": label,
            "definition": definition,
            "include": criteria["include"],
            "exclude": criteria["exclude"],
        }
        for optional_field in ("family", "theoretical_basis", "orientation_anchor"):
            value = _text(row.get(optional_field))
            if value:
                concept[optional_field] = value
        concepts.append(concept)
        seen.add(concept_id)

    payload: dict[str, Any] = {
        "schema_version": metadata["schema_version"],
        "version": metadata["version"],
        "status": metadata["status"],
        "title": metadata["title"],
    }
    if metadata.get("description"):
        payload["description"] = metadata["description"]
    payload["concepts"] = concepts
    return payload


def write_codebook_json(workbook_path: Path, output_path: Path) -> bool:
    """Generate JSON atomically; return True only when the file changed."""
    payload = read_codebook_workbook(workbook_path)
    if output_path.exists():
        try:
            existing = json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = None
        if existing == payload:
            return False
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.{uuid.uuid4().hex}.tmp")
    with temporary.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, output_path)
    return True
