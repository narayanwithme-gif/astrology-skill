#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Composite and relationship chart calculations."""

from datetime import timezone

from chart_engine import jd_at, make_chart, pos


def _midpoint(a, b):
    difference = (b - a + 180) % 360 - 180
    if difference == -180:
        # Exact oppositions have two equally short arcs. Choose a stable axis.
        return (min(a, b) + 90) % 360
    return (a + difference / 2) % 360


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
    if chart_a["zodiac"] != chart_b["zodiac"] or chart_a.get("ayanamsha") != chart_b.get("ayanamsha"):
        raise ValueError("Composite charts require matching zodiac and ayanamsha")
    planets_composite = {}

    for planet in chart_a['planets'].keys():
        if planet not in chart_b['planets']:
            continue

        lon_a = chart_a['planets'][planet]['longitude']
        lon_b = chart_b['planets'][planet]['longitude']

        planets_composite[planet] = {
            **pos(_midpoint(lon_a, lon_b)),
            'method': 'midpoint',
            'source_a_longitude': lon_a,
            'source_b_longitude': lon_b
        }

    return {
        'type': 'midpoint_composite',
        'zodiac': chart_a['zodiac'],
        'ascendant': pos(_midpoint(chart_a['ascendant']['longitude'],
                                   chart_b['ascendant']['longitude'])),
        'midheaven': pos(_midpoint(chart_a['midheaven']['longitude'],
                                   chart_b['midheaven']['longitude'])),
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
    chart['method'] = 'Davison midpoint time at supplied location'
    chart['location'] = {'latitude': lat, 'longitude': lon}
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
    Generate a midpoint composite and synastry aspect table.

    Returns:
        Dictionary with midpoint_composite and synastry_aspects
    """
    result = {
        'midpoint_composite': midpoint_chart(chart_a, chart_b, lat, lon, settings),
        'synastry_aspects': synastry_aspects(chart_a, chart_b, settings.get('aspect_orb_degrees', 6))
    }

    return result


if __name__ == '__main__':
    print("Composite chart module - import and use functions from other scripts")
    print("Example: from composite_charts import midpoint_chart, davison_chart, synastry_aspects")
