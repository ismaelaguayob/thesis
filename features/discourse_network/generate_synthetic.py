#!/usr/bin/env python3
"""Generate a clearly labelled synthetic signed discourse network for the poster.

The figure is derived from a small, deterministic actor-by-concept stance matrix.
Actor pairs receive positive weight when they take the same stance on a shared
concept and negative weight when their stances oppose one another. A two-group
signed partition is selected by exhaustive maximization of satisfied edge
weights. None of the actors, ties, or communities are empirical results.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import shutil
import subprocess
from html import escape
from pathlib import Path


CONCEPTS = (
    "Individual ownership",
    "Individual capitalization",
    "Contributory reciprocity",
    "Control",
    "Financial sustainability",
    "Solidarity",
    "Pension adequacy",
    "Need",
    "Public responsibility",
)

# +1 = support, -1 = opposition, 0 = no observed position.
ACTOR_STANCES = {
    "Senator A": (1, 1, 1, 1, 1, -1, 0, -1, 0),
    "Deputy B": (1, 1, 1, 1, 1, -1, -1, -1, -1),
    "AFP Association": (1, 1, 1, 0, 1, -1, 0, -1, -1),
    "Senator B": (1, 1, 1, 0, 1, 0, 1, 0, 0),
    "Deputy A": (1, 1, 1, 1, 1, -1, 0, -1, 0),
    "Deputy C": (-1, -1, -1, -1, 0, 1, 1, 1, 1),
    "Deputy D": (-1, -1, -1, -1, -1, 1, 1, 1, 1),
    "Trade Union": (-1, -1, -1, 0, 0, 1, 1, 1, 1),
    "Pensioners' Assoc.": (0, -1, 0, -1, 0, 1, 1, 1, 1),
    "Senator D": (0, -1, 0, 0, 1, 1, 1, 1, 1),
    "Labour Minister": (1, 1, 1, 0, 1, 1, 1, 1, 1),
    "Senator C": (1, 0, 1, 0, 1, 1, 1, 1, 0),
}

WIDTH = 2400
HEIGHT = 1800
NODE_RADIUS = 98


def pair_weight(first: tuple[int, ...], second: tuple[int, ...]) -> float:
    """Return activity-normalized signed agreement in the range [-1, 1]."""

    shared_products = [a * b for a, b in zip(first, second) if a and b]
    if not shared_products:
        return 0.0
    directional_balance = sum(shared_products) / len(shared_products)
    overlap_factor = math.sqrt(len(shared_products) / len(CONCEPTS))
    return directional_balance * overlap_factor


def project_actor_network() -> dict[tuple[str, str], float]:
    edges: dict[tuple[str, str], float] = {}
    for first, second in itertools.combinations(ACTOR_STANCES, 2):
        edges[(first, second)] = pair_weight(
            ACTOR_STANCES[first], ACTOR_STANCES[second]
        )
    return edges


def detect_two_communities(
    actors: list[str], edges: dict[tuple[str, str], float]
) -> dict[str, int]:
    """Find the binary signed partition with the highest satisfied-edge score."""

    anchor = actors[0]
    remaining = actors[1:]
    best_score = float("-inf")
    best_assignment: dict[str, int] | None = None

    for bits in itertools.product((0, 1), repeat=len(remaining)):
        assignment = {anchor: 0, **dict(zip(remaining, bits))}
        if not any(bits):
            continue
        score = 0.0
        for (first, second), weight in edges.items():
            same_group = assignment[first] == assignment[second]
            score += weight if same_group else -weight
        if score > best_score:
            best_score = score
            best_assignment = assignment

    if best_assignment is None:
        raise RuntimeError("Could not identify a non-empty signed partition")
    return best_assignment


def detect_bridge_actors(
    actors: list[str],
    edges: dict[tuple[str, str], float],
    communities: dict[str, int],
    count: int = 2,
) -> list[str]:
    """Rank actors by positive connection strength to both communities."""

    scores: list[tuple[float, str]] = []
    for actor in actors:
        strength = [0.0, 0.0]
        for other in actors:
            if actor == other:
                continue
            key = tuple(sorted((actor, other), key=actors.index))
            weight = edges[key]
            if weight > 0:
                strength[communities[other]] += weight
        bridge_score = math.sqrt(strength[0] * strength[1])
        scores.append((bridge_score, actor))
    return [actor for score, actor in sorted(scores, reverse=True)[:count] if score > 0]


def circular_positions(
    names: list[str], center_x: float, center_y: float, radius_x: float, radius_y: float
) -> dict[str, tuple[float, float]]:
    positions: dict[str, tuple[float, float]] = {}
    start_angle = -math.pi / 2
    for index, name in enumerate(names):
        angle = start_angle + 2 * math.pi * index / len(names)
        positions[name] = (
            center_x + radius_x * math.cos(angle),
            center_y + radius_y * math.sin(angle),
        )
    return positions


def build_positions(
    actors: list[str], communities: dict[str, int], bridges: list[str]
) -> dict[str, tuple[float, float]]:
    left_group = [a for a in actors if communities[a] == 0 and a not in bridges]
    right_group = [a for a in actors if communities[a] == 1 and a not in bridges]

    positions = circular_positions(left_group, 600, 810, 350, 455)
    positions.update(circular_positions(right_group, 1800, 810, 350, 455))

    bridge_y = [665, 1030]
    for index, actor in enumerate(bridges):
        positions[actor] = (1200, bridge_y[index])
    return positions


def select_display_edges(
    actors: list[str], edges: dict[tuple[str, str], float], bridges: list[str]
) -> list[tuple[str, str, float]]:
    positive = sorted(
        ((a, b, w) for (a, b), w in edges.items() if w >= 0.27),
        key=lambda item: item[2],
        reverse=True,
    )
    negative = sorted(
        ((a, b, w) for (a, b), w in edges.items() if w <= -0.38),
        key=lambda item: item[2],
    )

    selected: dict[tuple[str, str], tuple[str, str, float]] = {}
    degree = {actor: 0 for actor in actors}

    for edge in positive:
        first, second, _ = edge
        if degree[first] < 4 or degree[second] < 4 or first in bridges or second in bridges:
            selected[(first, second)] = edge
            degree[first] += 1
            degree[second] += 1
        if len([e for e in selected.values() if e[2] > 0]) >= 22:
            break

    for edge in negative[:12]:
        selected[(edge[0], edge[1])] = edge

    return sorted(selected.values(), key=lambda item: item[2])


def split_label(label: str) -> list[str]:
    if len(label) <= 11:
        return [label]
    words = label.split()
    if len(words) == 2:
        return words
    midpoint = math.ceil(len(words) / 2)
    return [" ".join(words[:midpoint]), " ".join(words[midpoint:])]


def is_parliamentarian(actor: str) -> bool:
    return actor.startswith(("Senator ", "Deputy "))


def svg_text(
    x: float,
    y: float,
    content: str,
    *,
    size: int,
    weight: int = 400,
    fill: str = "#172033",
    anchor: str = "middle",
    opacity: float = 1.0,
) -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="DejaVu Sans, Arial, sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" opacity="{opacity}">'
        f"{escape(content)}</text>"
    )


def render_svg(
    output_path: Path,
    actors: list[str],
    edges: dict[tuple[str, str], float],
    communities: dict[str, int],
    bridges: list[str],
) -> None:
    positions = build_positions(actors, communities, bridges)
    displayed_edges = select_display_edges(actors, edges, bridges)
    colors = {0: "#981B3A", 1: "#1F5A85"}
    pale_colors = {0: "#F7E7EB", 1: "#E6F0F6"}

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" '
            f'height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">'
        ),
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<rect x="385" y="25" width="1630" height="88" rx="44" fill="#FFF3CD"/>',
        svg_text(
            1200,
            82,
            "ILLUSTRATIVE NETWORK · SYNTHETIC DATA · NOT EMPIRICAL RESULTS",
            size=38,
            weight=700,
            fill="#6B4F00",
        ),
        (
            '<ellipse cx="600" cy="810" rx="500" ry="575" '
            f'fill="{pale_colors[0]}" stroke="{colors[0]}" stroke-width="3" '
            'stroke-opacity="0.20"/>'
        ),
        (
            '<ellipse cx="1800" cy="810" rx="500" ry="575" '
            f'fill="{pale_colors[1]}" stroke="{colors[1]}" stroke-width="3" '
            'stroke-opacity="0.20"/>'
        ),
        svg_text(600, 176, "DETECTED COMMUNITY 1", size=36, weight=700, fill=colors[0]),
        svg_text(1800, 176, "DETECTED COMMUNITY 2", size=36, weight=700, fill=colors[1]),
    ]

    # Draw ties behind nodes: negative first, then positive.
    for first, second, weight in displayed_edges:
        if weight >= 0:
            continue
        x1, y1 = positions[first]
        x2, y2 = positions[second]
        width = 2.5 + 6 * abs(weight)
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#B4232F" stroke-width="{width:.1f}" stroke-dasharray="14 11" '
            'stroke-linecap="round" opacity="0.30"/>'
        )

    for first, second, weight in displayed_edges:
        if weight <= 0:
            continue
        x1, y1 = positions[first]
        x2, y2 = positions[second]
        width = 2.5 + 7 * abs(weight)
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#58677A" stroke-width="{width:.1f}" '
            'stroke-linecap="round" opacity="0.47"/>'
        )

    for actor in actors:
        x, y = positions[actor]
        community = communities[actor]
        is_bridge = actor in bridges
        if is_parliamentarian(actor):
            if is_bridge:
                parts.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_RADIUS + 11}" '
                    'fill="none" stroke="#F59E0B" stroke-width="12"/>'
                )
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_RADIUS}" '
                f'fill="{colors[community]}" stroke="#FFFFFF" stroke-width="6"/>'
            )
        else:
            node_width = 230
            node_height = 174
            if is_bridge:
                parts.append(
                    f'<rect x="{x - node_width / 2 - 11:.1f}" '
                    f'y="{y - node_height / 2 - 11:.1f}" '
                    f'width="{node_width + 22}" height="{node_height + 22}" rx="38" '
                    'fill="none" stroke="#F59E0B" stroke-width="12"/>'
                )
            parts.append(
                f'<rect x="{x - node_width / 2:.1f}" y="{y - node_height / 2:.1f}" '
                f'width="{node_width}" height="{node_height}" rx="32" '
                f'fill="{colors[community]}" stroke="#FFFFFF" stroke-width="6"/>'
            )
        label_lines = split_label(actor)
        line_height = 40
        first_y = y - (len(label_lines) - 1) * line_height / 2 + 13
        for line_index, line in enumerate(label_lines):
            parts.append(
                svg_text(
                    x,
                    first_y + line_index * line_height,
                    line,
                    size=34 if len(line) > 9 else 38,
                    weight=700,
                    fill="#FFFFFF",
                )
            )

    # Legend and provenance.
    parts.extend(
        [
            '<rect x="140" y="1455" width="2120" height="240" rx="34" fill="#F8FAFC" '
            'stroke="#CBD5E1" stroke-width="3"/>',
            '<circle cx="250" cy="1525" r="32" fill="#334155"/>',
            svg_text(300, 1538, "senator / deputy", size=32, anchor="start"),
            '<rect x="675" y="1490" width="80" height="70" rx="17" fill="#334155"/>',
            svg_text(785, 1538, "government / invited actor", size=32, anchor="start"),
            f'<circle cx="1420" cy="1525" r="29" fill="{colors[0]}"/>',
            f'<circle cx="1460" cy="1525" r="29" fill="{colors[1]}"/>',
            svg_text(1510, 1538, "detected community", size=32, anchor="start"),
            '<circle cx="2075" cy="1525" r="36" fill="#FFFFFF" stroke="#F59E0B" stroke-width="10"/>',
            svg_text(2130, 1538, "bridge", size=32, anchor="start"),
            '<line x1="480" y1="1630" x2="650" y2="1630" stroke="#58677A" '
            'stroke-width="10" stroke-linecap="round" opacity="0.65"/>',
            svg_text(700, 1642, "congruence", size=32, anchor="start"),
            '<line x1="1210" y1="1630" x2="1380" y2="1630" stroke="#B4232F" '
            'stroke-width="9" stroke-dasharray="18 14" stroke-linecap="round" opacity="0.65"/>',
            svg_text(1430, 1642, "conflict", size=32, anchor="start"),
        ]
    )
    parts.append("</svg>")
    output_path.write_text("\n".join(parts), encoding="utf-8")


def write_synthetic_matrix(output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("actor", *CONCEPTS))
        for actor, stances in ACTOR_STANCES.items():
            writer.writerow((actor, *stances))


def export_png(svg_path: Path, png_path: Path, export_width: int = 3600) -> None:
    inkscape = shutil.which("inkscape")
    if not inkscape:
        raise RuntimeError("Inkscape is required to export the PNG preview")
    completed = subprocess.run(
        [
            inkscape,
            str(svg_path),
            f"--export-filename={png_path}",
            f"--export-width={export_width}",
            "--export-background=#ffffff",
            "--export-background-opacity=255",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Inkscape PNG export failed: {completed.stderr.strip()}")


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=project_root / "output" / "figures",
        help="Directory for the SVG and PNG outputs.",
    )
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=project_root / "output" / "tables",
        help="Directory for the synthetic stance matrix.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.figures_dir.mkdir(parents=True, exist_ok=True)
    args.tables_dir.mkdir(parents=True, exist_ok=True)
    actors = list(ACTOR_STANCES)
    edges = project_actor_network()
    communities = detect_two_communities(actors, edges)
    bridges = detect_bridge_actors(actors, edges, communities)

    svg_path = args.figures_dir / "synthetic_signed_discourse_network.svg"
    png_path = args.figures_dir / "synthetic_signed_discourse_network.png"
    matrix_path = args.tables_dir / "synthetic_actor_concept_matrix.csv"

    render_svg(svg_path, actors, edges, communities, bridges)
    write_synthetic_matrix(matrix_path)
    export_png(svg_path, png_path)

    print(f"SVG: {svg_path}")
    print(f"PNG: {png_path}")
    print(f"Synthetic matrix: {matrix_path}")
    print(f"Bridge actors: {', '.join(bridges)}")


if __name__ == "__main__":
    main()
