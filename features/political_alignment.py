"""Shared political-alignment configuration for analysis and validation.

``PARTY_ALIGNMENT`` is a JSON object with two arrays, ``left`` and ``right``.
Parties absent from both arrays are classified as ``center``. Party names are
matched case-insensitively and without diacritics so that known BCN spelling
variants do not require duplicate configuration entries.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from dotenv import load_dotenv


PARTY_ALIGNMENT_ENV = "PARTY_ALIGNMENT"
ALIGNMENTS = ("izquierda", "derecha", "centro")


def normalize_party_name(value: Any) -> str:
    """Return the stable comparison key used for party names."""
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(character for character in text if not unicodedata.combining(character))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def _party_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{PARTY_ALIGNMENT_ENV}.{field} debe ser una lista JSON no vacía")
    parties: list[str] = []
    seen: set[str] = set()
    for position, party in enumerate(value):
        if not isinstance(party, str) or not party.strip():
            raise ValueError(
                f"{PARTY_ALIGNMENT_ENV}.{field}[{position}] debe ser un nombre de partido"
            )
        display_name = " ".join(party.split())
        normalized = normalize_party_name(display_name)
        if normalized in seen:
            raise ValueError(
                f"{PARTY_ALIGNMENT_ENV}.{field} contiene el partido duplicado {display_name!r}"
            )
        seen.add(normalized)
        parties.append(display_name)
    return tuple(parties)


@dataclass(frozen=True)
class PartyAlignment:
    """Immutable party grouping shared by every analytical procedure."""

    left: tuple[str, ...]
    right: tuple[str, ...]

    def __post_init__(self) -> None:
        left_keys = {normalize_party_name(party) for party in self.left}
        right_keys = {normalize_party_name(party) for party in self.right}
        overlap = left_keys.intersection(right_keys)
        if overlap:
            raise ValueError(
                f"{PARTY_ALIGNMENT_ENV} asigna partidos a izquierda y derecha a la vez: "
                + ", ".join(sorted(overlap))
            )

    @property
    def left_keys(self) -> frozenset[str]:
        return frozenset(normalize_party_name(party) for party in self.left)

    @property
    def right_keys(self) -> frozenset[str]:
        return frozenset(normalize_party_name(party) for party in self.right)

    def classify(self, party: Any) -> str:
        key = normalize_party_name(party)
        if key in self.left_keys:
            return "izquierda"
        if key in self.right_keys:
            return "derecha"
        return "centro"

    def snapshot(self) -> dict[str, Any]:
        definition = {
            "environment_variable": PARTY_ALIGNMENT_ENV,
            "left": list(self.left),
            "right": list(self.right),
            "center_rule": "partido no enumerado en left ni right",
        }
        encoded = json.dumps(
            definition, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return {
            **definition,
            "sha256": hashlib.sha256(encoded.encode("utf-8")).hexdigest(),
        }


def parse_party_alignment(raw: str) -> PartyAlignment:
    """Validate and parse the JSON value stored in ``PARTY_ALIGNMENT``."""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{PARTY_ALIGNMENT_ENV} debe contener JSON válido") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{PARTY_ALIGNMENT_ENV} debe ser un objeto JSON")
    unexpected = sorted(set(payload).difference({"left", "right"}))
    if unexpected:
        raise ValueError(
            f"{PARTY_ALIGNMENT_ENV} contiene claves no admitidas: {', '.join(unexpected)}"
        )
    return PartyAlignment(
        left=_party_list(payload.get("left"), "left"),
        right=_party_list(payload.get("right"), "right"),
    )


def load_party_alignment(
    env_path: Path | str = Path(".env"),
    environ: Mapping[str, str] | None = None,
) -> PartyAlignment:
    """Load ``PARTY_ALIGNMENT`` from the process environment or ``.env``."""
    if environ is None:
        load_dotenv(dotenv_path=env_path, override=False)
        values: Mapping[str, str] = os.environ
    else:
        values = environ
    raw = values.get(PARTY_ALIGNMENT_ENV, "").strip()
    if not raw:
        raise ValueError(
            f"Falta {PARTY_ALIGNMENT_ENV}; defínela en {Path(env_path)} o en el entorno"
        )
    return parse_party_alignment(raw)
