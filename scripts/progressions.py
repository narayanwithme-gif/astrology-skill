#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Day-for-a-year progressions and nearest solar/lunar returns."""

from datetime import datetime, timedelta, timezone

import swisseph as swe
from chart_engine import jd_at, make_chart, set_ayanamsha


def secondary_progressions(birth_dt, target_dt, lat, lon, settings):
    birth_utc = _utc(birth_dt)
    target_utc = _utc(target_dt)
    age_years = (target_utc - birth_utc) / timedelta(days=365.25)
    if age_years < 0:
        raise ValueError("Progression target must be at or after birth")
    progressed_dt = birth_utc + timedelta(days=age_years)
    chart = make_chart(
        jd_at(progressed_dt), lat, lon, settings, settings.get("zodiac") == "sidereal"
    )
    return {
        **chart,
        "type": "secondary_progressions",
        "method": "One ephemeris day per 365.25 elapsed days",
        "birth_utc": birth_utc.isoformat(),
        "target_date_utc": target_utc.isoformat(),
        "progressed_date_utc": progressed_dt.isoformat(),
        "age_years": round(age_years, 2),
    }


def solar_return(birth_dt, year, lat, lon, settings):
    birth_utc = _utc(birth_dt)
    # February 29 maps to February 28 for the search anchor in a common year.
    try:
        anchor = birth_utc.replace(year=year)
    except ValueError:
        anchor = birth_utc.replace(year=year, day=28)
    chart = _return_chart(birth_dt, anchor, lat, lon, settings, swe.SUN, "Sun", 3)
    return {**chart, "year": year}


def lunar_return(birth_dt, target_month, lat, lon, settings):
    """Find the lunar return closest to the supplied instant."""
    return _return_chart(birth_dt, _utc(target_month), lat, lon, settings, swe.MOON, "Moon", 16)


def _return_chart(birth, anchor, lat, lon, settings, body, name, window):
    sidereal = settings.get("zodiac") == "sidereal"
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED
    if sidereal:
        set_ayanamsha(settings)
        flags |= swe.FLG_SIDEREAL

    def longitude(jd):
        position, returned_flags = swe.calc_ut(jd, body, flags)
        if not returned_flags & swe.FLG_MOSEPH:
            raise ValueError("Return calculation engine mismatch")
        return position[0]

    natal = longitude(jd_at(_utc(birth)))

    def signed_difference(jd):
        return (longitude(jd) - natal + 180) % 360 - 180

    center = jd_at(anchor)
    crossings = []
    left = center - window
    left_delta = signed_difference(left)
    for step in range(1, window * 2 + 1):
        right = center - window + step
        right_delta = signed_difference(right)
        # The signed difference jumps downward at opposition. A return crosses zero upward.
        if left_delta <= 0 < right_delta:
            lo, hi = left, right
            while hi - lo > 1e-8:
                midpoint = (lo + hi) / 2
                if signed_difference(midpoint) < 0:
                    lo = midpoint
                else:
                    hi = midpoint
            crossings.append((lo + hi) / 2)
        left, left_delta = right, right_delta
    if not crossings:
        raise ValueError(f"No {name} return found within {window} days of the anchor")

    jd = min(crossings, key=lambda candidate: abs(candidate - center))
    chart = make_chart(jd, lat, lon, settings, sidereal)
    year, month, day, hour = swe.revjul(jd, swe.GREG_CAL)
    instant = datetime(year, month, day, tzinfo=timezone.utc) + timedelta(hours=hour)
    kind = "solar_return" if body == swe.SUN else "lunar_return"
    return {
        **chart,
        "type": kind,
        f"{kind}_datetime_utc": instant.isoformat(),
        f"natal_{name.lower()}_longitude": natal,
        f"return_{name.lower()}_longitude": chart["planets"][name]["longitude"],
        "orb_degrees": abs(signed_difference(jd)),
    }


def _utc(instant):
    if instant.utcoffset() is None:
        raise ValueError("Return and progression timestamps must include a UTC offset")
    return instant.astimezone(timezone.utc)
