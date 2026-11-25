#!/usr/bin/env python3
"""Offline sunrise-based Vedic calendar for one Gregorian month."""

import argparse
import calendar
import json
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from chart_engine import jd_at, panchanga_at_instant, set_ayanamsha  # noqa: E402


def _julian_day(value):
    return jd_at(value)


def sunrise_for_day(day, timezone, latitude, longitude, altitude=0):
    """Return the local sunrise for a location/date, or raise if none is found."""
    zone = ZoneInfo(timezone)
    local_midnight = datetime.combine(day, time.min, tzinfo=zone)
    start_jd = _julian_day(local_midnight)
    result, times = swe.rise_trans(
        start_jd,
        swe.SUN,
        swe.CALC_RISE | swe.BIT_DISC_CENTER,
        (longitude, latitude, altitude),
        0.0,
        15.0,
        swe.FLG_MOSEPH,
    )
    if result != 0:
        raise ValueError(f"Sunrise unavailable for {day.isoformat()} at this location")
    sunrise_utc = swe.revjul(times[0], swe.GREG_CAL)
    year, month, day_num, hour = sunrise_utc
    hour_int = int(hour)
    minute_float = (hour - hour_int) * 60
    minute_int = int(minute_float)
    second = round((minute_float - minute_int) * 60)
    utc = datetime(year, month, day_num, hour_int, minute_int, tzinfo=ZoneInfo("UTC"))
    utc += timedelta(seconds=second)
    local = utc.astimezone(zone)
    if local.date() != day:
        raise ValueError(f"Sunrise fell outside local date {day.isoformat()}")
    return local


def panchanga_at_sunrise(day, timezone, latitude, longitude, ayanamsha="lahiri", altitude=0):
    """Calculate sunrise-based Panchanga limbs using sidereal Moshier positions."""
    sunrise = sunrise_for_day(day, timezone, latitude, longitude, altitude)
    jd = _julian_day(sunrise)
    mode = set_ayanamsha({"ayanamsha": ayanamsha})
    flags = swe.FLG_MOSEPH | swe.FLG_SIDEREAL
    sun, sun_flags = swe.calc_ut(jd, swe.SUN, flags)
    moon, moon_flags = swe.calc_ut(jd, swe.MOON, flags)
    if not (sun_flags & swe.FLG_MOSEPH and moon_flags & swe.FLG_MOSEPH):
        raise ValueError("Requested Moshier ephemeris was not returned")
    limbs = panchanga_at_instant(sun[0], moon[0], day)
    return {
        "date": day.isoformat(),
        "sunrise_local": sunrise.isoformat(),
        "timezone": timezone,
        "coordinates": {"latitude": latitude, "longitude": longitude, "altitude_m": altitude},
        "ayanamsha": mode,
        "ephemeris": "PySwissEph Moshier",
        **limbs,
        "day_boundary": "sunrise",
    }


def month_calendar(year, month, timezone, latitude, longitude, ayanamsha="lahiri", altitude=0):
    if not 1800 <= year <= 2399:
        raise ValueError("year must be in 1800–2399")
    if not 1 <= month <= 12:
        raise ValueError("month must be in 1–12")
    ZoneInfo(timezone)
    first_weekday, count = calendar.monthrange(year, month)
    days = [
        panchanga_at_sunrise(
            date(year, month, day), timezone, latitude, longitude, ayanamsha, altitude
        )
        for day in range(1, count + 1)
    ]
    return {
        "year": year,
        "month": month,
        "timezone": timezone,
        "location": {"latitude": latitude, "longitude": longitude, "altitude_m": altitude},
        "week_starts_on": "Monday",
        "leading_blank_days": first_weekday,
        "days": days,
        "scope_note": "Tithi at sunrise; not a regional festival or vrat determination.",
    }


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--timezone", required=True, help="IANA timezone, for example Asia/Kolkata")
    parser.add_argument("--latitude", type=float, required=True)
    parser.add_argument("--longitude", type=float, required=True)
    parser.add_argument("--altitude", type=float, default=0)
    parser.add_argument(
        "--ayanamsha", choices=["lahiri", "raman", "krishnamurti", "drik"], default="lahiri"
    )
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not -89.9 <= args.latitude <= 89.9 or not -180 <= args.longitude <= 180:
        parser.error("coordinates are outside supported limits")
    if not -500 <= args.altitude <= 9000:
        parser.error("altitude must be between -500 and 9000 metres")
    try:
        result = month_calendar(
            args.year,
            args.month,
            args.timezone,
            args.latitude,
            args.longitude,
            args.ayanamsha,
            args.altitude,
        )
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"written: {args.out}")
        return 0
    except (ValueError, KeyError, swe.Error) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(cli())
