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
            "center": ["Partido Demócrata Cristiano"],
            "right": ["Partido Renovación Nacional"],
            "nonpartisan": ["Independiente"],
        }))

    def test_classification_is_accent_and_case_insensitive(self) -> None:
        self.assertEqual(
            self.alignment.classify("partido renovacion nacional"), "derecha"
        )
        self.assertEqual(
            self.alignment.classify("PARTIDO SOCIALISTA DE CHILE"), "izquierda"
        )
        self.assertEqual(self.alignment.classify("Partido Demócrata Cristiano"), "centro")
        self.assertEqual(self.alignment.classify("Independiente"), "nonpartisan")
        self.assertEqual(self.alignment.classify(None), "unclassified")

    def test_overlap_and_invalid_schema_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "más de una categoría"):
            parse_party_alignment(json.dumps({
                "left": ["Partido Único"],
                "center": ["Centro"],
                "right": ["partido unico"],
                "nonpartisan": ["Independiente"],
            }))
        with self.assertRaisesRegex(ValueError, "claves no admitidas"):
            parse_party_alignment(json.dumps({
                "left": ["A"], "center": ["B"], "right": ["C"],
                "nonpartisan": ["D"], "other": ["E"],
            }))

    def test_snapshot_is_stable_and_documents_unclassified_rule(self) -> None:
        first = self.alignment.snapshot()
        second = self.alignment.snapshot()
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["environment_variable"], "PARTY_ALIGNMENT")
        self.assertIn("no enumerado", first["unclassified_rule"])

    def test_loader_reads_dotenv_when_process_variable_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text(
                "PARTY_ALIGNMENT="
                + json.dumps({
                    "left": ["Partido A"], "center": ["Partido C"],
                    "right": ["Partido B"], "nonpartisan": ["Independiente"],
                })
                + "\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                loaded = load_party_alignment(env_path)
                self.assertEqual(loaded.classify("Partido A"), "izquierda")
                self.assertEqual(loaded.classify("Partido B"), "derecha")
                self.assertEqual(loaded.classify("Partido C"), "centro")
                self.assertEqual(loaded.classify("Independiente"), "nonpartisan")

    def test_loader_rejects_missing_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "Falta PARTY_ALIGNMENT"):
            load_party_alignment(".env-inexistente", environ={})


if __name__ == "__main__":
    unittest.main()
