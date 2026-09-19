"""Source-backed manual resolutions for historical parliamentary affiliations."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


KEY_COLUMNS = ("document_uri", "reference_date", "person_href")
REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "resolution",
    "party_at_date",
    "party_at_date_href",
    "evidence_url",
    "evidence_note",
    "reviewed_by",
    "reviewed_at",
}
RESOLUTIONS = {"pending", "confirmed", "nonpartisan", "unresolved"}
APPLIED_RESOLUTIONS = {"confirmed", "nonpartisan"}


class AffiliationOverrideError(ValueError):
    """Raised when the editable affiliation-resolution table is inconsistent."""


def _text(value: object) -> str:
    return "" if value is None else str(value).strip()


def _require(value: object, field: str, row_number: int) -> str:
    text = _text(value)
    if not text:
        raise AffiliationOverrideError(f"Fila {row_number}: falta {field}")
    return text


def load_affiliation_overrides(path: Path) -> pd.DataFrame:
    """Read and validate the user-editable, source-backed resolution queue."""
    if not path.is_file():
        raise FileNotFoundError(f"Falta la tabla editable de afiliaciones: {path}")
    table = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = sorted(REQUIRED_COLUMNS.difference(table.columns))
    if missing:
        raise AffiliationOverrideError(
            "Faltan columnas en la tabla de afiliaciones: " + ", ".join(missing)
        )
    table = table.copy()
    for column in REQUIRED_COLUMNS:
        table[column] = table[column].map(_text)
    table["resolution"] = table["resolution"].str.casefold()
    invalid = table.loc[~table["resolution"].isin(RESOLUTIONS), "resolution"].unique()
    if len(invalid):
        raise AffiliationOverrideError(
            "resolution debe ser pending, confirmed, nonpartisan o unresolved: "
            + ", ".join(sorted(invalid))
        )
    if table.duplicated(list(KEY_COLUMNS)).any():
        duplicates = table.loc[
            table.duplicated(list(KEY_COLUMNS), keep=False), list(KEY_COLUMNS)
        ].to_dict("records")
        raise AffiliationOverrideError(
            f"La tabla repite document_uri × reference_date × person_href: {duplicates[:3]}"
        )
    for index, row in table.iterrows():
        row_number = index + 2  # Header is row one in the CSV.
        if row["resolution"] not in APPLIED_RESOLUTIONS:
            continue
        party = _require(row["party_at_date"], "party_at_date", row_number)
        if row["resolution"] == "nonpartisan" and party.casefold() != "independiente":
            raise AffiliationOverrideError(
                f"Fila {row_number}: nonpartisan debe usar party_at_date=Independiente"
            )
        for field in ("evidence_url", "evidence_note", "reviewed_by", "reviewed_at"):
            _require(row[field], field, row_number)
    return table


def apply_affiliation_overrides(
    speeches: pd.DataFrame,
    overrides: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Apply only documented resolutions to automatic ``unknown`` affiliations.

    The BCN extraction is intentionally left untouched. This function changes the
    derived speech table only after validating that each editable row maps to an
    observed discussion/person/date and that it does not overwrite an automatic
    resolution or a role for which party affiliation is inapplicable.
    """
    required = {"document_uri", "date", "person_href", "party_at_date_status"}
    missing = sorted(required.difference(speeches.columns))
    if missing:
        raise AffiliationOverrideError(
            "No se pueden aplicar afiliaciones: faltan columnas " + ", ".join(missing)
        )
    result = speeches.copy()
    result["reference_date"] = result["date"].map(_text)
    # Keep the analytical schema stable even while every editable row is pending.
    for column in (
        "affiliation_evidence_url",
        "affiliation_evidence_note",
        "affiliation_reviewed_by",
        "affiliation_reviewed_at",
    ):
        result[column] = None
    active = overrides.loc[overrides["resolution"].isin(APPLIED_RESOLUTIONS)].copy()
    # The editable queue covers every law. A single-law render must apply only
    # its own rows, while still validating an exact person/date match in scope.
    active = active.loc[active["document_uri"].isin(result["document_uri"].unique())].copy()
    if active.empty:
        result["affiliation_resolution_method"] = "automatic"
        return result, active

    observed = result[["document_uri", "reference_date", "person_href"]].drop_duplicates()
    checked = active.merge(observed, on=list(KEY_COLUMNS), how="left", indicator=True)
    unmatched = checked.loc[checked["_merge"].ne("both"), list(KEY_COLUMNS)]
    if not unmatched.empty:
        raise AffiliationOverrideError(
            "La tabla incluye una discusión/persona/fecha que no existe en el corpus: "
            + str(unmatched.to_dict("records")[:3])
        )

    status_by_key = result.merge(
        active[list(KEY_COLUMNS)], on=list(KEY_COLUMNS), how="inner", validate="many_to_one"
    )
    ineligible = status_by_key.loc[
        ~status_by_key["party_at_date_status"].eq("unknown"),
        [*KEY_COLUMNS, "party_at_date_status"],
    ].drop_duplicates()
    if not ineligible.empty:
        raise AffiliationOverrideError(
            "Una corrección manual solo puede resolver afiliaciones unknown: "
            + str(ineligible.to_dict("records")[:3])
        )

    result = result.merge(
        active[
            [
                *KEY_COLUMNS,
                "resolution",
                "party_at_date",
                "party_at_date_href",
                "evidence_url",
                "evidence_note",
                "reviewed_by",
                "reviewed_at",
            ]
        ].rename(
            columns={
                "resolution": "_override_resolution",
                "party_at_date": "_override_party_at_date",
                "party_at_date_href": "_override_party_at_date_href",
                "evidence_url": "_override_evidence_url",
                "evidence_note": "_override_evidence_note",
                "reviewed_by": "_override_reviewed_by",
                "reviewed_at": "_override_reviewed_at",
            }
        ),
        on=list(KEY_COLUMNS),
        how="left",
        validate="many_to_one",
    )
    result["affiliation_resolution_method"] = "automatic"
    applied = result["_override_resolution"].notna()
    result.loc[applied, "party_at_date"] = result.loc[applied, "_override_party_at_date"]
    result.loc[applied, "party_at_date_href"] = result.loc[
        applied, "_override_party_at_date_href"
    ].replace("", None)
    result.loc[applied, "party_at_date_status"] = "matched"
    result.loc[applied, "party_at_date_source"] = "manual_documented"
    result.loc[applied, "affiliation_resolution_method"] = result.loc[
        applied, "_override_resolution"
    ].map({"confirmed": "manual_confirmed", "nonpartisan": "manual_nonpartisan"})
    result.loc[applied, "affiliation_evidence_url"] = result.loc[
        applied, "_override_evidence_url"
    ]
    result.loc[applied, "affiliation_evidence_note"] = result.loc[
        applied, "_override_evidence_note"
    ]
    result.loc[applied, "affiliation_reviewed_by"] = result.loc[
        applied, "_override_reviewed_by"
    ]
    result.loc[applied, "affiliation_reviewed_at"] = result.loc[
        applied, "_override_reviewed_at"
    ]
    result = result.drop(
        columns=[
            "_override_resolution",
            "_override_party_at_date",
            "_override_party_at_date_href",
            "_override_evidence_url",
            "_override_evidence_note",
            "_override_reviewed_by",
            "_override_reviewed_at",
        ]
    )
    return result, active
