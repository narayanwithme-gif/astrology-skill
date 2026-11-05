#!/usr/bin/env python3
"""Validation harness test: dual-engine drift within tolerance."""
import json
import subprocess
import sys
from pathlib import Path

import unittest

ROOT = Path(__file__).resolve().parent.parent
CHART = ROOT / "examples" / "demo" / "chart.json"

class ValidationTests(unittest.TestCase):
    def test_drift_within_tolerance(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_engine.py"),
             "--chart", str(CHART), "--tol", "0.01"],
            capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        data = json.loads(r.stdout)
        self.assertLessEqual(data["worst_delta_deg"], 0.01)

if __name__ == "__main__":
    unittest.main()
