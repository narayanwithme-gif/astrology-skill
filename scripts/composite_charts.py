#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Composite and relationship chart calculations."""

import sys
from datetime import datetime, timezone

import swisseph as swe

from chart_engine import make_chart, jd_at, pos


def midpoint_chart(chart_a, chart_b, lat, lon, settings):
    """
    Calculate midpoint composite chart (average of two natal charts).

    Args:
        chart_a: First natal chart data
        chart_b: Second natal chart data
        lat: Composite chart latitude
        lon: Composite chart longitude
        settings: Chart calculation settings

    Returns:
        Composite chart with midpoint positions
    """
    planets_composite = {}

    for planet in chart_a['planets'].keys():
        if planet not in chart_b['planets']:
            continue

        lon_a = chart_a['planets'][planet]['longitude']
        lon_b = chart_b['planets'][planet]['longitude']

        # Calculate shorter arc midpoint
        diff = (lon_b - lon_a) % 360
        if diff > 180:
            midpoint_lon = (lon_a - (360 - diff) / 2) % 360
        else:
            midpoint_lon = (lon_a + diff / 2) % 360

        planets_composite[planet] = {
            **pos(midpoint_lon),
            'method': 'midpoint',
            'source_a_longitude': lon_a,
            'source_b_longitude': lon_b
        }

    # Calculate composite Ascendant as midpoint
    asc_a = chart_a['ascendant']['longitude']
    asc_b = chart_b['ascendant']['longitude']
    diff = (asc_b - asc_a) % 360
    if diff > 180:
        composite_asc = (asc_a - (360 - diff) / 2) % 360
    else:
        composite_asc = (asc_a + diff / 2) % 360

    return {
        'type': 'midpoint_composite',
        'zodiac': chart_a['zodiac'],
        'ascendant': pos(composite_asc),
        'planets': planets_composite,
        'method': 'Midpoint method - average of two natal charts',
        'chart_a_reference': chart_a.get('birth', {}).get('date'),
        'chart_b_reference': chart_b.get('birth', {}).get('date')
    }


def davison_chart(birth_a, birth_b, lat, lon, settings):
    """
    Calculate Davison relationship chart (midpoint in time and space).

    Args:
        birth_a: First person's birth datetime (aware)
        birth_b: Second person's birth datetime (aware)
        lat: Chart latitude (can be midpoint of birth locations)
        lon: Chart longitude (can be midpoint of birth locations)
        settings: Chart calculation settings

    Returns:
        Davison chart data
    """
    # Calculate midpoint in time
    delta = birth_b.astimezone(timezone.utc) - birth_a.astimezone(timezone.utc)
    midpoint_time = birth_a.astimezone(timezone.utc) + delta / 2

    # Calculate chart for midpoint time and location
    jd = jd_at(midpoint_time)

    sidereal = settings.get('zodiac') == 'sidereal'
    chart = make_chart(jd, lat, lon, settings, sidereal)

    chart['type'] = 'davison_relationship'
    chart['method'] = 'Davison method - midpoint in time and space'
    chart['midpoint_datetime_utc'] = midpoint_time.isoformat()
    chart['birth_a_utc'] = birth_a.astimezone(timezone.utc).isoformat()
    chart['birth_b_utc'] = birth_b.astimezone(timezone.utc).isoformat()

    return chart


def synastry_aspects(chart_a, chart_b, orb=6):
    """
    Calculate inter-chart aspects between two natal charts.

    Args:
        chart_a: First natal chart
        chart_b: Second natal chart
        orb: Aspect orb in degrees

    Returns:
        List of synastry aspects
    """
    from chart_engine import ASPECTS, BODIES

    aspects = []
    names = [n for n, _ in BODIES]

    for a in names:
        if a not in chart_a['planets']:
            continue
        for b in names:
            if b not in chart_b['planets']:
                continue

            lon_a = chart_a['planets'][a]['longitude']
            lon_b = chart_b['planets'][b]['longitude']

            sep = abs((lon_a - lon_b + 180) % 360 - 180)

            for aspect_name, angle in ASPECTS:
                if abs(sep - angle) <= orb:
                    aspects.append({
                        'person_a_planet': a,
                        'person_b_planet': b,
                        'aspect': aspect_name,
                        'angle': round(sep, 2),
                        'orb': round(abs(sep - angle), 2),
                        'applying': None  # Would require speed calculation
                    })

    return sorted(aspects, key=lambda x: x['orb'])


def composite_report(chart_a, chart_b, lat, lon, settings):
    """
    Generate complete composite analysis including both midpoint and Davison charts.

    Returns:
        Dictionary with midpoint_composite, synastry_aspects, and optionally davison
    """
    result = {
        'midpoint_composite': midpoint_chart(chart_a, chart_b, lat, lon, settings),
        'synastry_aspects': synastry_aspects(chart_a, chart_b, settings.get('aspect_orb_degrees', 6))
    }

    return result


if __name__ == '__main__':
    print("Composite chart module - import and use functions from other scripts")
    print("Example: from composite_charts import midpoint_chart, davison_chart, synastry_aspects")
