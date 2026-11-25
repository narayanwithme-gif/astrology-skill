#!/usr/bin/env python3
"""Render offline report visuals from JSON or from calculated astrology chart data."""

import argparse
import json
import math
from datetime import date, datetime
from html import escape
from pathlib import Path

VISUAL_CSS = """
.rv {color:#24213a; background:#fff; border:1px solid #d7d3e1; border-top:3px solid #574179;
     margin:1.25rem 0; padding:clamp(.8rem,3vw,1.5rem); font: .94rem/1.5 system-ui,sans-serif}
.rv h2,.rv h3 {color:#30214c; font:700 1.3rem/1.25 Georgia,serif;
                        margin:0 0 .5rem; border:0; padding:0}
.rv p {margin:.5rem 0; overflow-wrap:anywhere}
.rv-note {color:#534b62; font-size:.88rem}
.rv-table {width:100%; border-collapse:collapse; margin:.75rem 0 0; background:#fff;
           font-size:.88rem; font-variant-numeric:tabular-nums}
.rv-table th,.rv-table td {width:auto; border:0; border-bottom:1px solid #e6e3ed;
                          padding:.5rem .6rem; text-align:left; vertical-align:middle;
                          overflow-wrap:anywhere}
.rv-table thead th {color:#30214c; background:#f0ecf6; font-weight:700}
.rv-table tbody th {font-weight:600; background:#fff}
.rv-table .rv-number {text-align:right; white-space:nowrap}
.rv-table .rv-track-cell {width:40%}
.rv-table-scroll {overflow-x:auto}
.rv-track {display:block; position:relative; height:.55rem; width:100%; background:#e9e5ef}
.rv-fill {display:block; position:absolute; height:100%; background:#574179; print-color-adjust:exact}
.rv-steps {padding-left:1.7rem; margin:.75rem 0 0}
.rv-steps li {margin:.45rem 0; padding:.6rem .8rem; background:#f4f1f8; overflow-wrap:anywhere}
.rv-steps span {display:block; color:#534b62}
@page {size:A4; margin:14mm}
@media print {
    .rv {break-inside:auto}
    .rv h2,.rv h3,.rv p {break-after:avoid}
    .rv-table {break-inside:auto}
    .rv-table tr,.rv-steps li {break-inside:avoid}
    .rv-table thead {display:table-header-group}
    .rv-track,.rv-fill {print-color-adjust:exact}
}
"""


def _number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    return value


def _percent(value, maximum):
    return (value / maximum) * 100


def _track(width, offset=0):
    return (
        '<span class="rv-track" aria-hidden="true">'
        f'<span class="rv-fill" style="left:{offset:.6f}%;width:{width:.6f}%"></span></span>'
    )


