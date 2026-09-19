from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from features.affiliation_overrides import (
    AffiliationOverrideError,
    apply_affiliation_overrides,
    load_affiliation_overrides,
)


class AffiliationOverridesTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name) / "overrides.csv"
        self.speeches = pd.DataFrame([
            {
                "document_uri": "document-1", "date": "2025-01-29",
                "person_href": "person-1", "party_at_date": None,
                "party_at_date_href": None, "party_at_date_status": "unknown",
                "party_at_date_source": None,
            },
            {
                "document_uri": "document-2", "date": "2025-01-29",
                "person_href": "person-2", "party_at_date": "Partido A",
                "party_at_date_href": "party-a", "party_at_date_status": "matched",
                "party_at_date_source": "bcn_militancy_history",
            },
        ])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _write(self, rows: list[dict[str, str]]) -> None:
        pd.DataFrame(rows).to_csv(self.path, index=False)

    @staticmethod
    def _row(**values: str) -> dict[str, str]:
        return {
            "document_uri": "document-1",
            "reference_date": "2025-01-29",
            "person_href": "person-1",
            "resolution": "pending",
            "party_at_date": "",
            "party_at_date_href": "",
            "evidence_url": "",
            "evidence_note": "",
            "reviewed_by": "",
            "reviewed_at": "",
            **values,
        }

    def test_pending_rows_preserve_automatic_unknown_affiliations(self) -> None:
        self._write([self._row()])
        result, applied = apply_affiliation_overrides(
            self.speeches, load_affiliation_overrides(self.path)
        )
        self.assertTrue(applied.empty)
        self.assertEqual("unknown", result.loc[0, "party_at_date_status"])
        self.assertEqual("automatic", result.loc[0, "affiliation_resolution_method"])

    def test_documented_nonpartisan_resolution_is_applied_with_provenance(self) -> None:
        self._write([self._row(
            resolution="nonpartisan", party_at_date="Independiente",
            evidence_url="https://example.test/evidence",
            evidence_note="Perfil institucional fechado en la discusión.",
            reviewed_by="ismael", reviewed_at="2026-09-19",
        )])
        result, applied = apply_affiliation_overrides(
            self.speeches, load_affiliation_overrides(self.path)
        )
        self.assertEqual(1, len(applied))
        self.assertEqual("Independiente", result.loc[0, "party_at_date"])
        self.assertEqual("matched", result.loc[0, "party_at_date_status"])
        self.assertEqual("manual_documented", result.loc[0, "party_at_date_source"])
        self.assertEqual("manual_nonpartisan", result.loc[0, "affiliation_resolution_method"])
        self.assertEqual("https://example.test/evidence", result.loc[0, "affiliation_evidence_url"])
        self.assertEqual("ismael", result.loc[0, "affiliation_reviewed_by"])

    def test_documented_rows_require_provenance_and_unknown_automatic_state(self) -> None:
        self._write([self._row(resolution="confirmed", party_at_date="Partido A")])
        with self.assertRaisesRegex(AffiliationOverrideError, "falta evidence_url"):
            load_affiliation_overrides(self.path)

        self._write([self._row(
            document_uri="document-2", person_href="person-2", resolution="confirmed",
            party_at_date="Partido A", evidence_url="https://example.test/evidence",
            evidence_note="Fuente.", reviewed_by="ismael", reviewed_at="2026-09-19",
        )])
        with self.assertRaisesRegex(AffiliationOverrideError, "solo puede resolver afiliaciones unknown"):
            apply_affiliation_overrides(self.speeches, load_affiliation_overrides(self.path))


if __name__ == "__main__":
    unittest.main()
