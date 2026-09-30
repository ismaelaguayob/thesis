"""Source-backed political-group assignments for independent parliamentarians.

BCN records independents as ``Independiente`` at the debate date. The thesis
assigns them to the group of the caucus (bancada) they joined at that date or,
when no caucus is documented, to the party whose electoral quota they occupied.
Independent members of the executive, who have neither, are assigned by their
documented closeness to a party (``cercania``).
``party_at_date`` keeps the historical militancy; the assignment is stored in
``political_group_party``, which is the only field used to derive alignment.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from features.political_alignment import PartyAlignment, normalize_party_name


KEY_COLUMNS = ("document_uri", "reference_date", "person_href")
REQUIRED_COLUMNS = {
    *KEY_COLUMNS,
    "speaker",
    "electoral_pact",
    "electoral_quota_party",
    "bancada_at_date",
    "bloc_party",
    "basis",
    "resolution",
    "evidence_url",
    "evidence_note",
    "reviewed_by",
    "reviewed_at",
}
RESOLUTIONS = {"pending", "confirmed", "nonpartisan", "unresolved"}
BASES = {"bancada", "cupo", "cercania", "none"}
INDEPENDENT_KEY = normalize_party_name("Independiente")
GROUP_SOURCES = {
    "bancada": "independent_bancada",
    "cupo": "independent_quota",
    "cercania": "independent_affinity",
    "none": "independent_none",
}


class IndependentBlocError(ValueError):
    """Raised when the editable independent-assignment table is inconsistent."""


def _text(value: object) -> str:
    return "" if value is None or pd.isna(value) else str(value).strip()


def load_independent_blocs(path: Path, alignment: PartyAlignment) -> pd.DataFrame:
    """Read and validate the curated assignment table."""
    if not path.is_file():
        raise FileNotFoundError(f"Falta la tabla de asignación de independientes: {path}")
    # utf-8-sig tolera el BOM que agregan las planillas al guardar CSV.
    table = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    missing = sorted(REQUIRED_COLUMNS.difference(table.columns))
    if missing:
        raise IndependentBlocError(
            "Faltan columnas en la tabla de independientes: " + ", ".join(missing)
        )
    table = table.copy()
    for column in table.columns:
        table[column] = table[column].map(_text)
    table["resolution"] = table["resolution"].str.casefold()
    bad_dates = table.loc[
        ~table["reference_date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}"), "reference_date"
    ].unique()
    if len(bad_dates):
        raise IndependentBlocError(
            "reference_date debe usar el formato AAAA-MM-DD; una planilla pudo "
            "reformatear las fechas: " + ", ".join(sorted(bad_dates)[:5])
        )
    table["basis"] = table["basis"].str.casefold()
    invalid = sorted(set(table["resolution"]).difference(RESOLUTIONS))
    if invalid:
        raise IndependentBlocError(
            "resolution debe ser pending, confirmed, nonpartisan o unresolved: "
            + ", ".join(invalid)
        )
    if table.duplicated(list(KEY_COLUMNS)).any():
        duplicates = table.loc[
            table.duplicated(list(KEY_COLUMNS), keep=False), list(KEY_COLUMNS)
        ].to_dict("records")
        raise IndependentBlocError(
            f"La tabla repite document_uri × reference_date × person_href: {duplicates[:3]}"
        )
    for index, row in table.iterrows():
        row_number = index + 2  # Header is row one in the CSV.
        resolution = row["resolution"]
        if resolution not in {"confirmed", "nonpartisan"}:
            continue
        for field in ("evidence_url", "evidence_note", "reviewed_by", "reviewed_at"):
            if not row[field]:
                raise IndependentBlocError(f"Fila {row_number}: falta {field}")
        if resolution == "nonpartisan":
            if row["basis"] != "none" or row["bloc_party"]:
                raise IndependentBlocError(
                    f"Fila {row_number}: nonpartisan exige basis=none y bloc_party vacío"
                )
            continue
        if row["basis"] not in {"bancada", "cupo", "cercania"}:
            raise IndependentBlocError(
                f"Fila {row_number}: confirmed exige basis=bancada, cupo o cercania"
            )
        if row["basis"] == "bancada" and not row["bancada_at_date"]:
            raise IndependentBlocError(f"Fila {row_number}: falta bancada_at_date")
        if row["basis"] == "cupo" and not row["electoral_quota_party"]:
            raise IndependentBlocError(f"Fila {row_number}: falta electoral_quota_party")
        if not row["bloc_party"]:
            raise IndependentBlocError(f"Fila {row_number}: falta bloc_party")
        if alignment.classify(row["bloc_party"]) == "unclassified":
            raise IndependentBlocError(
                f"Fila {row_number}: bloc_party {row['bloc_party']!r} no figura en "
                "PARTY_ALIGNMENT"
            )
    return table


def apply_independent_blocs(
    speeches: pd.DataFrame, table: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Derive ``political_group_party`` without overwriting ``party_at_date``.

    Militants keep their party. Independents with a confirmed row take
    ``bloc_party``; the rest keep ``Independiente`` and record why.
    """
    required = {"document_uri", "date", "person_href", "party_at_date", "party_at_date_status"}
    missing = sorted(required.difference(speeches.columns))
    if missing:
        raise IndependentBlocError(
            "No se pueden asignar independientes: faltan columnas " + ", ".join(missing)
        )
    result = speeches.copy()
    matched = result["party_at_date_status"].eq("matched")
    independent = matched & result["party_at_date"].map(normalize_party_name).eq(
        INDEPENDENT_KEY
    )
    result["political_group_party"] = result["party_at_date"].where(matched)
    result["political_group_source"] = None
    result.loc[matched, "political_group_source"] = "party"
    result.loc[independent, "political_group_source"] = "independent_pending"
    for column in ("political_group_evidence_url", "political_group_evidence_note"):
        result[column] = None

    # Pending rows may describe people whose affiliation is still unresolved;
    # only rows that will be applied must match an observed independent.
    in_scope = table.loc[
        table["document_uri"].isin(result["document_uri"].unique())
        & table["resolution"].isin({"confirmed", "nonpartisan"})
    ].copy()
    keys = pd.DataFrame({
        "document_uri": result["document_uri"].map(_text),
        "reference_date": result["date"].map(_text),
        "person_href": result["person_href"].map(_text),
    })
    observed = keys.loc[independent].drop_duplicates()
    checked = in_scope.merge(observed, on=list(KEY_COLUMNS), how="left", indicator=True)
    unmatched = checked.loc[checked["_merge"].ne("both"), [*KEY_COLUMNS, "speaker"]]
    if not unmatched.empty:
        raise IndependentBlocError(
            "La tabla incluye filas que no corresponden a un independiente del corpus: "
            + str(unmatched.to_dict("records")[:3])
        )

    active = in_scope
    lookup = active.set_index(list(KEY_COLUMNS))
    row_keys = pd.MultiIndex.from_frame(keys)
    hit = independent & row_keys.isin(lookup.index)
    if hit.any():
        rows = lookup.loc[row_keys[hit]]
        confirmed = rows["resolution"].eq("confirmed").to_numpy()
        group_party = rows["bloc_party"].where(confirmed, "Independiente").to_numpy()
        result.loc[hit, "political_group_party"] = group_party
        result.loc[hit, "political_group_source"] = rows["basis"].map(GROUP_SOURCES).to_numpy()
        result.loc[hit, "political_group_evidence_url"] = rows["evidence_url"].to_numpy()
        result.loc[hit, "political_group_evidence_note"] = rows["evidence_note"].to_numpy()
    return result, active
