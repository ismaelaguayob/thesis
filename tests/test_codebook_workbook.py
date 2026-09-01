from __future__ import annotations

import json
import unittest
from pathlib import Path

from features.manual_validation.codebook_workbook import read_codebook_workbook


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CodebookWorkbookTestCase(unittest.TestCase):
    def test_v01_xlsx_remains_the_exact_source_of_its_json(self) -> None:
        workbook = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.1.xlsx"
        generated_json = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.1.json"
        expected = read_codebook_workbook(workbook)
        actual = json.loads(generated_json.read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected["concepts"]), 10)
        self.assertEqual(expected["concepts"][0]["id"], "capitalizacion_individual")

    def test_v02_xlsx_is_the_exact_source_of_the_generated_json(self) -> None:
        workbook = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.2.xlsx"
        generated_json = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.2.json"
        expected = read_codebook_workbook(workbook)
        actual = json.loads(generated_json.read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)
        self.assertEqual(expected["version"], "0.3.0-pilot")
        self.assertEqual(len(expected["concepts"]), 13)
        ids = {concept["id"] for concept in expected["concepts"]}
        self.assertNotIn("capitalizacion_individual_afp", ids)
        self.assertNotIn("solidaridad", ids)
        self.assertNotIn("suficiencia_pensiones", ids)
        self.assertNotIn("sostenibilidad_financiera", ids)
        self.assertIn("igualdad_universalismo", ids)
        self.assertIn("conciencia_costos", ids)
        self.assertIn("solidaridad_intergeneracional", ids)
        self.assertIn("ineficiencia_estado", ids)
        self.assertIn("capitalizacion_individual", ids)
        self.assertIn("prevision_como_mercado", ids)
        self.assertIn("ilegitimidad_origen_dictatorial", ids)
        self.assertNotIn("comisiones_afp", ids)
        self.assertTrue(
            all(concept.get("orientation_anchor") for concept in expected["concepts"])
        )
        cost_awareness = next(
            concept
            for concept in expected["concepts"]
            if concept["id"] == "conciencia_costos"
        )
        self.assertEqual(
            cost_awareness["orientation_anchor"],
            "La reforma o expansión previsional evaluada es demasiado costosa, "
            "carece de financiamiento sostenible o excede la capacidad fiscal "
            "del Estado.",
        )
        intergenerational_solidarity = next(
            concept
            for concept in expected["concepts"]
            if concept["id"] == "solidaridad_intergeneracional"
        )
        self.assertEqual(
            intergenerational_solidarity["orientation_anchor"],
            "Las generaciones activas deben compartir recursos o riesgos "
            "previsionales con las generaciones jubiladas.",
        )
        market = next(
            concept
            for concept in expected["concepts"]
            if concept["id"] == "prevision_como_mercado"
        )
        self.assertTrue(any("productividad" in criterion for criterion in market["include"]))
        self.assertTrue(any("Comisiones" in criterion for criterion in market["include"]))
        reciprocity = next(
            concept
            for concept in expected["concepts"]
            if concept["id"] == "reciprocidad_contributiva"
        )
        self.assertTrue(
            any("capitalización individual" in criterion for criterion in reciprocity["exclude"])
        )

    def test_v03_xlsx_is_the_exact_source_of_the_generated_json(self) -> None:
        workbook = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.3.xlsx"
        generated_json = PROJECT_ROOT / "data" / "codebook" / "codebook_v0.3.json"
        expected = read_codebook_workbook(workbook)
        actual = json.loads(generated_json.read_text(encoding="utf-8"))
        self.assertEqual(expected, actual)
        self.assertEqual(expected["version"], "0.4.0-pilot")
        self.assertEqual(len(expected["concepts"]), 14)
        concepts = {concept["id"]: concept for concept in expected["concepts"]}
        self.assertIn("acuerdos_moderacion", concepts)
        self.assertIn("título moral", concepts["reciprocidad_contributiva"]["definition"])
        self.assertTrue(
            any(
                "controlar" in criterion
                for criterion in concepts["reciprocidad_contributiva"]["include"]
            )
        )
        self.assertTrue(
            any(
                "preferencias ciudadanas" in criterion
                for criterion in concepts["acuerdos_moderacion"]["exclude"]
            )
        )


if __name__ == "__main__":
    unittest.main()
