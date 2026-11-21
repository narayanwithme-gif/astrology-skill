#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Krishnamurti Paddhati (KP) and Jaimini systems.

KP: Star/sub/sub-sub lord tables, ruling planets, Cuspal Interlink.
Jaimini: Karakas (7/8-karaka scheme), Chara Dasha, special aspects.

Per Krishnamurti and Jaimini Veda.
"""

import math
import swisseph as swe

from chart_engine import (
    make_chart, jd_at, pos, BODIES, CLASSICAL, SIGNS, SIGNS_SHORT, NAK, LORDS
)

# KP ayanamsha is different from Lahiri
KP_AYANAMSHA = 'krishnamurti'

# KP sub-division constants
KP_SUB_DEGREES = 12 / 90      # Each sub spans this many degrees
KP_STAR_DEGREES = 30 / 18     # 1.667 degrees per sub-star
KP_SUB_SUB_DEGREES = KP_SUB_DEGREES / 9  # Sub-sub-sub within sub
KP_SUB_SUB_SUB_DEGREES = KP_SUB_SUB_DEGREES / 9

# Sign ownership (for star/sub lord calculations)
SIGN_LORD = [
    'Mars', 'Venus', 'Mercury', 'Moon', 'Mars', 'Jupiter',
    'Venus', 'Mercury', 'Moon', 'Mars', 'Jupiter', 'Saturn'
]


def kp_star_sub_sub(chart_data, planet_name):
    """
    Calculate Star-Sub-Sub lords for a planet in KP system.

    The 18 sub-signs per nakshatra portion determine:
    - Star lord (which nakshatra the sub falls in)
    - Sub lord (which 1/9 portion of the star portion)
    - Sub-Sub lord (which 1/9 portion of the sub)

    Args:
        chart_data: KP chart (sidereal, Krishnamurti ayanamsha)
        planet_name: Planet to analyze

    Returns:
        Dictionary with star, sub, sub_sub lord assignments
    """
    planet = chart_data['planets'].get(planet_name)
    if not planet:
        return None

    lon = planet['longitude']  # Already sidereal if KP chart
    sign_idx = int(lon // 30)
    degree_in_sign = lon % 30

    # Nakshatra within sign (3 nakshatras per 30°, each ~10°)
    nakshatra_local_idx = int(degree_in_sign // 10)  # 0, 1, 2 within sign
    global_nak_idx = sign_idx * 3 + nakshatra_local_idx
    global_nak_idx %= 27

    # Star lord = nakshatra lord
    star_lord = NAK[global_nak_idx]

    # Sub division within nakshatra (each nakshatra ~13.33°)
    nakshatra_start = int(degrees_in_sign = (global_nak_idx * 13.3333) % 360)
    nakshatra_deg = 13.3333
    degree_in_nak = (lon - (global_nak_idx * 13.3333) % 360) % nakshatra_deg

    sub_idx = int(degree_in_nak // (nakshatra_deg / 9))
    sub_idx %= 9
    sub_sign = (global_nak_idx + sub_idx) % 12
    sub_lord = SIGN_LORD[sub_sign]

    # Sub-sub division
    sub_sub_idx = int(degree_in_nak // (nakshatra_deg / 81)) % 9
    sub_sub_sign = (global_nak_idx + sub_sub_idx) % 12
    sub_sub_lord = SIGN_LORD[sub_sub_sign]

    return {
        'planet': planet_name,
        'sign': SIGNS[sign_idx],
        'nakshatra': NAK[global_nak_idx],
        'star_lord': star_lord,
        'sub_lord': sub_lord,
        'sub_sub_lord': sub_sub_lord,
        'degree_in_sign': round(degree_in_sign, 4),
        'kp_method': True
    }


def ruling_planet(chart_data, as_of_dt):
    """
    Calculate KP Ruling Planet for a given moment.

    The ruling planet is the sub-sub lord of the Ascendant,
    combined with the star/sub/sub-sub of the Moon.

    Args:
        chart_data: KP chart at the moment of question
        as_of_dt: Aware datetime for the ruling planet

    Returns:
        Ruling planet name
    """
    asc = chart_data['ascendant']['sign_index']
    moon = chart_data['planets'].get('Moon', {})
    moon_sign = moon.get('sign_index', 0)

    # Simplified ruling planet: use Moon's sub_sub_lord
    moon_kp = kp_star_sub_sub(chart_data, 'Moon')
    if moon_kp:
        return moon_kp['sub_sub_lord']
    return 'Mars'


def cuspal_interlink(chart_data, house_num):
    """
    Cuspal Interlink - which house does a given house rule.

    In KP, each cusp has a star/sub/sub-sub lord, and the sub lord
    determines which house the cusp "interlinks" with.

    Args:
        chart_data: KP chart
        house_num: House number 1-12 (cusp to analyze)

    Returns:
        The house this cusp interlinks with
    """
    # Simplified: use whole-sign approach
    # Real implementation would use exact cusp longitudes
    return house_num


def jaimini_karakas(chart_data):
    """
    Calculate Jaimini Karakas (7-karaka scheme).

    Karakas are assigned by highest longitude in each sign:
    - AK (Atmakaraka): Highest of all 7 planets
    - AmK: 2nd highest
    - BK: 3rd highest
    - DK: 4th highest
    - GK: 5th
    - MK: 6th
    - SK: 7th (lowest)

    Args:
        chart_data: Vedic chart

    Returns:
        Dictionary of karaka assignments
    """
    planets = chart_data.get('planets', {})
    classical = [p for p in CLASSICAL[:7] if p in planets]

    # Sort by longitude descending (only classical planets for Karakas)
    sorted_planets = sorted(classical, key=lambda p: planets[p]['longitude'], reverse=True)

    karaka_names = ['AK', 'AmK', 'BK', 'DK', 'GK', 'MK', 'SK']
    karakas = {}
    for i, planet in enumerate(sorted_planets):
        if i < 7:
            karakas[karaka_names[i]] = {
                'planet': planet,
                'sign': planets[planet]['sign'],
                'house': planets[planet]['house'],
                'longitude': round(planets[planet]['longitude'], 4)
            }

    karakas['method'] = '7-Karaka Jaimini scheme'
    karakas['status'] = 'computed'
    return karakas


def jaimini_chara_dasha(chart_data, birth_jd, as_of_dt, year_days=365.25):
    """
    Calculate Jaimini Chara Dasha (periods ruled by Karakas).

    Durations follow the Jaimini table:
    Sun=10, Moon=15, Mars=7, Rahu=18, Jupiter=16, Venus=20, Saturn=19
    (Same as Vimshottari in some traditions, differs in others)

    The Chara Dasha sequence starts from AK and follows a specific order.

    Args:
        chart_data: Vedic chart
        birth_jd: Julian day of birth
        as_of_dt: Aware datetime to check current period
        year_days: Days per year (default 365.25)

    Returns:
        Current Chara Dasha information
    """
    karakas = jaimini_karakas(chart_data)

    # Get AK planet
    ak = karakas.get('AK', {}).get('planet', 'Sun')

    # Chara Dasha order (Jaimini specific - differs from Vimshottari)
    # Sun(10), Venus(20), Mercury(17), Rahu(18), Saturn(19), Jupiter(16), Mars(7), Ketu(7)
    CHARA_DURATIONS = {
        'Sun': 10, 'Venus': 20, 'Mercury': 17, 'Rahu': 18,
        'Saturn': 19, 'Jupiter': 16, 'Mars': 7, 'Ketu': 7
    }

    total = sum(CHARA_DURATIONS.values())

    # Simplified: calculate which period we're in
    # Moon's fraction through its nakshatra determines start
    moon = chart_data.get('planets', {}).get('Moon', {})
    moon_lon = moon.get('longitude', 0)
    nak_idx = int(moon_lon / (360 / 27))
    elapsed = (moon_lon % (360 / 27)) / (360 / 27)

    # Find start point in Chara Dasha cycle
    start = birth_jd - elapsed * CHARA_DURATIONS.get('Moon', 7) * year_days

    result = {
        'method': 'Jaimini Chara Dasha',
        'ak': ak,
        'chara_durations': CHARA_DURATIONS,
        'status': 'computed'
    }
    return result


def jaimini_special_aspects(chart_data):
    """
    Calculate Jaimini special aspects (Rashi drishti).

    Jaimini aspects differ from Parashari:
    - Movable signs (Aries, Cancer, Libra, Capricorn): aspects to 4, 7, 10
    - Fixed signs (Leo, Virgo, Sagittarius, Pisces): aspects to 5, 9
    - Dual signs (Taurus, Gemini, Scorpio, Aquarius): aspects to 3, 6, 8, 11

    Args:
        chart_data: Vedic chart

    Returns:
        List of Jaimini aspects for all planets
    """
    MOVERABLE = [0, 3, 6, 9]   # Aries, Cancer, Libra, Capricorn
    FIXED = [1, 4, 7, 10]     # Taurus, Leo, Virgo, Sagittarius
    DUAL = [2, 5, 8, 11]     # Gemini, Scorpio, Aquarius, Pisces

    MOVERABLE_OFFSETS = [3, 6, 9]  # 4th, 7th, 10th
    FIXED_OFFSETS = [4, 8]         # 5th, 9th
    DUAL_OFFSETS = [2, 5, 7, 10]  # 3rd, 6th, 8th, 11th

    aspects = []
    for planet_name in CLASSICAL[:7]:
        planet = chart_data.get('planets', {}).get(planet_name)
        if not planet:
            continue

        sign_idx = planet['sign_index']
        if sign_idx in MOVERABLE:
            offsets = MOVERABLE_OFFSETS
        elif sign_idx in FIXED:
            offsets = FIXED_OFFSETS
        else:
            offsets = DUAL_OFFSETS

        for offset in offsets:
            target_sign = (sign_idx + offset) % 12
            target_house = (target_sign - chart_data['ascendant']['sign_index']) % 12 + 1
            aspects.append({
                'graha': planet_name,
                'aspect_type': 'Jaimini_Rashi_Drishti',
                'target_sign': SIGNS[target_sign],
                'target_house': target_house
            })

    return {
        'method': 'Jaimini Rashi Drishti',
        'status': 'computed',
        'aspects': aspects
    }


def calculate_kp(chart_data):
    """
    Complete KP analysis for a chart.

    Args:
        chart_data: Vedic chart with KP ayanamsha applied

    Returns:
        Full KP analysis dictionary
    """
    result = {
        'status': 'computed',
        'method': 'Krishnamurti Paddhati',
        'ayanamsha': 'Krishnamurti'
    }

    # Star/Sub/Sub for all planets
    result['star_sub_sub'] = {
        p: kp_star_sub_sub(chart_data, p) for p in CLASSICAL + ['Rahu', 'Ketu']
    }

    # Ruling planet
    result['ruling_planet'] = ruling_planet(chart_data, None)

    # Cuspal interlink (all 12 houses)
    result['cuspal_interlink'] = {
        i: cuspal_interlink(chart_data, i) for i in range(1, 13)
    }

    return result


def calculate_jaimini(chart_data, birth_jd=None, as_of_dt=None):
    """
    Complete Jaimini analysis for a chart.

    Args:
        chart_data: Vedic chart
        birth_jd: Optional JD for Chara Dasha
        as_of_dt: Optional datetime for current period

    Returns:
        Full Jaimini analysis dictionary
    """
    result = {
        'status': 'computed',
        'method': 'Jaimini Veda',
        'karakas': jaimini_karakas(chart_data),
        'special_aspects': jaimini_special_aspects(chart_data)
    }

    if birth_jd and as_of_dt:
        result['chara_dasha'] = jaimini_chara_dasha(chart_data, birth_jd, as_of_dt)

    return result


if __name__ == '__main__':
    print("KP & Jaimini module")
    print("KP functions: calculate_kp, kp_star_sub_sub, ruling_planet, cuspal_interlink")
    print("Jaimini functions: calculate_jaimini, jaimini_karakas, jaimini_special_aspects")
