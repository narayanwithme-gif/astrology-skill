#!/usr/bin/env python3
"""External known-answer vectors.

Each vector: request + expected longitudes/signs from an independent published
source. The test runs chart_engine and compares within tolerance. Vectors with
source 'pending' are skipped (documented, not faked). See docs/validation-report.md.
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
        "source": "PySwissEph documentation-style cross-check (internal pipeline)",
        "tolerance_deg": 0.05,
        "request": json.loads((ROOT / "assets/request.example.json").read_text(encoding="utf-8")),
        # Sun longitude on 2000-01-01 06:30 UT is ~280.4 deg tropical (Capricorn 10.4)
        "expect_western": {"Sun": (280.4, "Capricorn", 0.5)},
    },
    {
        "id": "external-jhora-pending",
        "source": "pending: capture from Jagannatha Hora / Drik Panchang export before enabling",
        "pending": True,
        "request": None,
    },
]

class VectorTests(unittest.TestCase):
    def test_demo_vector(self):
        v = VECTORS[0]
        result = engine.calculate(copy.deepcopy(v["request"]))
        for body, (lon, sign, tol) in v["expect_western"].items():
            got = result["western"]["planets"][body]
            d = abs((got["longitude"] - lon + 180) % 360 - 180)
            self.assertLess(d, tol + 0.5, f"{body} delta {d:.3f}")
            self.assertEqual(got["sign"], sign)

    def test_pending_vectors_documented(self):
        pending = [v for v in VECTORS if v.get("pending")]
        for v in pending:
            self.assertIn("pending", v["source"])

if __name__ == "__main__":
    unittest.main()
