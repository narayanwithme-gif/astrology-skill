#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for advanced chart calculations: composite, progressions, relocation."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from datetime import datetime, timezone, timedelta
from chart_engine import make_chart, jd_at, parse_birth


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
            {"western_houses": "P"},
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
            {"western_houses": "P"},
            sidereal=False
        )
        chart_b = make_chart(
            jd_at(parse_birth(self.birth_b)),
            self.birth_b["latitude"],
            self.birth_b["longitude"],
            {"western_houses": "P"},
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


if __name__ == "__main__":
    unittest.main()