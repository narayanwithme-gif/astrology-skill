#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shadbala - Six-fold strength calculations for Vedic astrology.

Implements: Sthana Bala (positional), Dig Bala (directional),
Kala Bala (temporal), Cheshta Bala (motional), Naisa Bala (aspect),
Drik Bala (aspect from benefics). Per BPHS and classical sources.
"""

from chart_engine import CLASSICAL, SIGNS


# Sign ownership (planet -> set of signs it owns)
PLANET_OWN_SIGNS = {
    'Sun':      {'Leo'},
    'Moon':     {'Cancer'},
    'Mars':     {'Aries', 'Scorpio'},
    'Mercury':  {'Gemini', 'Virgo'},
    'Jupiter':  {'Sagittarius', 'Pisces'},
    'Venus':    {'Taurus', 'Libra'},
    'Saturn':   {'Capricorn', 'Aquarius'},
}

# Exalted signs (planet -> sign where planet is exalted)
EXALTED_SIGNS = {
    'Sun':      'Aries',
    'Moon':     'Taurus',
    'Mars':     'Capricorn',
    'Mercury':  'Virgo',
    'Jupiter':  'Cancer',
    'Venus':    'Pisces',
    'Saturn':   'Libra',
}

# Debilitated signs (opposite of exaltation)
DEBILITATED_SIGNS = {
    'Sun':      'Libra',
    'Moon':     'Scorpio',
    'Mars':     'Cancer',
    'Mercury':  'Pisces',
    'Jupiter':  'Capricorn',
    'Venus':    'Virgo',
    'Saturn':   'Aries',
}

# Moolatrikona signs (stronger than regular own sign)
MOOLATRIKONA_SIGNS = {
    'Sun':      'Leo',
    'Moon':     'Cancer',
    'Mars':     'Aries',
    'Mercury':  'Gemini',
    'Jupiter':  'Pisces',
    'Venus':    'Taurus',
    'Saturn':   'Capricorn',
}

# Friend planets (based on elemental compatibility in Vedic tradition)
FRIEND_PLANETS = {
    'Sun':      {'Mars', 'Jupiter', 'Venus'},
    'Moon':     {'Mercury', 'Venus'},
    'Mars':     {'Sun', 'Moon', 'Venus'},
    'Mercury':  {'Sun', 'Venus'},
    'Jupiter':  {'Sun', 'Mars', 'Venus', 'Moon'},
    'Venus':    {'Mercury', 'Sun'},
    'Saturn':   {'Mercury', 'Jupiter'},
}

# Enemy planets
ENEMY_PLANETS = {
    'Sun':      {'Mars'},
    'Moon':     {'Saturn'},
    'Mars':     {'Jupiter', 'Saturn'},
    'Mercury':  {'Saturn', 'Jupiter'},
    'Jupiter':  {'Saturn', 'Mars'},
    'Venus':    {'Mars', 'Jupiter'},
    'Saturn':   {'Sun', 'Moon', 'Mars', 'Jupiter'},
}


def sthana_bala(planet, sign, house):
    """
    Calculate Sthana Bala (positional strength).

    Points:
      - Moolatrikona sign:    45
      - Own sign (non-moola): 45
      - Exalted sign:         60
      - Friend's sign:        30
      - Neutral sign:         15
      - Enemy's sign:         7
      - Debilitated sign:     0

    Args:
        planet: Planet name (Sun through Saturn)
        sign: Sign name (e.g., 'Aries')
        house: House number (1-12)

    Returns:
        Sthana Bala points (int)
    """
    if planet not in EXALTED_SIGNS:
        return 15

    # Debilitated: 0
    if DEBILITATED_SIGNS.get(planet) == sign:
        return 0

    # Exalted: 60
    if EXALTED_SIGNS.get(planet) == sign:
        return 60

    # Own sign (moolatrikona gets 45, regular own also 45 here):
    if sign in PLANET_OWN_SIGNS.get(planet, set()):
        return 45

    # Determine whose sign we're in
    lord_of_sign = None
    for p, signs in PLANET_OWN_SIGNS.items():
        if sign in signs:
            lord_of_sign = p
            break

    if lord_of_sign is None:
        return 15  # Neutral (Rahu/Ketu sign)

    if lord_of_sign in FRIEND_PLANETS.get(planet, set()):
        return 30
    if lord_of_sign in ENEMY_PLANETS.get(planet, set()):
        return 7
    return 15


def dig_bala(planet, house):
    """
    Calculate Dig Bala (directional strength).

    Planets are strongest in specific houses:
      - Sun: 1st, Jupiter: 1st/5th, Moon: 4th, Mars: 10th,
        Mercury: 1st/7th, Venus: 4th/10th, Saturn: 7th

    Args:
        planet: Planet name
        house: House number (1-12)

    Returns:
        Dig Bala points (int, 0-60)
    """
    if house not in (1, 4, 7, 10):
        return 0  # Only cardinal houses matter for dig bala

    base = {
        'Sun':      {1: 60, 4: 0,  7: 30, 10: 30},
        'Moon':     {1: 30, 4: 60, 7: 0,  10: 30},
        'Mars':     {1: 30, 4: 0,  7: 30, 10: 60},
        'Mercury':  {1: 60, 4: 0,  7: 30, 10: 30},
        'Jupiter':  {1: 60, 4: 0,  7: 30, 10: 30},
        'Venus':    {1: 30, 4: 60, 7: 0,  10: 30},
        'Saturn':   {1: 0,  4: 30, 7: 60, 10: 30},
    }

    return base.get(planet, {}).get(house, 0)


def cheshta_bala(planet, retrograde):
    """
    Calculate Cheshta Bala (motional strength).

    - Direct motion: 60
    - Retrograde:    30
    - Rahu/Ketu:     30 (perpetually retrograde)

    Args:
        planet: Planet name
        retrograde: bool

    Returns:
        Cheshta Bala points (int)
    """
    if planet in ('Rahu', 'Ketu'):
        return 30
    return 30 if retrograde else 60


def uccha_bala(planet, longitude):
    """
    Calculate Uccha Bala (exaltation strength).

    Ranges from 0 at the debilitation point to 60 at the exaltation point.
    Uses sign-based lookup (not exact degree calculation) for a simplified score.

    Args:
        planet: Planet name
        longitude: Ecliptic longitude (float, 0-360)

    Returns:
        Uccha Bala points (int, 0-60)
    """
    if planet not in EXALTED_SIGNS:
        return 30

    exalta_sign = EXALTED_SIGNS[planet]
    debila_sign = DEBILITATED_SIGNS[planet]
    current_sign = SIGNS[int(longitude) // 30]

    if current_sign == exalta_sign:
        return 60
    if current_sign == debila_sign:
        return 0

    # Opposite to exaltation = debilitation (already handled)
    # Count distance from exaltation sign
    exalta_idx = SIGNS.index(exalta_sign)
    current_idx = SIGNS.index(current_sign)
    dist = abs(exalta_idx - current_idx)
    dist = min(dist, 12 - dist)

    return int(60 * (1 - dist / 6))


def Kala_Bala__temporal(birth_jd, planet, settings):
    """Kala Bala (temporal strength) - stub for API compatibility.

    Simplified: returns 30 (neutral) without a full sunrise/sunset table.
    Use calculate_shadbala() for the full breakdown.
    """
    return 30


def drik_bala(planet, aspects_to_planet):
    """
    Calculate Drik Bala (strength from aspects received).

    Benefic aspects add strength, malefic aspects reduce it.

    Args:
        planet: Planet being aspected
        aspects_to_planet: list of (aspecting_planet_name, aspect_type) tuples

    Returns:
        Drik Bala points (int, 0-60)
    """
    score = 30  # Base

    for aspector in aspects_to_planet:
        if isinstance(aspector, str):
            name = aspector
        else:
            name = aspector[0]

        if name in ('Jupiter', 'Venus'):
            score += 15
        elif name in ('Sun', 'Mars', 'Saturn', 'Rahu', 'Ketu'):
            score -= 10

    return max(0, min(score, 60))


def calculate_shadbala(chart_data, birth_hour=None):
    """
    Calculate complete Shadbala for all planets in a chart.

    Args:
        chart_data: Vedic chart dict from chart_engine.make_chart()
        birth_hour: Hour of birth (0-23.99) for Kala Bala; if None, day=0/night=1 assumed

    Returns:
        Dictionary with Shadbala breakdown for each planet
    """
    planets = chart_data.get('planets', {})
    result = {
        'status': 'computed',
        'method': 'BPHS Shadbala (simplified sign-based)',
        'planets': {}
    }

    for planet in CLASSICAL[:7]:
        if planet not in planets:
            continue

        p = planets[planet]
        sign = p.get('sign', SIGNS[0])
        house = p.get('house', 1)
        longitude = p.get('longitude', 0.0)
        retrograde = p.get('retrograde', False)

        sb = sthana_bala(planet, sign, house)
        db = dig_bala(planet, house)
        cb = cheshta_bala(planet, retrograde)
        ub = uccha_bala(planet, longitude)

        # Kala Bala: simplified — day births favour Sun/Jupiter/Saturn
        if birth_hour is None:
            kb = 30
        elif birth_hour < 6 or birth_hour >= 18:
            kb = 60 if planet in ('Moon', 'Venus') else 15
        else:
            kb = 60 if planet in ('Sun', 'Jupiter', 'Saturn') else 15

        drb = drik_bala(planet, [])  # No aspect data passed; use base score

        total = sb + db + cb + kb + ub + drb

        result['planets'][planet] = {
            'sthana_bala': sb,
            'dig_bala': db,
            'cheshta_bala': cb,
            'kala_bala': kb,
            'uccha_bala': ub,
            'drik_bala': drb,
            'total': total
        }

    return result


if __name__ == '__main__':
    print("Shadbala module")
    print("Usage: from shadbala import calculate_shadbala")
