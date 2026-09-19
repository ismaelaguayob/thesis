from __future__ import annotations

import unittest

import pandas as pd

from features.llm_annotations.evaluation import (
    attach_sampling_metadata,
    compare_blocks,
    create_adjudication_queue,
    manual_session_frames,
    summarize_block_comparison,
    validate_adjudication_queue,
)


class BlockEvaluationTestCase(unittest.TestCase):
    def test_sampling_metadata_is_attached_only_for_posthoc_analysis(self) -> None:
        blocks = pd.DataFrame([
            {"unit_id": "a", "resolution_status": "resolved", "evaluation_included": True},
            {"unit_id": "b", "resolution_status": "resolved", "evaluation_included": True},
        ])
        metadata = {
            "a": {"chamber": "Senado", "alignment": "izquierda", "gender": "Mujer",
                  "actor_type": "Parlamentario", "length_bin": "short"},
            "b": {"chamber": "Cámara", "alignment": "derecha", "gender": "Hombre",
                  "actor_type": "Parlamentario", "length_bin": "long"},
        }
        enriched = attach_sampling_metadata(blocks, metadata)
        self.assertEqual(enriched["alignment"].tolist(), ["izquierda", "derecha"])
        self.assertNotIn("alignment", blocks.columns)
        with self.assertRaisesRegex(ValueError, "Faltan metadatos"):
            attach_sampling_metadata(blocks, {"a": metadata["a"]})

    def test_manual_export_excludes_votes_procedure_and_unresolved(self) -> None:
        session = {"items": [
            {
                "unit_id": "included",
                "decision": "no_statements",
                "resolution_status": "resolved",
                "quality_flags": [],
                "annotations": [],
                "selection_weight": 2,
            },
            {
                "unit_id": "vote",
                "decision": "no_statements",
                "resolution_status": "resolved",
                "quality_flags": ["vote"],
                "annotations": [],
            },
            {
                "unit_id": "unknown",
                "decision": None,
                "resolution_status": "unresolved",
                "quality_flags": ["insufficient_context"],
                "annotations": [],
            },
        ]}
        blocks, annotations = manual_session_frames(session)
        indexed = blocks.set_index("unit_id")
        self.assertTrue(bool(indexed.loc["included", "evaluation_included"]))
        self.assertFalse(bool(indexed.loc["vote", "evaluation_included"]))
        self.assertEqual(indexed.loc["vote", "evaluation_exclusion_reasons"], '["vote"]')
        self.assertFalse(bool(indexed.loc["unknown", "evaluation_included"]))
        self.assertTrue(annotations.empty)

    def test_block_comparison_prioritizes_concept_and_stance_without_spans(self) -> None:
        blocks = pd.DataFrame([
            {"unit_id": "exact", "resolution_status": "resolved", "evaluation_included": True,
             "selection_weight": 1, "alignment": "izquierda"},
            {"unit_id": "stance", "resolution_status": "resolved", "evaluation_included": True,
             "selection_weight": 2, "alignment": "izquierda"},
            {"unit_id": "different", "resolution_status": "resolved", "evaluation_included": True,
             "selection_weight": 3, "alignment": "derecha"},
            {"unit_id": "vote", "resolution_status": "resolved", "evaluation_included": False,
             "selection_weight": 100, "alignment": "derecha"},
            {"unit_id": "failed", "resolution_status": "resolved", "evaluation_included": True,
             "selection_weight": 4, "alignment": "derecha"},
            {"unit_id": "review", "resolution_status": "resolved", "evaluation_included": True,
             "selection_weight": 5, "alignment": "centro"},
        ])
        human = pd.DataFrame([
            {"unit_id": "exact", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
            {"unit_id": "stance", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
            {"unit_id": "different", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
            {"unit_id": "vote", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
        ])
        results = pd.DataFrame([
            {"unit_id": "exact", "status": "completed"},
            {"unit_id": "stance", "status": "completed"},
            {"unit_id": "different", "status": "completed"},
            {"unit_id": "vote", "status": "completed"},
            {"unit_id": "failed", "status": "incomplete"},
            {"unit_id": "review", "status": "completed"},
        ])
        model = pd.DataFrame([
            {"unit_id": "exact", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
            {"unit_id": "stance", "concept_status": "in_codebook", "concept_id": "a", "stance": "oppose"},
            {"unit_id": "different", "concept_status": "in_codebook", "concept_id": "b", "stance": "support"},
            {"unit_id": "vote", "concept_status": "in_codebook", "concept_id": "a", "stance": "support"},
            {"unit_id": "review", "concept_status": "review", "concept_id": None, "stance": "support"},
        ])
        comparison = compare_blocks(blocks, human, results, model).set_index("unit_id")
        self.assertEqual(comparison.loc["exact", "comparison_status"], "concept_and_stance")
        self.assertEqual(comparison.loc["stance", "comparison_status"], "concept_only")
        self.assertEqual(comparison.loc["different", "comparison_status"], "divergent")
        self.assertEqual(comparison.loc["failed", "comparison_status"], "model_unavailable")
        self.assertEqual(comparison.loc["review", "comparison_status"], "concept_review_required")
        self.assertNotIn("vote", comparison.index)

        summary = summarize_block_comparison(comparison.reset_index())
        self.assertEqual(summary["blocks"].sum(), 5)
        self.assertAlmostEqual(summary["weighted_share"].sum(), 1.0)
        by_alignment = summarize_block_comparison(comparison.reset_index(), ["alignment"])
        self.assertEqual(
            set(by_alignment["alignment"]), {"izquierda", "derecha", "centro"}
        )
        self.assertTrue(all(
            abs(value - 1) < 1e-12
            for value in by_alignment.groupby("alignment")["weighted_share"].sum()
        ))

        queue = create_adjudication_queue(comparison.reset_index())
        self.assertEqual(set(queue["unit_id"]), {"stance", "different", "review"})
        queue.loc[queue.unit_id.eq("stance"), [
            "adjudication_status", "adjudicated_pairs", "reason", "reviewer"
        ]] = ["resolved", '[["a","support"]]', "Relectura del ancla.", "IA"]
        queue.loc[queue.unit_id.eq("different"), [
            "adjudication_status", "reason", "reviewer"
        ]] = ["unresolved", "La evidencia no permite distinguir los conceptos.", "IA"]
        queue.loc[queue.unit_id.eq("review"), [
            "adjudication_status", "reason", "reviewer"
        ]] = ["unresolved", "La propuesta requiere revisar el libro.", "IA"]
        validate_adjudication_queue(queue)


if __name__ == "__main__":
    unittest.main()
