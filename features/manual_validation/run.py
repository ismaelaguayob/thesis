#!/usr/bin/env python3
"""Run the local manual-validation web application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from features.manual_validation.codebook_workbook import write_codebook_json  # noqa: E402
from features.manual_validation.service import (  # noqa: E402
    ValidationService,
    create_server,
)


def default_source() -> Path:
    return PROJECT_ROOT / "data" / "proc_data" / "coding_chunks_long.parquet"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interfaz local para muestreo y codificación manual de declaraciones."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=default_source(),
        help="Parquet long de chunks generado por proc.qmd.",
    )
    parser.add_argument(
        "--codebook-workbook",
        type=Path,
        default=PROJECT_ROOT / "data" / "codebook" / "codebook_v0.3.xlsx",
        help="XLSX editable que actúa como fuente del libro de códigos.",
    )
    parser.add_argument(
        "--codebook-json",
        "--codebook",
        dest="codebook_json",
        type=Path,
        default=PROJECT_ROOT / "data" / "codebook" / "codebook_v0.3.json",
        help="JSON derivado que consumirá la interfaz.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codebook_changed = write_codebook_json(args.codebook_workbook, args.codebook_json)
    service = ValidationService(
        source_path=args.source,
        codebook_path=args.codebook_json,
        output_dir=args.output_dir,
    )
    static_dir = Path(__file__).resolve().parent / "web"
    server = create_server(service, static_dir, args.host, args.port)
    print(f"Corpus: {service.source_path}")
    print(
        f"Bloques disponibles: {len(service.records)} "
        f"(párrafos breves < {service.short_paragraph_words} palabras; "
        f"objetivo {service.target_block_words}; máximo {service.max_block_words}; "
        f"mínimo residual {service.min_words})"
    )
    print(f"Libro editable: {args.codebook_workbook.resolve()}")
    print(
        f"JSON derivado: {service.codebook_path}"
        f" ({'actualizado' if codebook_changed else 'sin cambios'})"
    )
    print(f"Outputs: {service.output_dir}")
    print(f"Interfaz: http://{args.host}:{server.server_port}")
    print("Presiona Ctrl+C para detenerla.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAplicación detenida.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
