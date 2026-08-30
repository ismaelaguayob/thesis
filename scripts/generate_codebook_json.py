#!/usr/bin/env python3
"""Generate the machine-readable codebook JSON from the editable XLSX."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.codebook_workbook import (  # noqa: E402
    CodebookWorkbookError,
    read_codebook_workbook,
    write_codebook_json,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el JSON del libro de códigos a partir de su XLSX editable."
    )
    parser.add_argument(
        "--workbook",
        type=Path,
        default=PROJECT_ROOT / "config" / "codebook_v0.2.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "config" / "codebook_v0.2.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Comprueba que el JSON existente coincida, sin escribir archivos.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.check:
            expected = read_codebook_workbook(args.workbook)
            if not args.output.exists():
                print(f"Falta el JSON generado: {args.output}", file=sys.stderr)
                return 1
            actual = json.loads(args.output.read_text(encoding="utf-8"))
            if actual != expected:
                print(
                    "El JSON está desactualizado. Ejecuta scripts/generate_codebook_json.py.",
                    file=sys.stderr,
                )
                return 1
            print(f"JSON sincronizado con {args.workbook}")
            return 0
        changed = write_codebook_json(args.workbook, args.output)
    except (CodebookWorkbookError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    action = "Generado" if changed else "Sin cambios"
    print(f"{action}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
