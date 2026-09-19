"""Block-level comparison of a frozen human reference and immutable LLM output."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import pandas as pd

from features.manual_validation.service import (
    ALLOWED_DECISIONS,
    evaluation_inclusion,
)


COMPARISON_SCHEMA_VERSION = "block-annotation-comparison-1.0.0"
COMPARISON_STATUSES = {
    "concept_and_stance",
    "concept_only",
    "divergent",
    "concept_review_required",
    "model_unavailable",
}
ADJUDICATION_STATUSES = {"pending", "resolved", "unresolved"}
ANALYSIS_METADATA_FIELDS = (
    "chamber", "alignment", "gender", "actor_type", "length_bin",
)


def _canonical(values: set[Any]) -> str:
    return json.dumps(sorted(values), ensure_ascii=False, separators=(",", ":"))


def manual_session_frames(session_or_path: dict[str, Any] | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Convert one frozen manual session to block and annotation tables."""
    if isinstance(session_or_path, Path):
        session = json.loads(session_or_path.read_text(encoding="utf-8"))
    else:
        session = session_or_path

    block_rows: list[dict[str, Any]] = []
    annotation_rows: list[dict[str, Any]] = []
    for item in session.get("items", []):
        decision = item.get("decision")
        resolution_status = item.get("resolution_status") or (
            "resolved" if decision in ALLOWED_DECISIONS else None
        )
        included, reasons = evaluation_inclusion(
            resolution_status, item.get("quality_flags", [])
        )
        unit_id = str(item["unit_id"])
        block_rows.append({
            "unit_id": unit_id,
            "utterance_id": item.get("utterance_id"),
            "law_number": item.get("law_number"),
            "document_uri": item.get("document_uri"),
            "resolution_status": resolution_status,
            "decision": decision,
            "evaluation_included": item.get("evaluation_included", included),
            "evaluation_exclusion_reasons": json.dumps(
                item.get("evaluation_exclusion_reasons", reasons),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "selection_weight": item.get("selection_weight", 1.0),
        })
        for annotation in item.get("annotations", []):
            annotation_rows.append({
                "unit_id": unit_id,
                "annotation_id": annotation.get("annotation_id"),
                "concept_status": annotation.get("concept_status"),
                "concept_id": annotation.get("concept_id"),
                "stance": annotation.get("stance"),
            })

    blocks = pd.DataFrame(block_rows)
    annotations = pd.DataFrame(
        annotation_rows,
        columns=["unit_id", "annotation_id", "concept_status", "concept_id", "stance"],
    )
    return blocks, annotations


def attach_sampling_metadata(
    reference_blocks: pd.DataFrame,
    metadata_by_unit: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Attach private stratum attributes after blind coding, keyed by block ID."""
    if "unit_id" not in reference_blocks.columns:
        raise ValueError("reference_blocks no contiene unit_id")
    if reference_blocks["unit_id"].astype(str).duplicated().any():
        raise ValueError("reference_blocks contiene unit_id duplicados")
    enriched = reference_blocks.copy()
    unit_ids = enriched["unit_id"].astype(str)
    missing = sorted({unit_id for unit_id in unit_ids if unit_id not in metadata_by_unit})
    if missing:
        preview = ", ".join(missing[:3])
        raise ValueError(f"Faltan metadatos de muestreo para: {preview}")
    for field in ANALYSIS_METADATA_FIELDS:
        enriched[field] = [metadata_by_unit[unit_id].get(field) for unit_id in unit_ids]
    return enriched


def compare_blocks(
    reference_blocks: pd.DataFrame,
    reference_annotations: pd.DataFrame,
    model_results: pd.DataFrame,
    model_annotations: pd.DataFrame,
) -> pd.DataFrame:
    """Compare concept and stance sets by block, without using span overlap."""
    required_blocks = {"unit_id", "resolution_status", "evaluation_included"}
    required_results = {"unit_id", "status"}
    required_annotations = {"unit_id", "concept_status", "concept_id", "stance"}
    for name, frame, required in (
        ("reference_blocks", reference_blocks, required_blocks),
        ("reference_annotations", reference_annotations, required_annotations),
        ("model_results", model_results, required_results),
        ("model_annotations", model_annotations, required_annotations),
    ):
        missing = sorted(required.difference(frame.columns))
        if missing:
            raise ValueError(f"{name} no contiene: {', '.join(missing)}")
    if reference_blocks["unit_id"].astype(str).duplicated().any():
        raise ValueError("reference_blocks contiene unit_id duplicados")
    if model_results["unit_id"].astype(str).duplicated().any():
        raise ValueError("model_results contiene unit_id duplicados")

    def known_pairs(frame: pd.DataFrame) -> dict[str, set[tuple[str, str]]]:
        pairs: dict[str, set[tuple[str, str]]] = defaultdict(set)
        known = frame.loc[
            frame["concept_status"].eq("in_codebook")
            & frame["concept_id"].notna()
            & frame["stance"].isin(["support", "oppose"])
        ]
        for row in known.itertuples(index=False):
            pairs[str(row.unit_id)].add((str(row.concept_id), str(row.stance)))
        return pairs

    reference_pairs = known_pairs(reference_annotations)
    model_pairs = known_pairs(model_annotations)
    reference_review = set(
        reference_annotations.loc[
            reference_annotations["concept_status"].eq("review"), "unit_id"
        ].astype(str)
    )
    model_review = set(
        model_annotations.loc[
            model_annotations["concept_status"].eq("review"), "unit_id"
        ].astype(str)
    )
    model_status = model_results.assign(
        unit_id=model_results["unit_id"].astype(str)
    ).set_index("unit_id")["status"].to_dict()

    rows: list[dict[str, Any]] = []
    for block in reference_blocks.itertuples(index=False):
        unit_id = str(block.unit_id)
        if block.resolution_status != "resolved" or not bool(block.evaluation_included):
            continue
        human = reference_pairs.get(unit_id, set())
        predicted = model_pairs.get(unit_id, set())
        human_concepts = {concept for concept, _ in human}
        predicted_concepts = {concept for concept, _ in predicted}
        status = model_status.get(unit_id)
        if status != "completed":
            comparison_status = "model_unavailable"
        elif unit_id in reference_review or unit_id in model_review:
            comparison_status = "concept_review_required"
        elif human == predicted:
            comparison_status = "concept_and_stance"
        elif human_concepts == predicted_concepts:
            comparison_status = "concept_only"
        else:
            comparison_status = "divergent"

        exact_pairs = human.intersection(predicted)
        common_concepts = human_concepts.intersection(predicted_concepts)
        row = {
            "comparison_schema_version": COMPARISON_SCHEMA_VERSION,
            "unit_id": unit_id,
            "comparison_status": comparison_status,
            "model_status": status or "missing",
            "reference_pairs": _canonical(human),
            "model_pairs": _canonical(predicted),
            "reference_concepts": _canonical(human_concepts),
            "model_concepts": _canonical(predicted_concepts),
            "exact_pair_count": len(exact_pairs),
            "common_concept_count": len(common_concepts),
            "reference_only_concept_count": len(human_concepts - predicted_concepts),
            "model_only_concept_count": len(predicted_concepts - human_concepts),
            "selection_weight": float(getattr(block, "selection_weight", 1.0) or 1.0),
        }
        for field in ANALYSIS_METADATA_FIELDS:
            if field in reference_blocks.columns:
                row[field] = getattr(block, field)
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_block_comparison(
    comparison: pd.DataFrame, group_by: list[str] | tuple[str, ...] = (),
) -> pd.DataFrame:
    """Return counts and weighted status shares, optionally within each group."""
    groups = list(group_by)
    if len(groups) != len(set(groups)):
        raise ValueError("group_by contiene dimensiones duplicadas")
    missing = sorted(set(groups).difference(comparison.columns))
    if missing:
        raise ValueError(f"comparison no contiene: {', '.join(missing)}")
    if comparison.empty:
        return pd.DataFrame(columns=[*groups,
            "comparison_status", "blocks", "weighted_blocks", "weighted_share"
        ])
    unknown = set(comparison["comparison_status"]) - COMPARISON_STATUSES
    if unknown:
        raise ValueError(f"Estados de comparación desconocidos: {sorted(unknown)}")
    summary = comparison.groupby(
        [*groups, "comparison_status"], as_index=False, dropna=False
    ).agg(
        blocks=("unit_id", "size"),
        weighted_blocks=("selection_weight", "sum"),
    )
    denominator = (
        summary.groupby(groups, dropna=False)["weighted_blocks"].transform("sum")
        if groups else summary["weighted_blocks"].sum()
    )
    summary["weighted_share"] = summary["weighted_blocks"] / denominator
    return summary.sort_values(
        [*groups, "comparison_status"], kind="stable"
    ).reset_index(drop=True)


def create_adjudication_queue(comparison: pd.DataFrame) -> pd.DataFrame:
    """Create a separate, single-reviewer queue without changing the blind reference."""
    required = {"unit_id", "comparison_status", "reference_pairs", "model_pairs"}
    missing = sorted(required.difference(comparison.columns))
    if missing:
        raise ValueError(f"comparison no contiene: {', '.join(missing)}")
    queue = comparison.loc[
        comparison["comparison_status"].isin([
            "concept_only", "divergent", "concept_review_required"
        ]),
        ["unit_id", "comparison_status", "reference_pairs", "model_pairs"],
    ].copy()
    queue["adjudication_status"] = "pending"
    queue["adjudicated_pairs"] = None
    queue["reason"] = None
    queue["reviewer"] = None
    queue["updated_at_utc"] = None
    return queue.reset_index(drop=True)


def validate_adjudication_queue(adjudications: pd.DataFrame) -> None:
    """Validate structured resolutions entered after computing primary metrics."""
    required = {
        "unit_id", "comparison_status", "reference_pairs", "model_pairs",
        "adjudication_status", "adjudicated_pairs", "reason", "reviewer",
    }
    missing = sorted(required.difference(adjudications.columns))
    if missing:
        raise ValueError(f"adjudications no contiene: {', '.join(missing)}")
    if adjudications["unit_id"].astype(str).duplicated().any():
        raise ValueError("adjudications contiene unit_id duplicados")
    unknown = set(adjudications["adjudication_status"]) - ADJUDICATION_STATUSES
    if unknown:
        raise ValueError(f"Estados de adjudicación desconocidos: {sorted(unknown)}")
    for row in adjudications.itertuples(index=False):
        if row.adjudication_status == "pending":
            continue
        if not isinstance(row.reason, str) or not row.reason.strip():
            raise ValueError(f"{row.unit_id}: la resolución requiere una razón")
        if not isinstance(row.reviewer, str) or not row.reviewer.strip():
            raise ValueError(f"{row.unit_id}: la resolución requiere identificar al revisor")
        if row.adjudication_status == "unresolved":
            if row.adjudicated_pairs not in (None, "", "null"):
                raise ValueError(
                    f"{row.unit_id}: un caso irresoluble no lleva pares adjudicados"
                )
            continue
        try:
            pairs = json.loads(row.adjudicated_pairs)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError(
                f"{row.unit_id}: adjudicated_pairs debe ser JSON"
            ) from exc
        if not isinstance(pairs, list):
            raise ValueError(f"{row.unit_id}: adjudicated_pairs debe ser una lista")
        normalized = set()
        for pair in pairs:
            if (
                not isinstance(pair, list)
                or len(pair) != 2
                or not all(isinstance(value, str) and value for value in pair)
                or pair[1] not in {"support", "oppose"}
            ):
                raise ValueError(f"{row.unit_id}: par adjudicado inválido")
            normalized.add((pair[0], pair[1]))
        if len(normalized) != len(pairs):
            raise ValueError(f"{row.unit_id}: pares adjudicados duplicados")
