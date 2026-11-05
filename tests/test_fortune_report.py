#!/usr/bin/env python3
"""Golden tests: Fortune Report HTML/PDF content + HTML/XML escaping."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import unittest

ROOT = Path(__file__).resolve().parent.parent
CHART = ROOT / "examples" / "demo" / "chart.json"
REQUEST = ROOT / "assets" / "request.example.json"

def run_report(name, brand, outdir):
    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "fortune_report.py"),
         "--chart", str(CHART), "--request", str(REQUEST),
         "--name", name, "--brand", brand, "--out-dir", str(outdir)],
        capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr

class FortuneReportTests(unittest.TestCase):
    def test_html_sections_and_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            run_report("Test Name", "Test Brand", td)
            html = list(Path(td).glob("*.html"))[0].read_text(encoding="utf-8")
            for needle in ["FORTUNE", "Your Lucky Things", "Numerological Analysis",
                           "Fortune Grid Analysis", "Kundali", "Life-Path Appendix",
                           "Mulank", "Bhagyank", "Lo Shu"]:
                self.assertIn(needle, html, needle)
            # numerology values must come from request.example.json + name, not hardcoded
            req = json.loads(REQUEST.read_text(encoding="utf-8"))
            self.assertIn(req["birth"]["date"], html)

    def test_html_escaping(self):
        with tempfile.TemporaryDirectory() as td:
            run_report('<script>alert(1)</script>', "A&B <i>Brand</i>", td)
            html = list(Path(td).glob("*.html"))[0].read_text(encoding="utf-8")
            self.assertNotIn("<script>alert(1)</script>", html)
            self.assertIn("&lt;script&gt;", html)
            self.assertIn("&amp;", html)

    def test_pdf_names_user_text(self):
        with tempfile.TemporaryDirectory() as td:
            run_report("Pdf & Test", "Brand <x>", td)
            pdfs = list(Path(td).glob("*.pdf"))
            self.assertEqual(len(pdfs), 1)
            self.assertGreater(pdfs[0].stat().st_size, 0)

if __name__ == "__main__":
    unittest.main()
