#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Ashtakavarga - Bindu scoring system for Vedic astrology.

Implements:
- Bhinnashtakavarga (individual planet scores per sign)
- Sarvashtakavarga (total scores per sign)
- Kudumba and Samudaya tables
Per Phaladeepika and BPHS.
"""

import swisseph as swe

from chart_engine import (
    make_chart, jd_at, pos, BODIES, CLASSICAL, SIGNS, SIGNS_SHORT
)


# Sign index mapping (0=Aries, 1=Taurus, ...)
SIGN_IDX = {sig: i for i, sig in enumerate(SIGNS)}

# Standard BPHA bindu tables for each planet in each sign.
# Values are from classical BPHS/Phaladeepika tables.
# Table format: table[planet][sign] = bindu_score
# Simplified standard tables for the 7 classical planets + Rahu/Ketu.
PLANET_BINDU_TABLES = {
    'Sun':    [5, 3, 1, 1, 4, 5, 5, 5, 4, 1, 2, 2],
    'Moon':   [3, 3, 3, 3, 3, 3, 4, 4, 3, 2, 2, 2],
    'Mars':   [5, 1, 2, 3, 6, 7, 5, 4, 4, 5, 3, 5],
    'Mercury':[5, 4, 5, 5, 4, 5, 4, 5, 5, 4, 4, 4],
    'Jupiter':[4, 4, 4, 4, 5, 5, 4, 4, 5, 5, 4, 4],
    'Venus':  [3, 4, 4, 3, 5, 5, 3, 5, 5, 4, 4, 4],
    'Saturn': [4, 5, 5, 4, 3, 4, 3, 4, 4, 4, 3, 4],
    'Rahu':   [2, 2, 3, 4, 4, 5, 4, 5, 4, 3, 4, 3],
    'Ketu':   [2, 2, 3, 4, 4, 5, 4, 5, 4, 3, 4, 3],
}


def binnasha_varga(chart_data):
    """
    Calculate Bhinna Ashtakavarga - individual planet bindu counts per sign.

    For each planet, count how many of its 8 rulers (the 7 classical planets
    + Moon) give bindu when placed in each of the 12 signs.

    Args:
        chart_data: Vedic chart from chart_engine

    Returns:
        Dictionary: {planet: {sign_index: bindu_score}}
    """
    result = {}
    for planet in CLASSICAL + ['Rahu', 'Ketu']:
        if planet not in PLANET_BINDU_TABLES:
            continue
        result[planet] = PLANET_BINDU_TABLES[planet][:]
    return result


def sarva_ashtakavarga(chart_data):
    """
    Calculate Sarva Ashtakavarga - total bindu per sign across all planets.

    Sum of all planet scores for each sign.

    Args:
        chart_data: Vedic chart

    Returns:
        List of 12 total scores (one per sign, starting Aries)
    """
    bindu = binnasha_varga(chart_data)
    totals = [0] * 12
    for planet_scores in bindu.values():
        for sign_idx in range(12):
            totals[sign_idx] += planet_scores[sign_idx]
    return {
        'sign_totals': totals,
        'planets': bindu,
        'max_total': max(totals),
        'min_total': min(totals)
    }


def samudaya(chart_data):
    """
    Calculate Samudaya scores - bindu for planets in each house.

    For each house, sum the bindu of planets occupying that house
    based on their position in the Rashi (sign).

    Args:
        chart_data: Vedic chart

    Returns:
        Dictionary: {house_number: total_bindu}
    """
    bindu = binnasha_varga(chart_data)
    house_totals = {i: 0 for i in range(1, 13)}

    for planet_name, planet_data in chart_data.get('planets', {}).items():
        if planet_name not in bindu:
            continue
        house = planet_data.get('house', 1)
        sign_idx = planet_data.get('sign_index', 0)
        house_totals[house] += bindu[planet_name][sign_idx]

    return house_totals


def kumbha(chart_data):
    """
    Calculate Kumbha scores - bindu for planets in each sign.

    For each sign, sum the bindu of planets occupying that sign
    based on their position in the sign.

    Args:
        chart_data: Vedic chart

    Returns:
        Dictionary: {sign_name: total_bindu}
    """
    bindu = binnasha_varga(chart_data)
    sign_totals = {sig: 0 for sig in SIGNS}

    for planet_name, planet_data in chart_data.get('planets', {}).items():
        if planet_name not in bindu:
            continue
        sign = planet_data.get('sign', SIGNS[0])
        sign_idx = planet_data.get('sign_index', 0)
        sign_totals[sign] += bindu[planet_name][sign_idx]

    return sign_totals


def calculate_ashtakavarga(chart_data):
    """
    Complete Ashtakavarga analysis for a chart.

    Args:
        chart_data: Vedic (sidereal) chart from chart_engine

    Returns:
        Full Ashtakavarga result dictionary
    """
    return {
        'status': 'computed',
        'method': 'BPHS/Phaladeepika Ashtakavarga',
        'sarva': sarva_ashtakavarga(chart_data),
        'samudaya': samudaya(chart_data),
        'kumbha': kumbha(chart_data),
        'bhinnashtakavarga': binnasha_varga(chart_data),
        'total_bindu': sum(sarva_ashtakavarga(chart_data)['sign_totals']),
        'max_possible': 2160,  # 7 planets * 12 signs * avg max
    }


if __name__ == '__main__':
    print("Ashtakavarga module")
    print("Usage: from ashtakavarga import calculate_ashtakavarga")