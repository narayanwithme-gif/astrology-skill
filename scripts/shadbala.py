#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shadbala component estimates with explicit approximations."""

from chart_engine import CLASSICAL, drishti
from engine_utils import SIGNS

EXALTATION_LONGITUDES = {
    "Sun": 10,
    "Moon": 33,
    "Mars": 298,
    "Mercury": 165,
    "Jupiter": 95,
    "Venus": 357,
    "Saturn": 200,
}
SIGN_LORDS = (
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
)
FRIEND_PLANETS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
ENEMY_PLANETS = {
    "Sun": {"Venus", "Saturn"},
    "Moon": set(),
    "Mars": {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"},
    "Saturn": {"Sun", "Moon", "Mars"},
}
STRONG_ANGLE = {
    "Sun": ("midheaven", 0),
    "Mars": ("midheaven", 0),
    "Moon": ("midheaven", 180),
    "Venus": ("midheaven", 180),
    "Mercury": ("ascendant", 0),
    "Jupiter": ("ascendant", 0),
    "Saturn": ("ascendant", 180),
}
STRONG_HOUSE = {
    "Sun": 10,
    "Mars": 10,
    "Moon": 4,
    "Venus": 4,
    "Mercury": 1,
    "Jupiter": 1,
    "Saturn": 7,
}
NAISARGIKA_ORDER = ("Saturn", "Mars", "Mercury", "Jupiter", "Venus", "Moon", "Sun")


def sthana_bala(planet, sign, house):
    """Estimate positional dignity by sign. The house argument is retained for callers."""
    if planet not in EXALTATION_LONGITUDES or sign not in SIGNS:
        return 15
    sign_index = SIGNS.index(sign)
    exalted = EXALTATION_LONGITUDES[planet] // 30
    owner = SIGN_LORDS[sign_index]
    if sign_index == exalted:
        return 60
    if (sign_index - exalted) % 12 == 6:
        return 0
    if owner == planet:
        return 45
    if owner in FRIEND_PLANETS[planet]:
        return 30
    if owner in ENEMY_PLANETS[planet]:
        return 7
    return 15


def dig_bala(planet, house):
    """Approximate directional strength using only the house number."""
    if planet not in STRONG_HOUSE:
        return 0
    return _strength_from_peak(house * 30, STRONG_HOUSE[planet] * 30)


def cheshta_bala(planet, retrograde):
    """Retain the direction-of-motion scoring convention used by the estimate."""
    return 30 if retrograde or planet in ("Rahu", "Ketu") else 60


def uccha_bala(planet, longitude):
    """Scale the angular distance from exact debilitation to 0–60."""
    if planet not in EXALTATION_LONGITUDES:
        return 30
    return _strength_from_peak(longitude, EXALTATION_LONGITUDES[planet])


def _strength_from_peak(longitude, peak):
    return 60 - abs((longitude - peak + 180) % 360 - 180) / 3


def Kala_Bala__temporal(birth_jd, planet, settings):  # noqa: N802
    """Legacy neutral fallback when the local hour is unavailable."""
    return 30


def _time_estimate(planet, hour):
    if hour is None:
        return 30
    if 6 <= hour < 18:
        return 60 if planet in ("Sun", "Jupiter", "Venus") else 15
    return 60 if planet in ("Moon", "Mars", "Saturn") else 15


def drik_bala(planet, aspects_to_planet):
    """Estimate aspect strength using full sign-based aspects and fixed weights."""
    score = 30
    for aspector in aspects_to_planet:
        name = aspector if isinstance(aspector, str) else aspector[0]
        if name in ("Jupiter", "Venus"):
            score += 15
        elif name in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"):
            score -= 10
    return max(0, min(score, 60))


def calculate_shadbala(chart_data, birth_hour=None):
    """Estimate all six components for the seven classical planets."""
    if chart_data["zodiac"] != "sidereal":
        raise ValueError("Shadbala requires a sidereal natal chart")
    if birth_hour is not None and not 0 <= birth_hour < 24:
        raise ValueError("Shadbala birth hour must be in [0, 24)")
    aspects = chart_data.get("graha_drishti")
    if aspects is None:
        aspects = drishti(chart_data)
    result = {
        "status": "computed",
        "method": "Simplified Shadbala estimates",
        "limitations": [
            "Sthana combines a sign-dignity estimate with Uccha.",
            "Dig uses the Ascendant and Midheaven as directional peaks.",
            "Kala uses local clock time. Cheshta uses direction of motion.",
            "Drik uses sign-based graha drishti with simple weights.",
            "Totals are estimates without reference Shadbala thresholds.",
        ],
        "planets": {},
    }
    for planet in CLASSICAL[:7]:
        position = chart_data["planets"][planet]
        longitude = position["longitude"]
        uccha = uccha_bala(planet, longitude)
        angle, offset = STRONG_ANGLE[planet]
        components = {
            "sthana_bala": sthana_bala(planet, position["sign"], position["house"]) + uccha,
            "dig_bala": _strength_from_peak(longitude, chart_data[angle]["longitude"] + offset),
            "cheshta_bala": cheshta_bala(planet, position["retrograde"]),
            "kala_bala": _time_estimate(planet, birth_hour),
            "naisargika_bala": 60 * (NAISARGIKA_ORDER.index(planet) + 1) / 7,
            "drik_bala": drik_bala(
                planet, [row["graha"] for row in aspects if planet in row["target_grahas"]]
            ),
        }
        result["planets"][planet] = {
            **components,
            "uccha_bala": uccha,
            "total": sum(components.values()),
        }
    return result
