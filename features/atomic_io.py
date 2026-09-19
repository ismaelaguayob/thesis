"""Atomic writers for derived analysis artifacts."""
from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any


def atomic_write(path: Path, writer: Callable[[Path], Any]) -> None:
    """Write a complete temporary artifact and publish it with ``os.replace``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.stem}-", suffix=path.suffix, dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        writer(temporary)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def atomic_write_parquet(dataframe: Any, path: Path) -> None:
    """Persist a DataFrame as a complete Parquet file before publication."""
    atomic_write(path, lambda temporary: dataframe.to_parquet(temporary, index=False))


def atomic_write_csv(dataframe: Any, path: Path) -> None:
    """Persist a DataFrame as a complete CSV file before publication."""
    atomic_write(path, lambda temporary: dataframe.to_csv(temporary, index=False))


def atomic_write_text(text: str, path: Path) -> None:
    """Persist text with an atomic publish step."""
    atomic_write(path, lambda temporary: temporary.write_text(text, encoding="utf-8"))


def atomic_write_bytes(payload: bytes, path: Path) -> None:
    """Persist bytes with an atomic publish step."""
    atomic_write(path, lambda temporary: temporary.write_bytes(payload))
