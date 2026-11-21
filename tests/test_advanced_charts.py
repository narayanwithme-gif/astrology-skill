#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for advanced chart calculations: composite, progressions, relocation."""

import json
import subprocess
import tempfile
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from datetime import datetime, timedelta
from pathlib import Path
from chart_engine import make_chart, jd_at, parse_birth

ROOT = Path(__file__).resolve().parents[1]


class TestCompositeCharts(unittest.TestCase):
    """Tests for composite chart calculations."""

    @classmethod
    def setUpClass(cls):
        """Set up sample charts for testing."""
        # Sample birth data
        cls.birth_a = {
            "date": "1990-06-15",
            "time": "10:30",
            "timezone": "Asia/Kolkata",
            "latitude": 22.5726,
            "longitude": 88.3639
        }
        cls.birth_b = {
            "date": "1992-03-22",
            "time": "14:45",
            "timezone": "Asia/Kolkata",
            "latitude": 22.5726,
            "longitude": 88.3639
        }

        cls.request_a = {"birth": cls.birth_a, "settings": {"western_houses": "P"}}
        cls.request_b = {"birth": cls.birth_b, "settings": {"western_houses": "P"}}

    def test_chart_creation(self):
        """Test basic chart creation works."""
        chart_a = make_chart(
            jd_at(parse_birth(self.birth_a)),
            self.birth_a["latitude"],
            self.birth_a["longitude"],
            {"western_houses": "P", "nodes": "mean"},
            sidereal=False
        )
        self.assertIn("planets", chart_a)
        self.assertIn("ascendant", chart_a)
        self.assertEqual(len(chart_a["planets"]), 12)

    def test_aspect_table(self):
        """Test aspect table generation."""
        from composite_charts import synastry_aspects

        chart_a = make_chart(
            jd_at(parse_birth(self.birth_a)),
            self.birth_a["latitude"],
            self.birth_a["longitude"],
            {"western_houses": "P", "nodes": "mean"},
            sidereal=False
        )
        chart_b = make_chart(
            jd_at(parse_birth(self.birth_b)),
            self.birth_b["latitude"],
            self.birth_b["longitude"],
            {"western_houses": "P", "nodes": "mean"},
            sidereal=False
        )

        aspects = synastry_aspects(chart_a, chart_b)
        self.assertIsInstance(aspects, list)
        # Should find some aspects
        self.assertGreater(len(aspects), 0)


class TestProgressions(unittest.TestCase):
    """Tests for progression calculations."""

    def test_secondary_progression_structure(self):
        """Test that progression module loads and has expected functions."""
        from progressions import secondary_progressions, solar_return, lunar_return
        self.assertTrue(callable(secondary_progressions))
        self.assertTrue(callable(solar_return))
        self.assertTrue(callable(lunar_return))


class TestRelocation(unittest.TestCase):
    """Tests for relocation chart calculations."""

    def test_relocation_structure(self):
        """Test that relocation module loads and has expected functions."""
        from relocation import relocation_chart, astrocartography_line
        self.assertTrue(callable(relocation_chart))
        self.assertTrue(callable(astrocartography_line))


class TestAdvancedReport(unittest.TestCase):
    def test_cli_advanced_example(self):
        with tempfile.TemporaryDirectory() as out:
            subprocess.run(
                [sys.executable, "scripts/chart_engine.py", "--input",
                 "assets/request.advanced.example.json", "--out", out],
                check=True, capture_output=True, text=True, cwd=ROOT,
            )
            report = json.loads((Path(out) / "chart.json").read_text(encoding="utf-8"))

        advanced = report["advanced"]
        western = report["western"]
        relocated = advanced["relocation"]
        self.assertEqual(relocated["planets"]["Moon"]["longitude"],
                         western["planets"]["Moon"]["longitude"])
        self.assertNotEqual(relocated["ascendant"], western["ascendant"])
        composite = advanced["composite"]
        self.assertTrue(composite["synastry_aspects"])
        self.assertIn("midheaven", composite["midpoint_composite"])
        self.assertEqual(composite["davison"]["location"], {"latitude": 23.9, "longitude": 75.1})
        progressed = advanced["progressions"]
        born = datetime.fromisoformat(progressed["birth_utc"])
        target = datetime.fromisoformat(progressed["target_date_utc"])
        expected = born + timedelta(days=(target - born) / timedelta(days=365.25))
        self.assertEqual(datetime.fromisoformat(progressed["progressed_date_utc"]), expected)
        for kind in ("solar_return", "lunar_return"):
            self.assertLess(advanced[kind]["orb_degrees"], 1e-5)
        vedic = advanced["vedic"]
        self.assertEqual(vedic["ashtakavarga"]["total_bindu"], 337)
        self.assertEqual(len(vedic["kp"]["cuspal_interlink"]), 12)
        self.assertEqual(vedic["kp"]["ayanamsha"], "krishnamurti")
        self.assertEqual(report["jyotisha"]["ayanamsha"], "lahiri")
        self.assertIn("DK", vedic["jaimini"]["karakas"])
        self.assertIn("naisargika_bala", vedic["shadbala"]["planets"]["Sun"])

    def test_midpoint_wraps_and_is_order_independent(self):
        from composite_charts import _midpoint

        self.assertEqual(_midpoint(350, 10), 0)
        self.assertEqual(_midpoint(15, 195), _midpoint(195, 15))

    def test_solar_return_for_february_29_birth(self):
        from progressions import solar_return

        birth = datetime.fromisoformat("2000-02-29T12:00:00+05:30")
        result = solar_return(birth, 2025, 28, 77, {"western_houses": "P", "nodes": "mean"})
        self.assertLess(result["orb_degrees"], 1e-5)


if __name__ == "__main__":
    unittest.main()
