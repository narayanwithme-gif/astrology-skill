#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Shadbala - Six-fold strength calculations for Vedic astrology.

Implements: Sthana Bala (positional), Dig Bala (directional),
Kala Bala (temporal), Cheshta Bala (motional), Naisa Bala (aspect),
Drik Bala (aspect from benefics). Per BPHS and classical sources.
"""

import math
from datetime import datetime, timezone

import swisseph as swe

from chart_engine import (
    make_chart, jd_at, pos, BODIES, CLASSICAL, SIGNS, LORDS, NAK
)


# Planet lords for each sign (Sun-Saturn, no Rahu/Ketu for sign ownership)
SIGN_LORDS = {
    'Aries': 'Mars', 'Leo': 'Sun', 'Sagittarius': 'Jupiter',
    'Taurus': 'Venus', 'Libra': 'Venus', 'Capricorn': 'Saturn',
    'Gemini': 'Mercury', 'Virgo': 'Mercury', 'Aquarius': 'Saturn',
    'Cancer': 'Moon', 'Scorpio': 'Mars', 'Pisces': 'Jupiter'
}

# Exaltation points (degrees)
EXALTATION_POINTS = {
    'Sun': 280, 'Moon': 53, 'Mars': 298, 'Mercury': 165,
    'Jupiter': 95, 'Venus': 357, 'Saturn': 210
}

# Debilitation points (opposite to exaltation)
DEBILITATION_POINTS = {k: (v + 180) % 360 for k, v in EXALTATION_POINTS.items()}

# Friends (based on element compatibility)
FRIENDS = {
    'Sun': ['Moon', 'Mars', 'Jupiter'], 'Moon': ['Sun', 'Mercury'],
    'Mars': ['Sun', 'Moon', 'Jupiter'], 'Mercury': ['Sun', 'Venus'],
    'Jupiter': ['Sun', 'Mars', 'Moon'], 'Venus': ['Mercury', 'Saturn'],
    'Saturn': ['Venus', 'Mercury']
}

# Enemies
ENEMIES = {
    'Sun': ['Venus', 'Saturn'], 'Moon': [], 'Mars': ['Mercury', 'Jupiter'],
    'Mercury': ['Moon'], 'Jupiter': ['Mercury', 'Venus'],
    'Venus': ['Sun', 'Mars'], 'Saturn': ['Sun', 'Moon', 'Mars']
}


def normalize_degrees(degrees):
    """Normalize degrees to 0-360 range."""
    return degrees % 360


def sthana_bala(planet, sign, house):
    """
    Calculate Sthana Bala (positional strength).

    Based on sign placement:
    - Exalted: 60 points
    - Moolatrikona: 45 points
    - Own sign: 30 points
    - Friend's sign: 22.5 points
    - Neutral: 15 points
    - Enemy's sign: 7.5 points
    - Debilitated: 0 points

    Args:
        planet: Planet name
        sign: Sign name (e.g., 'Aries')
        house: House number (1-12)

    Returns:
        Sthana Bala points (0-60)
    """
    if planet not in SIGN_LORDS and planet not in ['Rahu', 'Ketu']:
        return 0

    planet_sign_lord = SIGN_LORDS.get(planet, None)

    # Check exaltation
    if planet in EXALTATION_POINTS:
        exalta_sign_start = int(EXALTATION_POINTS[planet] // 30) * 30
        if sign == SIGNS[exalta_sign_start // 30]:
            return 60

    # Check debilitation
    if planet in DEBILITATION_POINTS:
        debila_sign_start = int(DEBILITATION_POINTS[planet] // 30) * 30
        if sign == SIGNS[debila_sign_start // 30]:
            return 0

    # Check own sign (simplified - doesn't account for Moolatrikona fully)
    if planet_sign_lord == sign:
        return 45  # Moolatrikona

    # Check friend's sign
    if planet in FRIENDS and planet_sign_lord in FRIENDS[planet]:
        return 22.5

    # Check enemy's sign
    if planet in ENEMIES and planet_sign_lord in ENEMIES[planet]:
        return 7.5

    return 15  # Neutral sign


def dig_bala(planet, house):
    """
    Calculate Dig Bala (directional strength).

    Planets are strongest in specific houses:
    - Sun, Jupiter: 1st house (own sign)
    - Mars: 10th house
    - Mercury: 1st house (own sign)
    - Saturn: 7th house
    - Venus: 4th house
    - Moon: 4th house (in Cancer)

    Args:
        planet: Planet name
        house: House number (1-12)

    Returns:
        Dig Bala points (0-60)
    """
    dig_strengths = {
        'Sun': {1: 60, 10: 30, 7: 15, 4: 0},
        'Moon': {4: 60, 10: 30, 1: 15, 7: 0},
        'Mars': {10: 60, 1: 30, 7: 15, 4: 0},
        'Mercury': {1: 60, 10: 30, 7: 15, 4: 0},
        'Jupiter': {1: 60, 10: 30, 7: 15, 4: 0},
        'Venus': {4: 60, 10: 30, 1: 15, 7: 0},
        'Saturn': {7: 60, 10: 30, 4: 15, 1: 0}
    }

    return dig_strengths.get(planet, {}).get(house, 0)


def cheshta_bala(planet, retrograde):
    """
    Calculate Cheshta Bala (motional strength).

    - Direct motion: 60 points
    - Retrograde: 30 points
    - Stationary: 15 points

    Args:
        planet: Planet name
        retrograde: Boolean indicating if planet is retrograde

    Returns:
        Cheshta Bala points
    """
    if planet in ['Rahu', 'Ketu']:  # Nodes are always retrograde-like
        return 30

    return 30 if retrograde else 60


def Kala_Bala__temporal(birth_jd, planet, settings):
    """
    Calculate Kala Bala (temporal strength).

    Based on time of birth:
    - Day births: Sun, Jupiter, Saturn strong; Moon, Venus weak
    - Night births: Moon, Venus strong; Sun, Jupiter, Saturn weak

    Also includes monthly strength based on Moon's position.

    Args:
        birth_jd: Julian day of birth
        planet: Planet name
        settings: Chart settings

    Returns:
        Kala Bala points (approximate)
    """
    # Convert JD to datetime to determine day/night
    birth_dt = datetime(*swe.revjul(birth_jd, 1)[:6], tzinfo=timezone.utc)
    hour = birth_dt.hour + birth_dt.minute / 60

    is_night = hour >= 18 or hour < 6

    # Day/night strength
    day_planets = ['Sun', 'Jupiter', 'Saturn']
    night_planets = ['Moon', 'Venus']

    if planet in day_planets and not is_night:
        return 60
    elif planet in night_planets and is_night:
        return 60
    elif planet in day_planets and is_night:
        return 15
    elif planet in night_planets and not is_night:
        return 15
    else:
        return 30  # Neutral


def naisa_bala(planet, aspecting_planets):
    """
    Calculate Naisa Bala (strength from aspecting planets).

    Based on aspects from benefic planets.
    Full aspect: 60 points
    Partial aspect: 30 points

    Args:
        planet: Planet being aspected
        aspecting_planets: List of planets aspecting this planet

    Returns:
        Naisa Bala points
    """
    benefics = ['Jupiter', 'Venus', 'Moon']  # Including Moon as generally benefic

    score = 0
    for aspector in aspecting_planets:
        if aspector in benefics:
            score += 30  # Partial benefic aspect

    return min(score, 60)  # Cap at 60


def drik_bala(planet, aspects_to_planet):
    """
    Calculate Drik Bala (strength from aspects received).

    Benefic aspects add strength, malefic aspects reduce it.

    Args:
        planet: Planet being aspected
        aspects_to_planet: List of (aspecting_planet, aspect_type) tuples

    Returns:
        Drik Bala points
    """
    benefics = {'Jupiter': 60, 'Venus': 60, 'Moon': 45}
    malefics = {'Sun': 30, 'Mars': 30, 'Saturn': 45, 'Rahu': 30, 'Ketu': 30}

    score = 30  # Base

    for aspector, aspect_name in aspects_to_planet:
        if aspector in benefics:
            score += benefics[aspector] / 3  # Reduced impact
        elif aspector in malefics:
            score -= malefics[aspector] / 3

    return max(0, min(score, 60))  # Clamp to 0-60


def uccha_bala(planet, longitude):
    """
    Calculate Uccha Bala (exaltation strength).

    Maximum at exact exaltation point, decreasing linearly to 0 at debilitation.

    Args:
        planet: Planet name
        longitude: Planet's ecliptic longitude

    Returns:
        Uccha Bala (0-60)
    """
    if planet not in EXALTATION_POINTS:
        return 30  # No exaltation for Rahu/Ketu

    exalta_lon = EXALTATION_POINTS[planet]
    debila_lon = (exalta_lon + 180) % 360

    # Calculate distance from exaltation
    diff_from_exalta = abs((longitude - exalta_lon + 180) % 360 - 180)
    diff_from_debila = abs((longitude - debila_lon + 180) % 360 - 180)

    # Maximum at exact exaltation
    if diff_from_exalta == 0:
        return 60

    # Linear decrease - full range is 180 degrees
    strength = 60 * (1 - diff_from_exalta / 180)

    return max(0, min(strength, 60))


def apa_bala(planet, longitude):
    """
    Calculate Apa Bala (combustion strength).

    Planet is weak when within certain degrees of Sun.

    Args:
        planet: Planet name
        longitude: Planet's ecliptic longitude

    Returns:
        Apa Bala (0-60) - lower when combust
    """
    if planet == 'Sun':
        return 0

    # This requires Sun's position - would need to pass it in
    # Simplified placeholder
    return 30


def calculate_shadbala(chart_data):
    """
    Calculate complete Shadbala for all planets in a chart.

    Args:
        chart_data: natal chart from chart_engine

    Returns:
        Dictionary with Shadbala breakdown for each planet
    """
    planets = chart_data['planets']
    asc_sign = chart_data['ascendant']['sign']
    asc_house = 1  # Simplified - actual calculation would need proper house assignment

    result = {
        'status': 'computed',
        'method': 'BPHS Shadbala (simplified)',
        'planets': {}
    }

    # Get Sun position for aspect calculations
    sun_lon = planets.get('Sun', {}).get('longitude', 0)

    for planet in CLASSICAL[:7]:  # Sun through Saturn
        if planet not in planets:
            continue

        p_data = planets[planet]
        sign = p_data['sign']
        house = p_data['house']
        longitude = p_data['longitude']
        retrograde = p_data.get('retrograde', False)

        # Calculate individual strengths
        sb = sthana_bala(planet, sign, house)
        db = dig_bala(planet, house)
        cb = cheshta_bala(planet, retrograde)
        kb = Kala_Bala__temporal(chart_data.get('provenance', {}).get('jd', 0), planet, {})
        ub = uccha_bala(planet, longitude)

        # Naisa and Drik require aspect data
        nb = naisa_bala(planet, [])  # Simplified
        drb = drik_bala(planet, [])  # Simplified

        total = sb + db + cb + kb + ub + drb + nb

        result['planets'][planet] = {
            'sthana_bala': round(sb, 2),
            'dig_bala': round(db, 2),
            'cheshta_bala': round(cb, 2),
            'kala_bala': round(kb, 2),
            'uccha_bala': round(ub, 2),
            'naisa_bala': round(nb, 2),
            'drik_bala': round(drb, 2),
            'total': round(total, 2)
        }

    return result


if __name__ == '__main__':
    print("Shadbala module")
    print("Usage: from shadbala import calculate_shadbala")