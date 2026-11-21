#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Relocation (locality) chart calculations."""

from datetime import datetime

from chart_engine import jd_at, make_chart, set_ayanamsha


def relocation_chart(natal_chart_data, new_lat, new_lon, settings):
    """
    Calculate relocation chart for same birth time at new location.

    A relocation chart recalculates the houses and angles for the same
    birth moment but at a different geographic location. Planet positions
    remain the same, but the Ascendant, Midheaven, and house cusps change.

    Args:
        natal_chart_data: Original natal chart data with birth info
        new_lat: New location latitude
        new_lon: New location longitude
        settings: Chart calculation settings

    Returns:
        Relocated chart with new angles and houses
    """
    # Accept the full calculator report and the original standalone input shape.
    if 'provenance' in natal_chart_data:
        birth_dt = natal_chart_data['provenance']['birth_utc']
        natal_location = natal_chart_data['input']['birth']
        natal_zodiac = 'tropical'
    else:
        birth_dt = natal_chart_data.get('birth_datetime')
        natal_location = natal_chart_data
        natal_zodiac = natal_chart_data['zodiac']
    if not birth_dt:
        raise ValueError("natal_chart_data must include 'birth_datetime' field")

    if isinstance(birth_dt, str):
        birth_dt = datetime.fromisoformat(birth_dt)
    if birth_dt.utcoffset() is None:
        raise ValueError('Relocation requires a birth timestamp with a UTC offset')

    # Calculate JD for birth moment
    jd = jd_at(birth_dt)

    # Recalculate chart at new location
    sidereal = settings.get('zodiac', natal_zodiac) == 'sidereal'
    relocated = make_chart(jd, new_lat, new_lon, settings, sidereal)

    # Add metadata
    relocated['type'] = 'relocation'
    relocated['method'] = 'Locality chart - natal planets at relocated angles'
    relocated['natal_location'] = {
        'latitude': natal_location.get('latitude'),
        'longitude': natal_location.get('longitude')
    }
    relocated['relocated_location'] = {
        'latitude': new_lat,
        'longitude': new_lon
    }
    relocated['birth_datetime'] = birth_dt.isoformat()

    # Note: Planet positions are identical, only angles and houses differ
    relocated['note'] = 'Planetary positions unchanged from natal; angles and houses recalculated for new location'

    return relocated


def astrocartography_line(planet_name, line_type, latitude, birth_jd, settings):
    """
    Calculate longitude where a planet is on a specific angle (ASC/DSC/MC/IC).

    This is a simplified astrocartography calculator for a single latitude line.
    Full astrocartography requires iterating over many latitudes and longitudes.

    Args:
        planet_name: Name of planet (Sun, Moon, etc.)
        line_type: 'ASC', 'DSC', 'MC', or 'IC'
        latitude: Latitude to check
        birth_jd: Julian day of birth
        settings: Chart settings

    Returns:
        Longitude where planet is on specified angle, or None if not found
    """
    import swisseph as swe

    body_map = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO
    }

    if planet_name not in body_map:
        return None

    body = body_map[planet_name]
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED

    if settings.get('zodiac') == 'sidereal':
        set_ayanamsha(settings)
        flags |= swe.FLG_SIDEREAL

    # Get planet position
    planet_pos, _ = swe.calc_ut(birth_jd, body, flags)
    planet_lon = planet_pos[0]

    # Search for longitude where planet is on desired angle
    # This is simplified - full implementation would use swe.houses and iteration
    for test_lon in range(-180, 180, 1):
        hs = settings['western_houses'].encode('ascii')
        cusps, angles = swe.houses_ex(birth_jd, latitude, test_lon, hs,
                                      swe.FLG_SIDEREAL if settings.get('zodiac') == 'sidereal' else 0)

        if line_type == 'ASC':
            angle_lon = angles[0]
        elif line_type == 'MC':
            angle_lon = angles[1]
        elif line_type == 'DSC':
            angle_lon = (angles[0] + 180) % 360
        elif line_type == 'IC':
            angle_lon = (angles[1] + 180) % 360
        else:
            continue

        # Check if planet is within 1 degree of angle
        diff = abs((planet_lon - angle_lon + 180) % 360 - 180)
        if diff < 1.0:
            return test_lon

    return None


if __name__ == '__main__':
    print("Relocation chart module")
    print("Functions: relocation_chart, astrocartography_line")
