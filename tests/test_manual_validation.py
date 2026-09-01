from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd

from features.manual_validation.service import (
    SCHEMA_VERSION,
    ValidationError,
    ValidationService,
    _paragraph_blocks,
    _paragraphs,
    create_server,
    sample_records,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = PROJECT_ROOT / "features" / "manual_validation" / "web"


class ManualValidationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.source_path = self.root / "speech_df.parquet"
        self.codebook_path = self.root / "codebook.json"
        self.output_dir = self.root / "validation"
        self._write_corpus()
        self._write_codebook()
        self.service = ValidationService(
            source_path=self.source_path,
            codebook_path=self.codebook_path,
            output_dir=self.output_dir,
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write_corpus(self) -> None:
        rows = [
            {
                "utterance_id": "doc-a-1",
                "document_uri": "doc-a",
                "utterance_order": 1,
                "kind": "participation",
                "content": "La solidaridad debe mejorar las pensiones.\nSí.",
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2024-01-01",
                "constitutional_stage": "Primer trámite",
                "title": "Sesión A",
                "n_words": 7,
                "speaker": "Nombre que no debe exponerse",
                "speaker_id": "persona-secreta-1",
                "current_party": "Partido secreto",
                "gender": "F",
            },
            {
                "utterance_id": "doc-a-2",
                "document_uri": "doc-a",
                "utterance_order": 2,
                "kind": "participation",
                "content": (
                    "Rechazo que el ahorro individual pierda su propiedad.\n"
                    "Este párrafo adicional sostiene una segunda razón previsional."
                ),
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2024-01-01",
                "constitutional_stage": "Primer trámite",
                "title": "Sesión A",
                "n_words": 16,
                "speaker": "Segundo nombre oculto",
                "speaker_id": "persona-secreta-2",
                "current_party": "Otro partido secreto",
                "gender": "M",
            },
            {
                "utterance_id": "doc-a-3",
                "document_uri": "doc-a",
                "utterance_order": 3,
                "kind": "participation",
                "content": (
                    "El costo fiscal debe poder sostenerse durante muchos años. " * 10
                    + "\n"
                    + "La responsabilidad previsional requiere una regla estable y transparente. " * 10
                ),
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2024-01-01",
                "constitutional_stage": "Primer trámite",
                "title": "Sesión A",
                "n_words": 180,
                "speaker": "Tercer nombre oculto",
                "speaker_id": "persona-secreta-3",
                "current_party": "Partido secreto",
                "gender": "M",
            },
            {
                "utterance_id": "doc-b-1",
                "document_uri": "doc-b",
                "utterance_order": 1,
                "kind": "participation",
                "content": "Una pensión suficiente permite vivir con dignidad.",
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2025-01-02",
                "constitutional_stage": "Segundo trámite",
                "title": "Sesión B",
                "n_words": 7,
                "speaker": "Cuarto nombre oculto",
                "speaker_id": "persona-secreta-4",
                "current_party": "Partido secreto",
                "gender": "F",
            },
            {
                "utterance_id": "doc-b-2",
                "document_uri": "doc-b",
                "utterance_order": 2,
                "kind": "participation",
                "content": "La tabla es la siguiente y cedo la palabra.",
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2025-01-02",
                "constitutional_stage": "Segundo trámite",
                "title": "Sesión B",
                "n_words": 8,
                "speaker": "Quinto nombre oculto",
                "speaker_id": "persona-secreta-5",
                "current_party": "Partido secreto",
                "gender": "M",
            },
            {
                "utterance_id": "excluded-vote",
                "document_uri": "doc-b",
                "utterance_order": 3,
                "kind": "participation",
                "content": "Resultado de la votación nominal registrado por la secretaría.",
                "bill_number": "15480-13",
                "section_name": "Votacion",
                "is_preamble": False,
                "date": "2025-01-02",
                "constitutional_stage": "Segundo trámite",
                "title": "Sesión B",
                "n_words": 9,
                "analysis_included": False,
            },
            {
                "utterance_id": "excluded-event",
                "document_uri": "doc-b",
                "utterance_order": 4,
                "kind": "transcription_event",
                "content": "Aplausos.",
                "bill_number": "15480-13",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2025-01-02",
                "constitutional_stage": "Segundo trámite",
                "title": "Sesión B",
                "n_words": 1,
            },
            {
                "utterance_id": "excluded-bill",
                "document_uri": "doc-c",
                "utterance_order": 1,
                "kind": "participation",
                "content": "Discusión de otro proyecto.",
                "bill_number": "99999-99",
                "section_name": "Discusión",
                "is_preamble": False,
                "date": "2025-01-02",
                "constitutional_stage": "Primer trámite",
                "title": "Sesión C",
                "n_words": 4,
            },
        ]
        excluded_analysis = dict(rows[0])
        excluded_analysis.update(
            {
                "utterance_id": "excluded-analysis",
                "document_uri": "doc-d",
                "content": "Intervención excluida por la definición del corpus analítico.",
                "analysis_included": False,
            }
        )
        rows.append(excluded_analysis)
        for row in rows:
            row.setdefault("analysis_included", True)
        pd.DataFrame(rows).to_parquet(self.source_path, index=False)

    def _write_codebook(self) -> None:
        codebook = {
            "schema_version": "codebook-1.0.0",
            "version": "test-0.1",
            "status": "draft",
            "title": "Libro de prueba",
            "concepts": [
                {
                    "id": "solidaridad",
                    "label": "Solidaridad",
                    "definition": "Distribución colectiva de riesgos o recursos.",
                    "include": ["Redistribución previsional."],
                    "exclude": ["Uso retórico aislado."],
                },
                {
                    "id": "propiedad_individual_fondos",
                    "label": "Propiedad individual de los fondos",
                    "definition": "Los fondos pertenecen al cotizante.",
                    "include": ["Propiedad del ahorro."],
                    "exclude": ["Capitalización sin propiedad."],
                },
            ],
        }
        self.codebook_path.write_text(
            json.dumps(codebook, ensure_ascii=False), encoding="utf-8"
        )

    def _session(self, sample_size: int = 5) -> dict:
        return self.service.create_session(
            {
                "coder_id": "test-coder",
                "sample_size": sample_size,
                "seed": 1122,
                "strategy": "stratified",
            }
        )

    def _session_payload(self, session_id: str) -> dict:
        return json.loads((self.output_dir / f"{session_id}.json").read_text(encoding="utf-8"))

    def test_corpus_builds_short_paragraph_blocks_and_keeps_votes(self) -> None:
        self.assertEqual(len(self.service.records), 7)
        self.assertTrue(all(record["n_words"] >= 5 for record in self.service.records))
        self.assertTrue(all(record["n_words"] <= 150 for record in self.service.records))
        by_id = {record["unit_id"]: record for record in self.service.records}
        first = by_id["doc-a-1::p0001-p0002"]
        self.assertIsNone(first["previous_context"])
        self.assertEqual(first["unit_kind"], "paragraph_block")
        self.assertEqual(first["paragraph_start"], 1)
        self.assertEqual(first["paragraph_end"], 2)
        self.assertEqual(first["block_paragraph_count"], 2)
        self.assertEqual(len(first["source_segments"]), 2)
        self.assertEqual(
            first["content"],
            "La solidaridad debe mejorar las pensiones.\n\nSí.",
        )
        self.assertFalse(
            by_id["doc-a-2::p0001-p0002"]["previous_context"]["same_utterance"]
        )
        self.assertTrue(
            by_id["doc-a-3::p0001"]["next_context"]["same_utterance"]
        )
        self.assertIsNone(by_id["doc-b-1::p0001"]["previous_context"])
        self.assertIn("excluded-vote::p0001", by_id)

    def test_chunking_prefers_previous_context_and_enforces_strict_maximum(self) -> None:
        text = "\n".join(
            " ".join([f"p{paragraph_number}"] * words)
            for paragraph_number, words in enumerate([60, 35, 17, 147, 34], start=1)
        )
        paragraphs = _paragraphs(text)
        for paragraph_number, paragraph in enumerate(paragraphs, start=1):
            paragraph["paragraph_number"] = paragraph_number
        blocks = _paragraph_blocks(
            paragraphs,
            short_paragraph_words=50,
            target_block_words=100,
            max_block_words=150,
        )
        self.assertEqual([block["n_words"] for block in blocks], [112, 147, 34])
        self.assertEqual(blocks[0]["paragraph_start"], 1)
        self.assertEqual(blocks[0]["paragraph_end"], 3)
        self.assertTrue(all(block["n_words"] <= 150 for block in blocks))

        long_paragraph = _paragraphs(" ".join(["palabra"] * 320))
        long_paragraph[0]["paragraph_number"] = 1
        split_blocks = _paragraph_blocks(
            long_paragraph,
            short_paragraph_words=50,
            target_block_words=100,
            max_block_words=150,
        )
        self.assertEqual(sum(block["n_words"] for block in split_blocks), 320)
        self.assertTrue(all(block["n_words"] <= 150 for block in split_blocks))
        self.assertTrue(
            all(
                segment["paragraph_segment_count"] == len(split_blocks)
                for block in split_blocks
                for segment in block["source_segments"]
            )
        )

    def test_stratified_sampling_is_deterministic_and_unique(self) -> None:
        first = sample_records(self.service.records, 4, 77, "stratified")
        second = sample_records(self.service.records, 4, 77, "stratified")
        first_ids = [item["unit_id"] for item in first]
        self.assertEqual(first_ids, [item["unit_id"] for item in second])
        self.assertEqual(len(first_ids), len(set(first_ids)))
        self.assertTrue(all("sampling_stratum" in item for item in first))

    def test_identity_fields_are_never_exposed_or_persisted(self) -> None:
        summary = self._session()
        public = self.service.open_item(summary["session_id"], 0)
        persisted = self._session_payload(summary["session_id"])
        forbidden = {"speaker", "speaker_id", "current_party", "party", "gender"}

        def assert_no_forbidden_keys(value: object) -> None:
            if isinstance(value, dict):
                self.assertTrue(forbidden.isdisjoint(value.keys()))
                for nested in value.values():
                    assert_no_forbidden_keys(nested)
            elif isinstance(value, list):
                for nested in value:
                    assert_no_forbidden_keys(nested)

        assert_no_forbidden_keys(public)
        assert_no_forbidden_keys(persisted)

    def test_multiple_annotations_and_review_are_persisted(self) -> None:
        summary = self._session()
        session_id = summary["session_id"]
        opened = self.service.open_item(session_id, 0)
        text = opened["item"]["target_text"]
        first_end = min(len(text), 12)
        second_start = max(0, len(text) - 12)
        saved = self.service.save_item(
            session_id,
            0,
            {
                "decision": "statements",
                "annotations": [
                    {
                        "annotation_id": "known-concept",
                        "start_char": 0,
                        "end_char": first_end,
                        "evidence_text": text[:first_end],
                        "concept_status": "in_codebook",
                        "concept_id": "solidaridad",
                        "proposed_concept": "",
                        "stance": "support",
                        "note": "Criterio claro",
                        "selected_at_client": "2026-08-24T12:00:00.000Z",
                    },
                    {
                        "annotation_id": "missing-concept",
                        "start_char": second_start,
                        "end_char": len(text),
                        "evidence_text": text[second_start:],
                        "concept_status": "review",
                        "concept_id": None,
                        "proposed_concept": "Administración pública",
                        "stance": "oppose",
                        "note": "Candidato para el libro",
                        "selected_at_client": "2026-08-24T12:01:00.000Z",
                    },
                ],
                "general_comment": "El bloque combina dos argumentos.",
                "quality_flags": ["insufficient_context"],
            },
        )
        self.assertEqual(saved["item"]["status"], "completed")
        self.assertEqual(saved["item"]["decision"], "statements")
        self.assertEqual(len(saved["item"]["annotations"]), 2)

        persisted = self._session_payload(session_id)
        item = persisted["items"][0]
        self.assertEqual(persisted["schema_version"], SCHEMA_VERSION)
        self.assertEqual(persisted["source"]["unit_of_analysis"], "paragraph_block")
        self.assertEqual(persisted["sampling"]["minimum_words"], 5)
        self.assertEqual(persisted["sampling"]["short_paragraph_words"], 50)
        self.assertEqual(persisted["sampling"]["target_block_words"], 100)
        self.assertEqual(persisted["sampling"]["max_block_words"], 150)
        self.assertEqual(item["unit_kind"], "paragraph_block")
        self.assertEqual(item["revision"], 1)
        self.assertEqual(item["general_comment"], "El bloque combina dos argumentos.")
        self.assertEqual(item["quality_flags"], ["insufficient_context"])
        self.assertTrue(item["completed_at_utc"].endswith("Z"))
        self.assertIn("-", item["completed_at_local"])
        self.assertEqual(item["annotations"][0]["span"]["text"], text[:first_end])
        self.assertEqual(item["annotations"][1]["concept_status"], "review")
        self.assertIsNone(item["annotations"][1]["concept_id"])
        self.assertEqual(item["annotations"][1]["proposed_concept"], "Administración pública")
        self.assertEqual(persisted["codebook"]["version"], "test-0.1")
        self.assertEqual(persisted["sampling"]["seed"], 1122)

    def test_no_statements_and_invalid_exact_span(self) -> None:
        summary = self._session()
        session_id = summary["session_id"]
        saved = self.service.save_item(
            session_id,
            0,
            {
                "decision": "no_statements",
                "annotations": [],
                "general_comment": "Registro de votación sin discurso sustantivo.",
                "quality_flags": ["vote", "procedural"],
            },
        )
        self.assertEqual(saved["item"]["decision"], "no_statements")
        self.assertEqual(saved["item"]["quality_flags"], ["vote", "procedural"])
        text = self.service.open_item(session_id, 1)["item"]["target_text"]
        with self.assertRaisesRegex(ValidationError, "no coincide exactamente"):
            self.service.save_item(
                session_id,
                1,
                {
                    "decision": "statements",
                    "annotations": [
                        {
                            "start_char": 0,
                            "end_char": min(5, len(text)),
                            "evidence_text": "texto distinto",
                            "concept_status": "in_codebook",
                            "concept_id": "solidaridad",
                            "stance": "support",
                        }
                    ],
                },
            )

    def test_http_api_contract_and_bad_index(self) -> None:
        server = create_server(self.service, STATIC_DIR, "127.0.0.1", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with urllib.request.urlopen(f"{base_url}/api/config", timeout=5) as response:
                config = json.load(response)
                self.assertIn(
                    "default-src", response.headers.get("Content-Security-Policy", "")
                )
            self.assertEqual(config["corpus"]["available_units"], 7)
            self.assertEqual(config["corpus"]["minimum_words"], 5)
            self.assertEqual(config["corpus"]["short_paragraph_words"], 50)
            self.assertEqual(config["corpus"]["target_block_words"], 100)
            self.assertEqual(config["corpus"]["max_block_words"], 150)
            self.assertIn({"id": "vote", "label": "Voto"}, config["quality_flags"])

            request = urllib.request.Request(
                f"{base_url}/api/sessions",
                data=json.dumps(
                    {"sample_size": 2, "seed": 99, "strategy": "random"}
                ).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=5) as response:
                summary = json.load(response)
            self.assertEqual(summary["sample_size"], 2)

            with self.assertRaises(urllib.error.HTTPError) as caught:
                urllib.request.urlopen(
                    f"{base_url}/api/sessions/{summary['session_id']}/items/not-a-number",
                    timeout=5,
                )
            self.assertEqual(caught.exception.code, 400)
            caught.exception.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_static_ui_includes_adjacent_context_and_coded_highlight(self) -> None:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        javascript = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
        styles = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
        self.assertIn('id="next-text"', html)
        self.assertIn('id="general-comment"', html)
        self.assertIn('id="quality-flags"', html)
        self.assertIn("function renderTargetText()", javascript)
        self.assertIn("quality_flags: qualityFlags", javascript)
        self.assertIn('highlight.className = "coded-highlight"', javascript)
        self.assertIn(".coded-highlight", styles)
        self.assertIn("#fde68a", styles)
        self.assertIn("máximo estricto", javascript)


if __name__ == "__main__":
    unittest.main()
