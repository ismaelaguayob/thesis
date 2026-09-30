from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from features.independent_blocs import (
    IndependentBlocError,
    apply_independent_blocs,
    load_independent_blocs,
)
from features.political_alignment import PartyAlignment


ALIGNMENT = PartyAlignment(
    left=("Partido Socialista de Chile",),
    center=("Partido Demócrata Cristiano",),
    right=("Partido Unión Demócrata Independiente",),
    nonpartisan=("Independiente",),
)


class IndependentBlocsTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "blocs.csv"
        self.speeches = pd.DataFrame([
            {
                "document_uri": "document-1", "date": "2025-01-29",
                "person_href": "person-1", "party_at_date": "Independiente",
                "party_at_date_status": "matched",
            },
            {
                "document_uri": "document-1", "date": "2025-01-29",
                "person_href": "person-1", "party_at_date": "Independiente",
                "party_at_date_status": "matched",
            },
            {
                "document_uri": "document-1", "date": "2025-01-29",
                "person_href": "person-2", "party_at_date": "Partido Socialista de Chile",
                "party_at_date_status": "matched",
            },
            {
                "document_uri": "document-1", "date": "2025-01-29",
                "person_href": "person-3", "party_at_date": None,
                "party_at_date_status": "not_applicable",
            },
        ])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _load(self, rows: list[dict[str, str]]) -> pd.DataFrame:
        pd.DataFrame(rows).to_csv(self.path, index=False)
        return load_independent_blocs(self.path, ALIGNMENT)

    @staticmethod
    def _row(**values: str) -> dict[str, str]:
        return {
            "document_uri": "document-1",
            "reference_date": "2025-01-29",
            "person_href": "person-1",
            "speaker": "Persona Uno",
            "electoral_pact": "",
            "electoral_quota_party": "",
            "bancada_at_date": "",
            "bloc_party": "",
            "basis": "",
            "resolution": "pending",
            "evidence_url": "",
            "evidence_note": "",
            "reviewed_by": "",
            "reviewed_at": "",
            **values,
        }

    def _confirmed(self, **values: str) -> dict[str, str]:
        return self._row(**{
            "resolution": "confirmed", "basis": "cupo",
            "electoral_quota_party": "Partido Socialista de Chile",
            "bloc_party": "Partido Socialista de Chile",
            "evidence_url": "https://example.org", "evidence_note": "IND-PS en 2021.",
            "reviewed_by": "Revisor", "reviewed_at": "2026-09-29", **values,
        })

    def test_pending_rows_keep_independent_group(self) -> None:
        result, applied = apply_independent_blocs(self.speeches, self._load([self._row()]))

        self.assertTrue(applied.empty)
        self.assertEqual(result["political_group_party"].tolist()[:3], [
            "Independiente", "Independiente", "Partido Socialista de Chile",
        ])
        self.assertTrue(pd.isna(result.loc[3, "political_group_party"]))
        self.assertEqual(result["political_group_source"].tolist(), [
            "independent_pending", "independent_pending", "party", None,
        ])

    def test_confirmed_row_assigns_group_without_touching_party(self) -> None:
        result, applied = apply_independent_blocs(self.speeches, self._load([self._confirmed()]))

        self.assertEqual(len(applied), 1)
        self.assertEqual(result.loc[:1, "political_group_party"].tolist(), [
            "Partido Socialista de Chile", "Partido Socialista de Chile",
        ])
        self.assertEqual(result.loc[:1, "party_at_date"].tolist(), [
            "Independiente", "Independiente",
        ])
        self.assertEqual(result.loc[0, "political_group_source"], "independent_quota")
        self.assertEqual(result.loc[0, "political_group_evidence_url"], "https://example.org")

    def test_nonpartisan_row_is_documented_as_without_bloc(self) -> None:
        row = self._row(
            resolution="nonpartisan", basis="none", evidence_url="https://example.org",
            evidence_note="Sin pacto ni bancada.", reviewed_by="Revisor",
            reviewed_at="2026-09-29",
        )
        result, _ = apply_independent_blocs(self.speeches, self._load([row]))

        self.assertEqual(result.loc[0, "political_group_party"], "Independiente")
        self.assertEqual(result.loc[0, "political_group_source"], "independent_none")

    def test_confirmed_row_requires_evidence(self) -> None:
        with self.assertRaisesRegex(IndependentBlocError, "evidence_url"):
            self._load([self._confirmed(evidence_url="")])

    def test_bloc_party_must_be_classified(self) -> None:
        with self.assertRaisesRegex(IndependentBlocError, "PARTY_ALIGNMENT"):
            self._load([self._confirmed(bloc_party="Partido Inexistente")])

    def test_bancada_basis_requires_bancada(self) -> None:
        with self.assertRaisesRegex(IndependentBlocError, "bancada_at_date"):
            self._load([self._confirmed(basis="bancada")])

    def test_rows_must_match_an_independent_in_scope(self) -> None:
        table = self._load([self._confirmed(person_href="person-2")])
        with self.assertRaisesRegex(IndependentBlocError, "no corresponden"):
            apply_independent_blocs(self.speeches, table)

    def test_pending_rows_may_reference_unresolved_people(self) -> None:
        table = self._load([self._row(person_href="person-3")])
        result, applied = apply_independent_blocs(self.speeches, table)

        self.assertTrue(applied.empty)
        self.assertTrue(pd.isna(result.loc[3, "political_group_party"]))

    def test_affinity_basis_assigns_executive_group(self) -> None:
        table = self._load([self._confirmed(basis="cercania", electoral_quota_party="")])
        result, _ = apply_independent_blocs(self.speeches, table)

        self.assertEqual(result.loc[0, "political_group_party"], "Partido Socialista de Chile")
        self.assertEqual(result.loc[0, "political_group_source"], "independent_affinity")

    def test_spreadsheet_dates_are_rejected(self) -> None:
        with self.assertRaisesRegex(IndependentBlocError, "AAAA-MM-DD"):
            self._load([self._row(reference_date="01-29-25")])

    def test_byte_order_mark_is_tolerated(self) -> None:
        pd.DataFrame([self._confirmed()]).to_csv(self.path, index=False, encoding="utf-8-sig")
        table = load_independent_blocs(self.path, ALIGNMENT)

        self.assertEqual(table.loc[0, "document_uri"], "document-1")

    def test_rows_from_other_documents_are_ignored(self) -> None:
        table = self._load([self._confirmed(document_uri="document-9")])
        result, applied = apply_independent_blocs(self.speeches, table)

        self.assertTrue(applied.empty)
        self.assertEqual(result.loc[0, "political_group_party"], "Independiente")


if __name__ == "__main__":
    unittest.main()
