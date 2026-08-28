#!/usr/bin/env python3
"""Run the local manual-validation web application."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.manual_validation import ValidationService, create_server  # noqa: E402


def default_source() -> Path:
    candidates = [
        PROJECT_ROOT / "data" / "proc_data" / "speech_df.parquet",
        PROJECT_ROOT / "data" / "speech_df.parquet",
    ]
    return next((path for path in candidates if path.exists()), candidates[0])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interfaz local para muestreo y codificación manual de declaraciones."
    )
    parser.add_argument("--source", type=Path, default=default_source())
    parser.add_argument(
        "--codebook",
        type=Path,
        default=PROJECT_ROOT / "config" / "codebook_v0.1.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "proc_data" / "validation",
    )
    parser.add_argument("--bill-number", default="15480-13")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = ValidationService(
        source_path=args.source,
        codebook_path=args.codebook,
        output_dir=args.output_dir,
        bill_number=args.bill_number,
    )
    static_dir = PROJECT_ROOT / "web" / "manual_validation"
    server = create_server(service, static_dir, args.host, args.port)
    print(f"Corpus: {service.source_path}")
    print(f"Intervenciones disponibles: {len(service.records)}")
    print(f"Libro de códigos: {service.codebook_path}")
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
