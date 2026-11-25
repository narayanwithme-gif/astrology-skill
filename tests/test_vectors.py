#!/usr/bin/env python3
"""Regression snapshots and placeholders for external known-answer vectors.

The demo snapshot is an internal regression check, not an independent accuracy
source. External vectors stay pending until their source, settings, and expected
values can be documented and reviewed. See docs/validation-report.md.
"""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("chart_engine", ROOT / "scripts/chart_engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)

VECTORS = [
    {
        "id": "demo-2000-01-01-delhi",
        "source": "examples/demo/chart.json (project-generated regression snapshot; not independent)",
        "tolerance_deg": 0.000001,
        "request": json.loads((ROOT / "assets/request.example.json").read_text(encoding="utf-8")),
        "expect_western": {"Sun": (280.1353021338655, "Capricorn", 0.000001)},
    },
    {
        "id": "external-jhora-pending",
        "source": "pending: capture from Jagannatha Hora / Drik Panchang export before enabling",
        "pending": True,
        "request": None,
    },
]


class VectorTests(unittest.TestCase):
    def test_demo_regression_snapshot(self):
        v = VECTORS[0]
        result = engine.calculate(copy.deepcopy(v["request"]))
        for body, (lon, sign, tol) in v["expect_western"].items():
            got = result["western"]["planets"][body]
            d = abs((got["longitude"] - lon + 180) % 360 - 180)
            self.assertLessEqual(d, tol, f"{body} delta {d:.8f}")
            self.assertEqual(got["sign"], sign)

    def test_pending_vectors_documented(self):
        pending = [v for v in VECTORS if v.get("pending")]
        for v in pending:
            self.assertIn("pending", v["source"])


if __name__ == "__main__":
    unittest.main()
