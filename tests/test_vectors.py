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


def validate_external_vector(vector):
    """Reject incomplete external vectors before they can be treated as evidence."""
    required = {
        "id", "source", "source_version", "retrieved", "request",
        "settings", "expected", "tolerance_deg", "license_note",
    }
    missing = required - vector.keys()
    if missing:
        raise ValueError(f"External vector is missing: {', '.join(sorted(missing))}")
    if vector.get("pending"):
        raise ValueError("Pending vectors cannot be validated as external references")
    if not isinstance(vector["expected"], dict) or not vector["expected"]:
        raise ValueError("External vector expected values must be a non-empty object")
    if not isinstance(vector["tolerance_deg"], (int, float)) or vector["tolerance_deg"] <= 0:
        raise ValueError("External vector tolerance_deg must be positive")
    if not vector["source"].strip() or not vector["source_version"].strip():
        raise ValueError("External vector source and source_version are required")


def run_external_vector(vector):
    """Calculate an externally sourced fixture; callers must keep source metadata."""
    validate_external_vector(vector)
    result = engine.calculate(copy.deepcopy(vector["request"]))
    for path, expected in vector["expected"].items():
        parts = path.split(".")
        actual = result
        for part in parts:
            actual = actual[part]
        if isinstance(expected, (int, float)):
            delta = abs((actual - expected + 180) % 360 - 180)
            if delta > vector["tolerance_deg"]:
                raise AssertionError(f"{path}: expected {expected}, got {actual}, delta {delta}")
        elif actual != expected:
            raise AssertionError(f"{path}: expected {expected!r}, got {actual!r}")
    return result


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

    def test_external_vector_requires_provenance_and_expected_values(self):
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_external_vector({"id": "incomplete"})

    def test_pending_vector_cannot_be_counted_as_validation(self):
        fixture = {
            "id": "pending", "source": "JHora", "source_version": "unknown",
            "retrieved": "2026-01-01", "request": {}, "settings": {},
            "expected": {"western.planets.Sun.longitude": 1.0},
            "tolerance_deg": 0.01, "license_note": "fictional test data", "pending": True,
        }
        with self.assertRaisesRegex(ValueError, "Pending"):
            validate_external_vector(fixture)


if __name__ == "__main__":
    unittest.main()