def _table(columns, rows, numeric_columns=()):
    headings = "".join(f'<th scope="col">{escape(str(column))}</th>' for column in columns)
    body = []
    for row in rows:
        if len(row) != len(columns):
            raise ValueError("Every table row must have the same number of cells as columns")
        cells = []
        for index, cell in enumerate(row):
            css = ' class="rv-number"' if index in numeric_columns else ""
            if index == 0:
                cells.append(f'<th scope="row"{css}>{cell}</th>')
            else:
                cells.append(f"<td{css}>{cell}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        '<div class="rv-table-scroll"><table class="rv-table"><thead><tr>'
        + headings
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def _percentage_bars(rows):
    body = []
    for row in rows:
        value = _number(row["value"], "value")
        maximum = _number(row["maximum"], "maximum")
        if maximum <= 0 or not 0 <= value <= maximum:
            raise ValueError("Percentage bars require 0 <= value <= maximum and maximum > 0")
        percent = _percent(value, maximum)
        body.append(
            (
                escape(str(row["label"])),
                f"{value} / {maximum}",
                f"{percent:.1f}%",
                _track(percent),
            )
        )
    return _table(["Category", "Value / base", "Percent", "Share of base"], body, (1, 2))


def _timeline(rows):
    intervals = [
        (row, date.fromisoformat(row["start"]), date.fromisoformat(row["end"])) for row in rows
    ]
    if any(end <= start for _, start, end in intervals):
        raise ValueError("Timeline end dates must follow their start dates")
    first = min(start for _, start, _ in intervals)
    last = max(end for _, _, end in intervals)
    span = (last - first).days
    body = []
    for row, start, end in sorted(intervals, key=lambda interval: interval[1]):
        body.append(
            (
                escape(str(row["label"])),
                start.isoformat(),
                end.isoformat(),
                _track(_percent((end - start).days, span), _percent((start - first).days, span)),
            )
        )
    return _table(["Period", "Start", "End", "Position on timeline"], body)


def _steps(rows):
    items = []
    for row in rows:
        label = escape(str(row["label"]))
        detail = escape(str(row.get("detail", "")))
        items.append(
            f"<li><strong>{label}</strong>{f'<span>{detail}</span>' if detail else ''}</li>"
        )
    return '<ol class="rv-steps">' + "".join(items) + "</ol>"


def render_section(section, *, heading="h2"):
    """Render a typed visual section. Escape all report labels and table data."""
    if heading not in {"h2", "h3"}:
        raise ValueError("Use h2 or h3 for visual headings")
    kind = section["type"]
    rows = section["rows"]
    if not rows:
        raise ValueError("Each visual section requires at least one row")
    if kind == "percentage-bars":
        visual = _percentage_bars(rows)
    elif kind == "timeline":
        visual = _timeline(rows)
    elif kind == "steps":
        visual = _steps(rows)
    elif kind == "table":
        columns = section["columns"]
        if not columns:
            raise ValueError("Tables require at least one column")
        visual = _table(
            columns,
            [[escape(str(cell)) for cell in row] for row in rows],
            section.get("numeric_columns", ()),
        )
    else:
        raise ValueError(f"Unsupported visual type: {kind}")

    title = escape(str(section["title"]))
    note = escape(str(section.get("note", "")))
    note_html = f'<p class="rv-note">{note}</p>' if note else ""
    return f'<section class="rv"><{heading}>{title}</{heading}>{note_html}{visual}</section>'


def render_report(spec):
    """Render a complete, script-free HTML report."""
    title = escape(str(spec["title"]))
    sections = "".join(render_section(section) for section in spec["sections"])
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{title}</title><style>"
        "body{margin:0;background:#f5f3f8;color:#24213a;font:1rem/1.5 system-ui,sans-serif}"
        "main{max-width:960px;margin:auto;padding:clamp(12px,4vw,48px)}"
        "h1{font:700 clamp(1.85rem,4vw,3rem)/1.15 Georgia,serif;color:#30214c;margin:0 0 1rem}"
        "@media print{body{background:#fff}main{max-width:none;padding:0}}"
        f"{VISUAL_CSS}</style></head><body><main><h1>{title}</h1>{sections}</main></body></html>"
    )


def house_distribution(jyotisha):
    counts = [0] * 12
    for planet in jyotisha["planets"].values():
        counts[planet["house"] - 1] += 1
    total = sum(counts)
    return {
        "type": "percentage-bars",
        "title": "Jyotisha D1 house distribution",
        "note": f"Share of the {total} plotted bodies in each whole-sign house.",
        "rows": [
            {"label": f"House {house}", "value": count, "maximum": total}
            for house, count in enumerate(counts, start=1)
        ],
    }


def vimshottari_timeline(vimshottari):
    return {
        "type": "timeline",
        "title": "Vimshottari Mahadasha timeline",
        "note": "Calculated period boundaries shown as UTC dates.",
        "rows": [
            {
                "label": row["lord"],
                "start": datetime.fromisoformat(row["start_utc"]).date().isoformat(),
                "end": datetime.fromisoformat(row["end_utc"]).date().isoformat(),
            }
            for row in vimshottari["mahadashas"]
        ],
    }


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True, help="Visual report JSON")
    parser.add_argument("--out", type=Path, required=True, help="Output HTML path")
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        document = render_report(spec)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        with args.out.open("x", encoding="utf-8") as output:
            output.write(document)
    except (KeyError, ValueError, TypeError, OSError, OverflowError) as exc:
        parser.error(str(exc))
    print(f"written: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
