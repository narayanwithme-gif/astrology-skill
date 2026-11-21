#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Unreduced seven-planet Ashtakavarga from natal sidereal signs."""

from engine_utils import SIGNS

# Brihat Jataka 9.1–7, Aiyar translation. Count each contributor's sign as 1.
CONTRIBUTORS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna")
BENEFIC_PLACES = {
    "Sun": (
        (1, 2, 4, 7, 8, 9, 10, 11),
        (3, 6, 10, 11),
        (1, 2, 4, 7, 8, 9, 10, 11),
        (3, 5, 6, 9, 10, 11, 12),
        (5, 6, 9, 11),
        (6, 7, 12),
        (1, 2, 4, 7, 8, 9, 10, 11),
        (3, 4, 6, 10, 11, 12),
    ),
    "Moon": (
        (3, 6, 7, 8, 10, 11),
        (1, 3, 6, 7, 10, 11),
        (2, 3, 5, 6, 9, 10, 11),
        (1, 3, 4, 5, 7, 8, 10, 11),
        (1, 4, 7, 8, 10, 11, 12),
        (3, 4, 5, 7, 9, 10, 11),
        (3, 5, 6, 11),
        (3, 6, 10, 11),
    ),
    "Mars": (
        (3, 5, 6, 10, 11),
        (3, 6, 11),
        (1, 2, 4, 7, 8, 10, 11),
        (3, 5, 6, 11),
        (6, 10, 11, 12),
        (6, 8, 11, 12),
        (1, 4, 7, 8, 9, 10, 11),
        (1, 3, 6, 10, 11),
    ),
    "Mercury": (
        (5, 6, 9, 11, 12),
        (2, 4, 6, 8, 10, 11),
        (1, 2, 4, 7, 8, 9, 10, 11),
        (1, 3, 5, 6, 9, 10, 11, 12),
        (6, 8, 11, 12),
        (1, 2, 3, 4, 5, 8, 9, 11),
        (1, 2, 4, 7, 8, 9, 10, 11),
        (1, 2, 4, 6, 8, 10, 11),
    ),
    "Jupiter": (
        (1, 2, 3, 4, 7, 8, 9, 10, 11),
        (2, 5, 7, 9, 11),
        (1, 2, 4, 7, 8, 10, 11),
        (1, 2, 4, 5, 6, 9, 10, 11),
        (1, 2, 3, 4, 7, 8, 10, 11),
        (2, 5, 6, 9, 10, 11),
        (3, 5, 6, 12),
        (1, 2, 4, 5, 6, 7, 9, 10, 11),
    ),
    "Venus": (
        (8, 11, 12),
        (1, 2, 3, 4, 5, 8, 9, 11, 12),
        (3, 5, 6, 9, 11, 12),
        (3, 5, 6, 9, 11),
        (5, 8, 9, 10, 11),
        (1, 2, 3, 4, 5, 8, 9, 10, 11),
        (3, 4, 5, 8, 9, 10, 11),
        (1, 2, 3, 4, 5, 8, 9, 11),
    ),
    "Saturn": (
        (1, 2, 4, 7, 8, 10, 11),
        (3, 6, 11),
        (3, 5, 6, 10, 11, 12),
        (6, 8, 9, 10, 11, 12),
        (5, 6, 11, 12),
        (6, 11, 12),
        (3, 5, 6, 11),
        (1, 3, 4, 6, 10, 11),
    ),
}


def binnasha_varga(chart_data):
    """Return twelve counts (Aries through Pisces) for each classical planet."""
    if chart_data["zodiac"] != "sidereal":
        raise ValueError("Ashtakavarga requires a sidereal natal chart")
    source_signs = [chart_data["planets"][planet]["sign_index"] for planet in CONTRIBUTORS[:-1]] + [
        chart_data["ascendant"]["sign_index"]
    ]
    result = {}
    for planet, rules in BENEFIC_PLACES.items():
        counts = [0] * 12
        for sign, houses in zip(source_signs, rules, strict=True):
            for house in houses:
                counts[(sign + house - 1) % 12] += 1
        result[planet] = counts
    return result


def sarva_ashtakavarga(chart_data):
    """Sum the seven planetary rows by sign."""
    rows = binnasha_varga(chart_data)
    totals = [sum(column) for column in zip(*rows.values(), strict=True)]
    return {
        "sign_totals": totals,
        "planets": rows,
        "max_total": max(totals),
        "min_total": min(totals),
    }


def samudaya(chart_data):
    """Return Sarvashtakavarga totals in whole-sign house order."""
    totals = sarva_ashtakavarga(chart_data)["sign_totals"]
    lagna = chart_data["ascendant"]["sign_index"]
    return {house: totals[(lagna + house - 1) % 12] for house in range(1, 13)}


def kumbha(chart_data):
    """Return Sarvashtakavarga totals by sign name."""
    return dict(zip(SIGNS, sarva_ashtakavarga(chart_data)["sign_totals"], strict=True))


def calculate_ashtakavarga(chart_data):
    sarva = sarva_ashtakavarga(chart_data)
    totals = sarva["sign_totals"]
    lagna = chart_data["ascendant"]["sign_index"]
    return {
        "status": "computed",
        "method": "Brihat Jataka 9.1–7 (unreduced)",
        "sarva": sarva,
        "samudaya": {house: totals[(lagna + house - 1) % 12] for house in range(1, 13)},
        "kumbha": dict(zip(SIGNS, totals, strict=True)),
        "bhinnashtakavarga": sarva["planets"],
        "total_bindu": sum(totals),
    }
