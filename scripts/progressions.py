#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Secondary progressions and solar return calculations."""

from datetime import datetime, timedelta, timezone

import swisseph as swe

from chart_engine import make_chart, jd_at, parse_birth


def secondary_progressions(birth_dt, target_dt, lat, lon, settings):
    """
    Calculate secondary progressions (day-for-a-year method).

    One day after birth = one year of life.

    Args:
        birth_dt: Birth datetime (aware)
        target_dt: Target date for progressions (aware)
        lat: Birth latitude
        lon: Birth longitude
        settings: Chart calculation settings

    Returns:
        Progressed chart data
    """
    # Calculate age in years
    birth_utc = birth_dt.astimezone(timezone.utc)
    target_utc = target_dt.astimezone(timezone.utc)

    age_days = (target_utc - birth_utc).total_seconds() / 86400
    age_years = age_days / 365.25

    # Progress birth time by one day per year
    progressed_dt = birth_utc + timedelta(days=age_years)

    jd = jd_at(progressed_dt)
    sidereal = settings.get('zodiac') == 'sidereal'

    chart = make_chart(jd, lat, lon, settings, sidereal)

    chart['type'] = 'secondary_progressions'
    chart['method'] = 'Day-for-a-year secondary progressions'
    chart['birth_utc'] = birth_utc.isoformat()
    chart['target_date_utc'] = target_utc.isoformat()
    chart['progressed_date_utc'] = progressed_dt.isoformat()
    chart['age_years'] = round(age_years, 2)

    return chart


def solar_return(birth_dt, year, lat, lon, settings):
    """
    Calculate solar return chart for a given year.

    Solar return occurs when transiting Sun returns to natal Sun position.

    Args:
        birth_dt: Birth datetime (aware)
        year: Year for solar return
        lat: Location latitude for return (can be birth location or current residence)
        lon: Location longitude for return
        settings: Chart calculation settings

    Returns:
        Solar return chart data
    """
    birth_jd = jd_at(birth_dt)

    # Get natal Sun position
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    if settings.get('zodiac') == 'sidereal':
        flags |= swe.FLG_SIDEREAL
        ayanamsha_name = settings.get('ayanamsha', 'lahiri')
        modes = {
            'lahiri': swe.SIDM_LAHIRI,
            'raman': swe.SIDM_RAMAN,
            'krishnamurti': swe.SIDM_KRISHNAMURTI,
            'kp': swe.SIDM_KRISHNAMURTI,
        }
        swe.set_sid_mode(modes.get(ayanamsha_name, swe.SIDM_LAHIRI))

    natal_sun, _ = swe.calc_ut(birth_jd, swe.SUN, flags)
    natal_sun_lon = natal_sun[0]

    # Find when Sun returns to natal position in target year
    # Start from birthday in target year
    birth_month_day = birth_dt.replace(year=year, tzinfo=timezone.utc)
    search_jd = jd_at(birth_month_day)

    # Search within +/- 2 days of birthday
    best_jd = search_jd
    min_diff = 360

    for offset in range(-2, 3):
        test_jd = search_jd + offset + (0.5 / 24)  # Search at noon
        for hour_offset in range(48):  # Half-hour increments
            current_jd = test_jd + (hour_offset * 0.5 / 24)
            sun_pos, _ = swe.calc_ut(current_jd, swe.SUN, flags)
            diff = abs((sun_pos[0] - natal_sun_lon + 180) % 360 - 180)

            if diff < min_diff:
                min_diff = diff
                best_jd = current_jd

    # Calculate chart for solar return time
    sidereal = settings.get('zodiac') == 'sidereal'
    chart = make_chart(best_jd, lat, lon, settings, sidereal)

    # Convert JD back to datetime
    solar_return_dt = datetime(*swe.revjul(best_jd, 1)[:6], tzinfo=timezone.utc)

    chart['type'] = 'solar_return'
    chart['year'] = year
    chart['solar_return_datetime_utc'] = solar_return_dt.isoformat()
    chart['natal_sun_longitude'] = natal_sun_lon
    chart['return_sun_longitude'] = chart['planets']['Sun']['longitude']
    chart['orb_degrees'] = round(min_diff, 4)

    return chart


def lunar_return(birth_dt, target_month, lat, lon, settings):
    """
    Calculate lunar return chart (Moon returns to natal position).

    Args:
        birth_dt: Birth datetime (aware)
        target_month: Target month datetime (aware) to find lunar return near
        lat: Location latitude
        lon: Location longitude
        settings: Chart calculation settings

    Returns:
        Lunar return chart data
    """
    birth_jd = jd_at(birth_dt)

    # Get natal Moon position
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    if settings.get('zodiac') == 'sidereal':
        flags |= swe.FLG_SIDEREAL

    natal_moon, _ = swe.calc_ut(birth_jd, swe.MOON, flags)
    natal_moon_lon = natal_moon[0]

    # Search for Moon return near target month
    search_jd = jd_at(target_month)

    best_jd = search_jd
    min_diff = 360

    # Search within +/- 15 days
    for day_offset in range(-15, 16):
        for hour in range(24):
            current_jd = search_jd + day_offset + (hour / 24)
            moon_pos, _ = swe.calc_ut(current_jd, swe.MOON, flags)
            diff = abs((moon_pos[0] - natal_moon_lon + 180) % 360 - 180)

            if diff < min_diff:
                min_diff = diff
                best_jd = current_jd

    sidereal = settings.get('zodiac') == 'sidereal'
    chart = make_chart(best_jd, lat, lon, settings, sidereal)

    lunar_return_dt = datetime(*swe.revjul(best_jd, 1)[:6], tzinfo=timezone.utc)

    chart['type'] = 'lunar_return'
    chart['lunar_return_datetime_utc'] = lunar_return_dt.isoformat()
    chart['natal_moon_longitude'] = natal_moon_lon
    chart['return_moon_longitude'] = chart['planets']['Moon']['longitude']
    chart['orb_degrees'] = round(min_diff, 4)

    return chart


if __name__ == '__main__':
    print("Progressions and returns module")
    print("Functions: secondary_progressions, solar_return, lunar_return")
