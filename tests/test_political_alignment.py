from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from features.political_alignment import load_party_alignment, parse_party_alignment


class PoliticalAlignmentTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.alignment = parse_party_alignment(json.dumps({
            "left": ["Partido Socialista de Chile"],
            "right": ["Partido Renovación Nacional"],
        }))

    def test_classification_is_accent_and_case_insensitive(self) -> None:
        self.assertEqual(
            self.alignment.classify("partido renovacion nacional"), "derecha"
        )
        self.assertEqual(
            self.alignment.classify("PARTIDO SOCIALISTA DE CHILE"), "izquierda"
        )
        self.assertEqual(self.alignment.classify("Independiente"), "centro")
        self.assertEqual(self.alignment.classify(None), "centro")

    def test_overlap_and_invalid_schema_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "izquierda y derecha"):
            parse_party_alignment(json.dumps({
                "left": ["Partido Único"],
                "right": ["partido unico"],
            }))
        with self.assertRaisesRegex(ValueError, "claves no admitidas"):
            parse_party_alignment(json.dumps({
                "left": ["A"], "right": ["B"], "center": ["C"],
            }))

    def test_snapshot_is_stable_and_documents_residual_rule(self) -> None:
        first = self.alignment.snapshot()
        second = self.alignment.snapshot()
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["environment_variable"], "PARTY_ALIGNMENT")
        self.assertIn("no enumerado", first["center_rule"])

    def test_loader_reads_dotenv_when_process_variable_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "PARTY_ALIGNMENT="
                + json.dumps({"left": ["Partido A"], "right": ["Partido B"]})
                + "\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                loaded = load_party_alignment(env_path)
                self.assertEqual(loaded.classify("Partido A"), "izquierda")
                self.assertEqual(loaded.classify("Partido B"), "derecha")

    def test_loader_rejects_missing_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "Falta PARTY_ALIGNMENT"):
            load_party_alignment(".env-inexistente", environ={})


if __name__ == "__main__":
    unittest.main()
