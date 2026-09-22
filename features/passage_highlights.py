"""Shared persistence for interpretation passages selected in the local UI."""

from __future__ import annotations

import re
import threading
from pathlib import Path

from features.atomic_io import atomic_write_text


_HIGHLIGHT_LOCK = threading.RLock()


def append_passage_highlight(
    path: Path,
    *,
    marker: str,
    title: str,
    text: str,
    metadata: str,
    note: str = "",
) -> dict[str, object]:
    """Append one numbered Markdown section unless its stable marker already exists."""
    with _HIGHLIGHT_LOCK:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        if marker in existing:
            return {
                "saved": False,
                "message": "Este pasaje ya estaba guardado.",
                "path": str(path),
            }

        numbers = [
            int(value) for value in re.findall(r"(?m)^##\s+(\d+)\.", existing)
        ]
        number = max(numbers, default=0) + 1
        section = f"## {number}. {title}\n\n{text.strip()}\n\n{metadata}\n"
        if note:
            section += f"\n**Nota interpretativa:** {note}\n"
        section += f"\n{marker}\n"
        # A hand-edited ledger may leave an empty heading as a placeholder. Remove
        # only that trailing placeholder when publishing the next complete entry.
        base = re.sub(r"(?:^|\n)##[ \t]*(?:\r?\n)*\Z", "", existing).rstrip()
        updated = base + ("\n\n" if base else "") + section
        atomic_write_text(updated, path)
        return {
            "saved": True,
            "message": "Pasaje guardado para la interpretación.",
            "path": str(path),
            "number": number,
        }
