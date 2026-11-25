#!/usr/bin/env python3
"""Validation CLI smoke tests across configured sidereal modes."""

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("chart_engine", ROOT / "scripts" / "chart_engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)
EXAMPLE = json.loads((ROOT / "assets" / "request.example.json").read_text(encoding="utf-8"))


class ValidationTests(unittest.TestCase):
    def test_mode_agreement_uses_chart_ayanamsha(self):
        for ayanamsha in ("lahiri", "raman", "krishnamurti", "drik"):
            with self.subTest(ayanamsha=ayanamsha), tempfile.TemporaryDirectory() as temp:
                request = copy.deepcopy(EXAMPLE)
                request["settings"]["ayanamsha"] = ayanamsha
                chart = engine.calculate(request)
                path = Path(temp) / "chart.json"
                path.write_text(json.dumps(chart), encoding="utf-8")
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "validate_engine.py"),
                        "--chart",
                        str(path),
                        "--tol",
                        "0.01",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=ROOT,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                report = json.loads(result.stdout)
                self.assertEqual(report["sidereal_mode"], ayanamsha)
                self.assertLessEqual(report["worst_delta_deg"], 0.01)


if __name__ == "__main__":
    unittest.main()
