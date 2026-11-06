#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shared constants/helpers extracted from chart_engine (modularisation)."""
from datetime import timezone

SIGNS = "Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio Sagittarius Capricorn Aquarius Pisces".split()
NAK = "Ashwini Bharani Krittika Rohini Mrigashira Ardra Punarvasu Pushya Ashlesha Magha Purva-Phalguni Uttara-Phalguni Hasta Chitra Swati Vishakha Anuradha Jyeshtha Mula Purva-Ashadha Uttara-Ashadha Shravana Dhanishtha Shatabhisha Purva-Bhadrapada Uttara-Bhadrapada Revati".split()
LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
YEARS = dict(zip(LORDS, [7, 20, 6, 10, 7, 18, 16, 19, 17]))
ASPECTS = [("conjunction", 0), ("sextile", 60), ("square", 90), ("trine", 120), ("opposition", 180)]
UTC = timezone.utc

def number(value, name, lo, hi):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    v = float(value)
    if not (lo <= v <= hi):
        raise ValueError(f"{name} must be finite, between {lo} and {hi}")
    return v
