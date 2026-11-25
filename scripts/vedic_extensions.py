#!/usr/bin/env python3
"""Optional offline Vedic festival, vrata and dasha tools powered by PyJHora."""

import argparse
import contextlib
import io
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    # PyJHora currently emits path diagnostics during import; keep the CLI's
    # stdout machine-readable JSON by containing that import-time output.
    with contextlib.redirect_stdout(io.StringIO()):
        from jhora import const
        from jhora.horoscope.dhasa import dhasa_selector
        from jhora.panchanga import drik, vratha
except ImportError as exc:  # pragma: no cover - exercised by installation smoke test
    raise SystemExit(
        "Full Vedic features need the optional offline package: "
        "python -m pip install 'hermes-astrology[vedic-full]'"
    ) from exc


SOURCE = "PyJHora 5.0.6 (AGPL-3.0-or-later), local package data and calculations"
_DASHA_GROUPS = [
    ("graha", const.planet_dhasas),
    ("rashi", const.rasi_dhasas),
    ("nakshatra", const.nakshathra_dhasas),
    ("karaka", const.karaka_dhasas),
    ("special", const.special_dhasas),
]
_VRATA_NAMES = sorted(vratha.special_vratha_map)
_CALENDARS = {
    "traditional": {0, 1, 2, 7},  # solar, amanta, purnimanta, Nepal Bikram Sambat
    "solar": {0},
    "amanta": {1},
    "purnimanta": {2},
    "nepal-bikram-sambat": {7},
    "all": set(range(len(const.CALENDAR_TYPE))),
}


def language_catalog():
    """Return source-provided UI language identifiers and native names."""
    return [
        {"code": code, "name": name, "translation_source": SOURCE}
        for code, name in const.available_languages_native.items()
    ]


def dasha_catalog():
    """Return only dasha names with both selector paths wired in the source."""
    supported = set(dhasa_selector.list_supported_dhasas())
    rows = [
        {"name": name, "group": group, "selector_wired": True}
        for group, names in _DASHA_GROUPS
        for name in names
        if name in supported
    ]
    return {
        "source": SOURCE,
        "count": len(rows),
        "systems": rows,
        "scope_note": (
            "This is a source-derived catalog of methods with root and child selectors. It does not "
            "claim this project computes every listed system or that each variant has independent validation."
        ),
    }


def _place(day, timezone, latitude, longitude, place_name):
    if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
        raise ValueError("coordinates are outside supported limits")
    zone = ZoneInfo(timezone)
    noon = datetime.combine(day, datetime.min.time().replace(hour=12), tzinfo=zone)
    offset = noon.utcoffset()
    if offset is None:
        raise ValueError(f"Cannot determine UTC offset for {timezone}")
    return drik.Place(place_name, latitude, longitude, offset.total_seconds() / 3600)


def _date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid ISO date: {value}") from exc


def _translated_festival(row, language):
    code = language
    key = f"Festival_{code}"
    translated = row.get(key, "").strip()
    english = row.get("Festival_en", row.get("Festival_name", "")).strip()
    return translated or english


def _local_wall_time(day_tuple, hours):
    if hours is None:
        return None
    day = date(*day_tuple)
    moment = datetime.combine(day, datetime.min.time()) + timedelta(seconds=round(hours * 3600))
    return moment.isoformat(timespec="seconds")


def festival_calendar(
    start, end, timezone, latitude, longitude, language="en", place_name="", calendar="traditional"
):
    """Return source-calendar matches for each civil day in an inclusive range."""
    start_day, end_day = _date(start), _date(end)
    if end_day < start_day:
        raise ValueError("end date must be on or after start date")
    if (end_day - start_day).days > 366:
        raise ValueError("date range cannot exceed 367 days")
    if language not in const.available_languages_native:
        raise ValueError(f"Unsupported language code: {language}")
    if calendar not in _CALENDARS:
        raise ValueError(f"Unsupported calendar preset: {calendar}")
    vratha.load_festival_data()
    result = []
    cursor = start_day
    while cursor <= end_day:
        place = _place(cursor, timezone, latitude, longitude, place_name)
        matches = vratha.get_festivals_between_the_dates(
            drik.Date(cursor.year, cursor.month, cursor.day),
            drik.Date(cursor.year, cursor.month, cursor.day),
            place,
        )
        rows = matches[0][1] if matches else []
        rows = [row for row in rows if int(row.get("calendar_type", -1)) in _CALENDARS[calendar]]
        result.append(
            {
                "date": cursor.isoformat(),
                "festivals": [
                    {
                        "name": _translated_festival(row, language),
                        "name_en": row.get("Festival_en", row.get("Festival_name", "")),
                        "calendar_type": row.get("calendar_type", ""),
                        "source_rule": "PyJHora multilingual festival dataset criteria",
                    }
                    for row in rows
                ],
            }
        )
        cursor += timedelta(days=1)
    return {
        "source": SOURCE,
        "location": {
            "name": place_name,
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
        },
        "language": language,
        "calendar": calendar,
        "dates": result,
        "convention_note": (
            "Dates follow the selected rows in the upstream dataset and its calendar-type, "
            "sunrise-tithi, nakshatra, month and day-offset matching rules. This is not a "
            "universal pan-Indian observance ruling; confirm local sampradaya/panchanga practice."
        ),
        "translation_note": (
            "The upstream festival dataset contains full-name fields only for English, Tamil, "
            "Telugu, Kannada, Hindi and Malayalam. Other selected languages fall back to English. "
            "Upstream language resources are not represented as independently reviewed here."
        ),
    }


