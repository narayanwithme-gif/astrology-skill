#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Rebuild the fictional example and README diagram."""

import json
from pathlib import Path

import chart_engine as engine


def main():
    root = Path(__file__).resolve().parents[1]
    request = json.loads((root / "assets/request.example.json").read_text(encoding="utf-8"))
    data = engine.calculate(request)
    target = root / "examples/demo"
    target.mkdir(parents=True, exist_ok=True)
    (target / "chart.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (target / "charts.html").write_text(engine.atlas(data), encoding="utf-8")
    image = root / "docs/images/charts.svg"
    image.parent.mkdir(parents=True, exist_ok=True)
    panels = [
        engine.wheel(data["western"]),
        engine.north(data["jyotisha"], "D1 Rashi"),
        engine.south(data["jyotisha"], "D1 Rashi"),
    ]
    panels = [
        panel.replace(
            "<svg ", '<svg x="' + str(i * 420 + 10) + '" y="50" width="400" height="400" ', 1
        )
        for i, panel in enumerate(panels)
    ]
    labels = ["Western tropical", "D1 — north Indian", "D1 — south Indian"]
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="470" viewBox="0 0 1280 470" role="img" aria-labelledby="title"><title id="title">Fictional Western and Jyotisha chart examples</title><rect width="1280" height="470" fill="#faf8f2"/><g font-family="system-ui,sans-serif" fill="#243247" color="#243247">'
    svg += "".join(
        engine.text_svg(i * 420 + 210, 30, [label], 18) for i, label in enumerate(labels)
    )
    svg += "".join(panels) + "</g></svg>"
    image.write_text(svg, encoding="utf-8")
    print("Rebuilt examples/demo and docs/images/charts.svg from fictional input")


if __name__ == "__main__":
    main()
