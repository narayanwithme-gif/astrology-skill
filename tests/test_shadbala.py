#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Shadbala, Ashtakavarga, KP and Jaimini calculations."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from datetime import datetime, timezone
from chart_engine import make_chart, jd_at, parse_birth


class TestShadbala(unittest.TestCase):
    """Tests for Shadbala calculations."""

    @classmethod
    def setUpClass(cls):
        """Set up a test chart."""
        cls.birth = {
            "date": "1990-06-15",
            "time": "10:30",
            "timezone": "Asia/Kolkata",
            "latitude": 22.5726,
            "longitude": 88.3639
        }
        cls.chart = make_chart(
            jd_at(parse_birth(cls.birth)),
            cls.birth["latitude"],
            cls.birth["longitude"],
            {"western_houses": "P", "ayanamsha": "lahiri", "nodes": "mean"},
            sidereal=True
        )

    def test_shadbala_import(self):
        """Test shadbala module loads correctly."""
        from shadbala import (
            sthana_bala, dig_bala, cheshta_bala, Kala_Bala__temporal,
            uccha_bala, calculate_shadbala
        )
        self.assertTrue(callable(sthana_bala))
        self.assertTrue(callable(dig_bala))
        self.assertTrue(callable(calculate_shadbala))

    def test_sthana_bala_exaltation(self):
        """Test sthana_bala returns correct value for exalted planet."""
        from shadbala import sthana_bala
        # Moon is exalted in Taurus (0-30 Taurus = 53°)
        result = sthana_bala("Moon", "Taurus", 1)
        self.assertEqual(result, 60)

    def test_sthana_bala_debilitation(self):
        """Test sthana_bala returns 0 for debilitated planet."""
        from shadbala import sthana_bala
        # Sun is debilitated in Libra
        result = sthana_bala("Sun", "Libra", 7)
        self.assertEqual(result, 0)

    def test_sthana_bala_own_sign(self):
        """Test sthana_bala for own sign."""
        from shadbala import sthana_bala
        # Mars in Aries (own sign, moolatrikona)
        result = sthana_bala("Mars", "Aries", 1)
        self.assertEqual(result, 45)

    def test_calculate_shadbala(self):
        """Test complete shadbala calculation."""
        from shadbala import calculate_shadbala
        result = calculate_shadbala(self.chart)
        self.assertEqual(result['status'], 'computed')
        self.assertIn('planets', result)
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            self.assertIn(planet, result['planets'])
            p_data = result['planets'][planet]
            self.assertIn('sthana_bala', p_data)
            self.assertIn('total', p_data)


class TestAshtakavarga(unittest.TestCase):
    """Tests for Ashtakavarga calculations."""

    @classmethod
    def setUpClass(cls):
        """Set up a test chart."""
        cls.birth = {
            "date": "1990-06-15",
            "time": "10:30",
            "timezone": "Asia/Kolkata",
            "latitude": 22.5726,
            "longitude": 88.3639
        }
        cls.chart = make_chart(
            jd_at(parse_birth(cls.birth)),
            cls.birth["latitude"],
            cls.birth["longitude"],
            {"western_houses": "P", "ayanamsha": "lahiri", "nodes": "mean"},
            sidereal=True
        )

    def test_ashtakavarga_import(self):
        """Test ashtakavarga module loads correctly."""
        from ashtakavarga import (
            binnasha_varga, sarva_ashtakavarga,
            samudaya, kumbha, calculate_ashtakavarga
        )
        self.assertTrue(callable(binnasha_varga))
        self.assertTrue(callable(calculate_ashtakavarga))

    def test_binnasha_varga_structure(self):
        """Test binnasha varga returns correct structure."""
        from ashtakavarga import binnasha_varga
        result = binnasha_varga(self.chart)
        self.assertIsInstance(result, dict)
        for planet in ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            self.assertIn(planet, result)
            self.assertEqual(len(result[planet]), 12)

    def test_sarva_ashtakavarga_totals(self):
        """Test sarva astakavarga produces 12 sign totals."""
        from ashtakavarga import sarva_ashtakavarga
        result = sarva_ashtakavarga(self.chart)
        self.assertIn('sign_totals', result)
        self.assertEqual(len(result['sign_totals']), 12)

    def test_calculate_ashtakavarga(self):
        """Test complete ashtakavarga calculation."""
        from ashtakavarga import calculate_ashtakavarga
        result = calculate_ashtakavarga(self.chart)
        self.assertEqual(result['status'], 'computed')
        self.assertIn('sarva', result)
        self.assertIn('samudaya', result)
        self.assertIn('kumbha', result)


class TestKPAndJaimini(unittest.TestCase):
    """Tests for KP and Jaimini calculations."""

    @classmethod
    def setUpClass(cls):
        """Set up a test chart with KP ayanamsha."""
        cls.birth = {
            "date": "1990-06-15",
            "time": "10:30",
            "timezone": "Asia/Kolkata",
            "latitude": 22.5726,
            "longitude": 88.3639
        }
        cls.chart = make_chart(
            jd_at(parse_birth(cls.birth)),
            cls.birth["latitude"],
            cls.birth["longitude"],
            {"western_houses": "P", "ayanamsha": "kp", "nodes": "mean"},
            sidereal=True
        )

    def test_kp_import(self):
        """Test KP/Jaimini module loads correctly."""
        from kp_system import (
            kp_star_sub_sub, ruling_planet, cuspal_interlink,
            jaimini_karakas, jaimini_special_aspects,
            calculate_kp, calculate_jaimini
        )
        self.assertTrue(callable(kp_star_sub_sub))
        self.assertTrue(callable(jaimini_karakas))

    def test_kp_star_sub_sub(self):
        """Test KP star/sub/sub calculation."""
        from kp_system import kp_star_sub_sub
        result = kp_star_sub_sub(self.chart, 'Sun')
        self.assertIsNotNone(result)
        self.assertIn('star_lord', result)
        self.assertIn('sub_lord', result)
        self.assertIn('sub_sub_lord', result)

    def test_jaimini_karakas(self):
        """Test Jaimini 7-karaka calculation."""
        from kp_system import jaimini_karakas
        result = jaimini_karakas(self.chart)
        self.assertIn('AK', result)
        self.assertIn('SK', result)

    def test_jaimini_special_aspects(self):
        """Test Jaimini special aspects."""
        from kp_system import jaimini_special_aspects
        result = jaimini_special_aspects(self.chart)
        self.assertEqual(result['status'], 'computed')
        self.assertIn('aspects', result)
        self.assertIsInstance(result['aspects'], list)

    def test_calculate_kp(self):
        """Test complete KP analysis."""
        from kp_system import calculate_kp
        result = calculate_kp(self.chart)
        self.assertEqual(result['status'], 'computed')
        self.assertIn('star_sub_sub', result)

    def test_calculate_jaimini(self):
        """Test complete Jaimini analysis."""
        from kp_system import calculate_jaimini
        result = calculate_jaimini(self.chart)
        self.assertEqual(result['status'], 'computed')
        self.assertIn('karakas', result)


if __name__ == "__main__":
    unittest.main()