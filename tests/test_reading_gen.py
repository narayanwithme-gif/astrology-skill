#!/usr/bin/env python3
"""Golden test: deterministic reading is byte-identical across runs."""
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import unittest

ROOT = Path(__file__).resolve().parent.parent
CHART = ROOT / "examples" / "demo" / "chart.json"
REQUEST = ROOT / "assets" / "request.example.json"

class ReadingGenTests(unittest.TestCase):
    def test_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            outs = []
            for i in (1, 2):
                out = Path(td) / f"r{i}.md"
                r = subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "reading_gen.py"),
                     "--chart", str(CHART), "--request", str(REQUEST),
                     "--out", str(out)],
                    capture_output=True, text=True, cwd=ROOT)
                self.assertEqual(r.returncode, 0, r.stderr)
                outs.append(hashlib.sha256(out.read_bytes()).hexdigest())
            self.assertEqual(outs[0], outs[1])
            text = (Path(td) / "r1.md").read_text(encoding="utf-8")
            for needle in ["## 1.", "## 4.", "## 6.", "## 8.", "## 11."]:
                self.assertIn(needle, text, needle)

if __name__ == "__main__":
    unittest.main()
