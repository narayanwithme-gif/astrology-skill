#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Export standalone SVG chart files from a calculated chart.json.

The chart engine embeds its SVG diagrams inside charts.html. This module writes
those same diagrams as individual .svg files, so they can be used in documents,
websites, or graphic tools, similar to the kerykeion library's SVG output.

Usage:
    python scripts/svg_export.py --chart /path/to/chart.json --out /path/to/svg-dir
    python scripts/chart_engine.py --input request.json --out report --svg
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

MODULE_DIR = str(Path(__file__).resolve().parent)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

from chart_engine import north, south, wheel  # noqa: E402

SVG_NS = 'xmlns="http://www.w3.org/2000/svg"'


def as_standalone(svg_markup: str) -> str:
    """Add an XML declaration and SVG namespace so a fragment is a valid .svg file."""
    if not svg_markup.lstrip().startswith("<svg"):
        raise ValueError("Expected an <svg> fragment")
    # Inject the namespace once on the root element only.
    rooted = svg_markup.replace("<svg ", f"<svg {SVG_NS} ", 1)
    if SVG_NS not in rooted:
        rooted = svg_markup.replace("<svg>", f"<svg {SVG_NS}>", 1)
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + rooted


def svg_files(data: dict) -> list[tuple[str, str]]:
    """Return (filename, svg_text) pairs for every chart diagram in a report."""
    western = data["western"]
    jyotisha = data["jyotisha"]
    files: list[tuple[str, str]] = [
        ("western-wheel.svg", as_standalone(wheel(western))),
    ]
    for key, label in (("D1", "d1"), ("D9", "d9"), ("D10", "d10")):
        chart = jyotisha if key == "D1" else jyotisha[key]
        title = f"{key} Rashi"
        files.append((f"{label}-north.svg", as_standalone(north(chart, title))))
        files.append((f"{label}-south.svg", as_standalone(south(chart, title))))
    return files


def export(chart_json: Path, out_dir: Path, *, overwrite: bool = False) -> list[Path]:
    """Write standalone SVG files into out_dir. Returns paths written."""
    data = json.loads(chart_json.read_text(encoding="utf-8-sig"))
    files = svg_files(data)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, content in files:
        target = out_dir / name
        if target.exists() and not overwrite:
            raise ValueError(f"Refusing to overwrite existing SVG: {target}")
        target.write_text(content, encoding="utf-8")
        written.append(target)
    return written


def cli() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--chart", required=True, type=Path, help="Path to chart.json")
    ap.add_argument("--out", required=True, type=Path, help="Directory for .svg files")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    args = ap.parse_args()
    try:
        written = export(args.chart, args.out, overwrite=args.overwrite)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(f"svg_export error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "exported", "files": [str(p.resolve()) for p in written]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