def vrata_dates(start, end, vrata_name, timezone, latitude, longitude, place_name=""):
    """Find source-engine special vrata dates for an inclusive date range."""
    start_day, end_day = _date(start), _date(end)
    if end_day < start_day:
        raise ValueError("end date must be on or after start date")
    if (end_day - start_day).days > 366:
        raise ValueError("date range cannot exceed 367 days")
    if vrata_name not in vratha.special_vratha_map:
        raise ValueError(
            f"Unsupported vrata name: {vrata_name}; choose from {', '.join(_VRATA_NAMES)}"
        )
    rows = []
    segment_start = start_day
    cursor = start_day + timedelta(days=1)
    segment_offset = _place(start_day, timezone, latitude, longitude, place_name).timezone
    while cursor <= end_day + timedelta(days=1):
        next_offset = None
        if cursor <= end_day:
            next_offset = _place(cursor, timezone, latitude, longitude, place_name).timezone
        if cursor > end_day or next_offset != segment_offset:
            place = _place(segment_start, timezone, latitude, longitude, place_name)
            segment_end = cursor - timedelta(days=1)
            day_rows = (
                vratha.special_vratha_dates(
                    place,
                    drik.Date(
                        (segment_start - timedelta(days=1)).year,
                        (segment_start - timedelta(days=1)).month,
                        (segment_start - timedelta(days=1)).day,
                    ),
                    drik.Date(
                        (segment_end + timedelta(days=1)).year,
                        (segment_end + timedelta(days=1)).month,
                        (segment_end + timedelta(days=1)).day,
                    ),
                    vratha_type=vrata_name,
                )
                or []
            )
            rows.extend(row for row in day_rows if segment_start <= date(*row[0]) <= segment_end)
            if cursor <= end_day:
                segment_start = cursor
                segment_offset = next_offset
        cursor += timedelta(days=1)
    return {
        "source": SOURCE,
        "vrata": vrata_name,
        "location": {
            "name": place_name,
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
        },
        "dates": [
            {
                "date": f"{row[0][0]:04d}-{row[0][1]:02d}-{row[0][2]:02d}",
                "start_local": _local_wall_time(row[0], row[1]),
                "end_local": _local_wall_time(row[0], row[2]),
                "start_local_hour": row[1],
                "end_local_hour": row[2],
                "label": row[3],
            }
            for row in rows
        ],
        "convention_note": (
            "Uses PyJHora's named special-vrata rule. Exact observance can vary by regional "
            "calendar, sunrise/sunset rule, and sampradaya; verify before acting on a date."
        ),
    }


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("languages", help="list the 22 upstream UI language identifiers")
    sub.add_parser("dashas", help="list supported dasha selector names")
    for command in ("festivals", "vratas"):
        item = sub.add_parser(command)
        item.add_argument("--start", required=True, help="inclusive YYYY-MM-DD")
        item.add_argument("--end", required=True, help="inclusive YYYY-MM-DD")
        item.add_argument("--timezone", required=True, help="IANA timezone")
        item.add_argument("--latitude", type=float, required=True)
        item.add_argument("--longitude", type=float, required=True)
        item.add_argument("--place", default="")
        item.add_argument("--out", type=Path)
        if command == "festivals":
            item.add_argument(
                "--language", choices=sorted(const.available_languages_native), default="en"
            )
            item.add_argument("--calendar", choices=sorted(_CALENDARS), default="traditional")
        else:
            item.add_argument("--vrata", choices=_VRATA_NAMES, required=True)
    args = parser.parse_args()
    if args.command == "languages":
        result = {
            "source": SOURCE,
            "count": len(language_catalog()),
            "languages": language_catalog(),
        }
    elif args.command == "dashas":
        result = dasha_catalog()
    elif args.command == "festivals":
        result = festival_calendar(
            args.start,
            args.end,
            args.timezone,
            args.latitude,
            args.longitude,
            args.language,
            args.place,
            args.calendar,
        )
    else:
        result = vrata_dates(
            args.start,
            args.end,
            args.vrata,
            args.timezone,
            args.latitude,
            args.longitude,
            args.place,
        )
    output = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if getattr(args, "out", None):
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
        print(f"written: {args.out}")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(cli())
