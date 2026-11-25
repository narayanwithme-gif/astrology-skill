# SPDX-License-Identifier: AGPL-3.0-or-later
"""Standalone SVG export behavior with fictional input."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("chart_engine", ROOT / "scripts/chart_engine.py")
engine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(engine)
SVG_SPEC = importlib.util.spec_from_file_location("svg_export", ROOT / "scripts/svg_export.py")
svg_export = importlib.util.module_from_spec(SVG_SPEC)
SVG_SPEC.loader.exec_module(svg_export)
EXAMPLE = json.loads((ROOT / "assets/request.example.json").read_text(encoding="utf-8"))


class SvgExportTests(unittest.TestCase):
    def test_svg_files_are_valid_standalone_files(self):
        data = engine.calculate(EXAMPLE)
        files = dict(svg_export.svg_files(data))
        expected = {
            "western-wheel.svg",
            "d1-north.svg", "d1-south.svg",
            "d9-north.svg", "d9-south.svg",
            "d10-north.svg", "d10-south.svg",
        }
        self.assertEqual(set(files), expected)
        for name, content in files.items():
            with self.subTest(name=name):
                self.assertTrue(content.startswith('<?xml version="1.0"'))
                self.assertIn('xmlns="http://www.w3.org/2000/svg"', content)
                self.assertIn("<svg ", content)
                self.assertTrue(content.rstrip().endswith("</svg>"))

    def test_export_writes_files_and_refuses_overwrite(self):
        data = engine.calculate(EXAMPLE)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            chart = out / "chart.json"
            chart.write_text(
                json.dumps(data, ensure_ascii=False, allow_nan=False), encoding="utf-8"
            )
            target = out / "svg"
            written = svg_export.export(chart, target)
            self.assertEqual(len(written), 7)
            self.assertTrue(all(p.exists() and p.stat().st_size > 0 for p in written))
            with self.assertRaises(ValueError):
                svg_export.export(chart, target)
            written_again = svg_export.export(chart, target, overwrite=True)
            self.assertEqual(len(written_again), 7)


if __name__ == "__main__":
    unittest.main()
