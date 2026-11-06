#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Offline, explicit-convention astrology calculation and standalone chart atlas."""

import argparse
import hashlib
import html
import importlib.metadata
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import swisseph as swe

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine_utils import ASPECTS, LORDS, NAK, SIGNS, YEARS, UTC, number  # noqa: F401  (re-exported)

BODIES = [
    (n, getattr(swe, n.upper()))
    for n in [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]
]
CLASSICAL = [n for n, _ in BODIES[:7]] + ["Rahu", "Ketu"]
ASPECTS = [("conjunction", 0), ("sextile", 60), ("square", 90), ("trine", 120), ("opposition", 180)]
ABBR = dict(
    zip(
        [n for n, _ in BODIES] + ["Rahu", "Ketu"],
        ["Su", "Mo", "Me", "Ve", "Ma", "Ju", "Sa", "Ur", "Ne", "Pl", "Ra", "Ke"],
    )
)
UTC = timezone.utc  # keep local alias for existing call sites


def parse_birth(b):
    naive = datetime.fromisoformat(b["date"] + "T" + b["time"])
    if naive.tzinfo is not None or not 1800 <= naive.year <= 2399:
        raise ValueError("Birth must be local wall time, Gregorian year 1800–2399")
    zone = ZoneInfo(b["timezone"])
    choices = []
    for fold in [0, 1]:
        candidate = naive.replace(tzinfo=zone, fold=fold)
        if candidate.astimezone(UTC).astimezone(zone).replace(tzinfo=None) == naive:
            choices.append(candidate)
    if not choices:
        raise ValueError("Nonexistent local time in this timezone (DST gap)")
    ambiguous = len({v.utcoffset() for v in choices}) > 1
    if ambiguous and "fold" not in b:
        raise ValueError("Ambiguous repeated local time; specify birth.fold=0 or 1")
    fold = b.get("fold", 0)
    if type(fold) is not int or fold not in (0, 1):
        raise ValueError("birth.fold must be 0 or 1")
    return naive.replace(tzinfo=zone, fold=fold)


def jd_at(dt):
    u = dt.astimezone(UTC)
    return swe.julday(
        u.year, u.month, u.day, u.hour + u.minute / 60 + (u.second + u.microsecond / 1e6) / 3600
    )


def pos(lon):
    lon %= 360
    si = int(lon // 30)
    return {"longitude": lon, "sign_index": si, "sign": SIGNS[si], "degree_in_sign": lon % 30}


def degree(lon):
    # Round before splitting so 29d59m60s is never displayed.
    total = round((lon % 360) * 3600) % (360 * 3600)
    si, within = divmod(total, 30 * 3600)
    d, rem = divmod(within, 3600)
    m, s = divmod(rem, 60)
    return f"{SIGNS[si]} {d:02d}°{m:02d}′{s:02d}″"


def house_of(lon, cusps):
    for i, start in enumerate(cusps):
        if (lon - start) % 360 < (cusps[(i + 1) % 12] - start) % 360:
            return i + 1
    raise ValueError("House boundaries do not partition the ecliptic")


def varga_longitude(lon, division):
    if division == 9:
        return lon * 9 % 360
    si = int(lon // 30)
    part = int((lon % 30) // 3)
    start = si if si % 2 == 0 else (si + 8) % 12
    return ((start + part) % 12) * 30 + ((lon % 30) % 3) * 10


def make_chart(jd, lat, lon, settings, sidereal):
    flags = swe.FLG_MOSEPH | swe.FLG_SPEED | (swe.FLG_SIDEREAL if sidereal else 0)
    hs = b"W" if sidereal else settings["western_houses"].encode("ascii")
    cusps, angles = swe.houses_ex(jd, lat, lon, hs, swe.FLG_SIDEREAL if sidereal else 0)
    cusps = list(cusps)
    if (
        len(cusps) != 12
        or abs(sum((cusps[(i + 1) % 12] - cusps[i]) % 360 for i in range(12)) - 360) > 1e-7
    ):
        raise ValueError("House calculation failed or boundaries are not a complete partition")
    planets, returned_flags = {}, {}
    node_id = swe.MEAN_NODE if settings["nodes"] == "mean" else swe.TRUE_NODE
    for name, body in BODIES + [("Rahu", node_id)]:
        x, ret = swe.calc_ut(jd, body, flags)
        if not (ret & swe.FLG_MOSEPH):
            raise ValueError("Requested analytical Moshier engine was not returned")
        planets[name] = {
            **pos(x[0]),
            "latitude": x[1],
            "speed_deg_day": x[3],
            "retrograde": x[3] < 0,
            "house": house_of(x[0], cusps),
        }
        returned_flags[name] = ret
    rahu = planets["Rahu"]
    planets["Ketu"] = {
        **pos(rahu["longitude"] + 180),
        "latitude": -rahu["latitude"],
        "speed_deg_day": rahu["speed_deg_day"],
        "retrograde": rahu["retrograde"],
        "house": house_of(rahu["longitude"] + 180, cusps),
    }
    result = {
        "zodiac": "sidereal" if sidereal else "tropical",
        "house_method": hs.decode(),
        "cusps": cusps,
        "ascendant": pos(angles[0]),
        "midheaven": pos(angles[1]),
        "planets": planets,
        "returned_flags": returned_flags,
    }
    if sidereal:
        result["ayanamsha_degrees"] = swe.get_ayanamsa_ut(jd)
        moon = planets["Moon"]["longitude"]
        ni = int(moon / (360 / 27))
        result["moon_nakshatra"] = {
            "index": ni,
            "name": NAK[ni],
            "pada": int((moon % (360 / 27)) / (360 / 108)) + 1,
            "lord": LORDS[ni % 9],
        }
        for division in [9, 10]:
            asc = pos(varga_longitude(angles[0], division))
            vp = {
                n: pos(varga_longitude(p["longitude"], division))
                for n, p in planets.items()
                if n in CLASSICAL
            }
            for p in vp.values():
                p["house"] = (p["sign_index"] - asc["sign_index"]) % 12 + 1
            result[f"D{division}"] = {
                "ascendant": asc,
                "planets": vp,
                "house_method": "whole-sign",
                "rule": "Parashari",
            }
    return result


def aspect_table(moving, natal=None, orb=6):
    names = [n for n, _ in BODIES]
    rows = []
    for i, a in enumerate(names):
        for j, b in enumerate(names):
            if natal is None and j <= i:
                continue
            right = moving[b] if natal is None else natal[b]
            sep = abs((moving[a]["longitude"] - right["longitude"] + 180) % 360 - 180)
            for name, angle in ASPECTS:
                if abs(sep - angle) <= orb:
                    rows.append(
                        {"from": a, "to": b, "aspect": name, "angle": sep, "orb": abs(sep - angle)}
                    )
    return sorted(rows, key=lambda r: r["orb"])


def drishti(chart, targets=None):
    result = []
    for n in CLASSICAL[:7]:
        offsets = {"Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10]}.get(n, [7])
        p = chart["planets"][n]
        for offset in offsets:
            si = (p["sign_index"] + offset - 1) % 12
            target_planets = chart["planets"] if targets is None else targets
            result.append(
                {
                    "graha": n,
                    "aspect_count": offset,
                    "target_sign": SIGNS[si],
                    "target_house": (si - chart["ascendant"]["sign_index"]) % 12 + 1,
                    "target_grahas": [
                        b for b in CLASSICAL if target_planets[b]["sign_index"] == si
                    ],
                }
            )
    return result


def dashas(birth, moon, as_of, year_days):
    ni = int(moon / (360 / 27))
    start_i = ni % 9
    elapsed = (moon % (360 / 27)) / (360 / 27)
    start = birth.astimezone(UTC) - timedelta(days=elapsed * YEARS[LORDS[start_i]] * year_days)
    sequence = []
    current = None
    for i in range(9):
        lord = LORDS[(start_i + i) % 9]
        end = start + timedelta(days=YEARS[lord] * year_days)
        ad_start, subs = start, []
        for j in range(9):
            ad_lord = LORDS[(start_i + i + j) % 9]
            ad_end = ad_start + timedelta(days=YEARS[lord] * YEARS[ad_lord] / 120 * year_days)
            row = {
                "lord": ad_lord,
                "start_utc": ad_start.isoformat(),
                "end_utc": ad_end.isoformat(),
            }
            subs.append(row)
            if start <= as_of < end and ad_start <= as_of < ad_end:
                current = {
                    "mahadasha": lord,
                    "antardasha": ad_lord,
                    **{k: v for k, v in row.items() if k != "lord"},
                }
            ad_start = ad_end
        sequence.append(
            {
                "lord": lord,
                "start_utc": start.isoformat(),
                "end_utc": end.isoformat(),
                "antardashas": subs,
            }
        )
        start = end
    return {
        "year_days": year_days,
        "birth_lord": LORDS[start_i],
        "birth_balance_years": (1 - elapsed) * YEARS[LORDS[start_i]],
        "current": current,
        "mahadashas": sequence,
    }


def signature(w, v):
    return {
        "western_asc_sign": w["ascendant"]["sign"],
        "vedic_asc_sign": v["ascendant"]["sign"],
        "moon_nakshatra": v["moon_nakshatra"]["name"],
        "western_houses": {n: p["house"] for n, p in w["planets"].items()},
        "vedic_houses": {n: p["house"] for n, p in v["planets"].items()},
        **{
            f"D{d}": {
                "asc_sign": v[f"D{d}"]["ascendant"]["sign"],
                "planet_signs": {n: p["sign"] for n, p in v[f"D{d}"]["planets"].items()},
            }
            for d in [9, 10]
        },
    }


def calculate(request):
    b = request["birth"]
    local = parse_birth(b)
    lat = number(b["latitude"], "latitude", -89.9, 89.9)
    lon = number(b["longitude"], "longitude", -180, 180)
    uncertainty = number(b.get("uncertainty_minutes", 0), "uncertainty_minutes", 0, 1440)
    s = {
        "western_houses": "P",
        "ayanamsha": "lahiri",
        "nodes": "mean",
        "dasha_year_days": 365.25,
        "aspect_orb_degrees": 6,
        **request.get("settings", {}),
    }
    if s["western_houses"] not in ["P", "W", "E", "K", "O"] or s["nodes"] not in ["mean", "true"]:
        raise ValueError("Unsupported house method or node mode")
    modes = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "kp": swe.SIDM_KRISHNAMURTI,
        "drik": swe.SIDM_TRUE_CITRA,
    }
    # normalise ayanamsha aliases (kp -> krishnamurti, drik -> true chitra)
    if isinstance(s.get("ayanamsha"), str):
        s["ayanamsha"] = s["ayanamsha"].lower()
        if s["ayanamsha"] in ("kp", "krishnamurti_vp291"):
            s["ayanamsha"] = "krishnamurti"
    if s["ayanamsha"] not in modes:
        raise ValueError("Unsupported ayanamsha")
    s["dasha_year_days"] = number(s["dasha_year_days"], "dasha_year_days", 350, 370)
    s["aspect_orb_degrees"] = number(s["aspect_orb_degrees"], "aspect_orb_degrees", 0, 12)
    now = datetime.fromisoformat(request["as_of"]) if request.get("as_of") else datetime.now(UTC)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("as_of must include an explicit UTC offset")
    if not 1800 <= now.year <= 2399:
        raise ValueError("as_of year must be 1800–2399")
    now = now.astimezone(UTC)
    swe.set_sid_mode(modes[s["ayanamsha"]])
    jd = jd_at(local)
    w, v = [make_chart(jd, lat, lon, s, sidereal) for sidereal in [False, True]]
    tithi = (
        int(((v["planets"]["Moon"]["longitude"] - v["planets"]["Sun"]["longitude"]) % 360) // 12)
        + 1
    )
    v["tithi_at_instant"] = {"number": tithi, "paksha": "Shukla" if tithi <= 15 else "Krishna"}
    v["graha_drishti"] = drishti(v)
    w["aspects"] = aspect_table(w["planets"], orb=s["aspect_orb_degrees"])
    dasha = dashas(local, v["planets"]["Moon"]["longitude"], now, s["dasha_year_days"])
    transit = {}
    for name, sidereal, natal in [("western", False, w), ("jyotisha", True, v)]:
        flags = swe.FLG_MOSEPH | swe.FLG_SPEED | (swe.FLG_SIDEREAL if sidereal else 0)
        planets = {}
        for n, body in BODIES + [
            ("Rahu", swe.MEAN_NODE if s["nodes"] == "mean" else swe.TRUE_NODE)
        ]:
            x, ret = swe.calc_ut(jd_at(now), body, flags)
            if not ret & swe.FLG_MOSEPH:
                raise ValueError("Transit engine mismatch")
            planets[n] = {**pos(x[0]), "speed_deg_day": x[3]}
        planets["Ketu"] = {
            **pos(planets["Rahu"]["longitude"] + 180),
            "speed_deg_day": planets["Rahu"]["speed_deg_day"],
        }
        transit[name] = {"planets": planets}
        if sidereal:
            for p in planets.values():
                p["natal_rashi_house"] = (p["sign_index"] - v["ascendant"]["sign_index"]) % 12 + 1
            transit[name]["graha_drishti_to_natal"] = drishti(
                {"planets": planets, "ascendant": v["ascendant"]}, v["planets"]
            )
        else:
            transit[name]["major_aspect_snapshot"] = aspect_table(
                planets, natal["planets"], s["aspect_orb_degrees"]
            )
    # Use the same apparent, sidereal-aware API to verify the actual longitude offset.
    actual_ayan = swe.get_ayanamsa_ex_ut(jd, swe.FLG_MOSEPH)[1]
    checks = {
        "rahu_ketu_180": all(
            abs((c["planets"]["Ketu"]["longitude"] - c["planets"]["Rahu"]["longitude"]) % 360 - 180)
            < 1e-8
            for c in [w, v]
        ),
        "tropical_sidereal_offset": all(
            abs(
                (
                    (
                        w["planets"][n]["longitude"]
                        - v["planets"][n]["longitude"]
                        - actual_ayan
                        + 180
                    )
                    % 360
                )
                - 180
            )
            < 1e-5
            for n, _ in BODIES
        ),
        "houses_partition": True,
    }
    if not all(checks.values()):
        raise ValueError(f"Internal invariant failed: {checks}")
    warnings = [
        "Computed with local Moshier via Swiss Ephemeris; not independently verified.",
        "Interpretation is not generated by this calculator.",
        "House membership uses ecliptic longitude. No full panchanga, shadbala, ashtakavarga or exact-event search.",
    ]
    sensitivity = None
    if uncertainty:
        base = signature(w, v)
        endpoints = []
        for minutes in [-uncertainty, uncertainty]:
            instant = local.astimezone(UTC) + timedelta(minutes=minutes)
            ew, ev = [
                make_chart(jd_at(instant), lat, lon, s, sidereal) for sidereal in [False, True]
            ]
            sig = signature(ew, ev)
            endpoints.append(
                {
                    "offset_minutes": minutes,
                    "utc": instant.isoformat(),
                    "signature": sig,
                    "changed_fields": [k for k in base if base[k] != sig[k]],
                }
            )
        sensitivity = {
            "central_signature": base,
            "endpoints": endpoints,
            "scope": "Endpoint comparison only; not exhaustive interval verification",
        }
        if any(e["changed_fields"] for e in endpoints):
            warnings.append(
                "Some chart factors change at stated uncertainty endpoints; qualify related readings."
            )
    return {
        "schema_version": "1.0",
        "label": request.get("label", "Private chart"),
        "input": request,
        "provenance": {
            "calculator": "astrology-structured 1.0.0",
            "swisseph_version": swe.version,
            "pyswisseph_version": importlib.metadata.version("pyswisseph"),
            "tzdata_version": importlib.metadata.version("tzdata"),
            "engine": "Moshier analytical; explicit FLG_MOSEPH",
            "frame": "geocentric apparent ecliptic of date",
            "birth_local": local.isoformat(),
            "birth_utc": local.astimezone(UTC).isoformat(),
            "julian_day_ut": jd,
            "as_of_utc": now.isoformat(),
            "settings": s,
            "apparent_sidereal_offset_degrees": actual_ayan,
        },
        "western": w,
        "jyotisha": v,
        "vimshottari": dasha,
        "transits": transit,
        "uncertainty": sensitivity,
        "internal_checks": checks,
        "warnings": warnings,
    }


def table(headers, rows):
    def esc(value):
        return html.escape(str(value))

    return (
        "<table><thead><tr>"
        + "".join("<th>" + esc(x) + "</th>" for x in headers)
        + "</tr></thead><tbody>"
        + "".join(
            "<tr>" + "".join("<td>" + esc(x) + "</td>" for x in row) + "</tr>" for row in rows
        )
        + "</tbody></table>"
    )


def text_svg(x, y, lines, size=12):
    return (
        f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}">'
        + "".join(
            f'<tspan x="{x}" dy="{0 if i == 0 else size + 2}">{html.escape(str(line))}</tspan>'
            for i, line in enumerate(lines)
        )
        + "</text>"
    )


def north(chart, title):
    positions = [
        (200, 82),
        (100, 40),
        (45, 95),
        (90, 190),
        (45, 275),
        (100, 335),
        (200, 275),
        (300, 335),
        (355, 275),
        (310, 190),
        (355, 95),
        (300, 40),
    ]
    svg = (
        '<svg viewBox="0 0 400 400" role="img" aria-label="'
        + html.escape(title)
        + '"><rect x="20" y="20" width="360" height="360" fill="none" stroke="currentColor"/><path d="M20 20L380 380M380 20L20 380M200 20L380 200L200 380L20 200Z" fill="none" stroke="currentColor"/>'
    )
    ai = chart["ascendant"]["sign_index"]
    for i, (x, y) in enumerate(positions):
        si = (ai + i) % 12
        occupants = [
            ABBR[n] for n, p in chart["planets"].items() if n in CLASSICAL and p["house"] == i + 1
        ]
        lines = [f"H{i + 1} {SIGNS[si][:3]}"] + [
            " ".join(occupants[j : j + 3]) for j in range(0, len(occupants), 3)
        ]
        svg += text_svg(x, y, lines, 9 if len(lines) > 3 else 11)
    return svg + "</svg>"


def south(chart, title):
    cells = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
        (3, 2),
        (3, 1),
        (3, 0),
        (2, 0),
        (1, 0),
        (0, 0),
    ]
    svg = '<svg viewBox="0 0 400 400" role="img" aria-label="' + html.escape(title) + '">'
    for si, (r, c) in enumerate(cells):
        x, y = c * 100, r * 100
        names = [
            ABBR[n] for n, p in chart["planets"].items() if n in CLASSICAL and p["sign_index"] == si
        ]
        if chart["ascendant"]["sign_index"] == si:
            names.insert(0, "Asc")
        svg += f'<rect x="{x}" y="{y}" width="100" height="100" fill="none" stroke="currentColor"/>'
        svg += text_svg(
            x + 50,
            y + 20,
            [SIGNS[si]] + [" ".join(names[j : j + 3]) for j in range(0, len(names), 3)],
            11,
        )
    return svg + text_svg(200, 185, ["Fixed signs", "South Indian"], 13) + "</svg>"


def wheel(chart):
    asc = chart["ascendant"]["longitude"]

    def xy(lon, r):
        a = math.radians(lon - asc + 180)
        return 250 + r * math.cos(a), 250 - r * math.sin(a)

    svg = '<svg viewBox="0 0 500 500" role="img" aria-label="Western tropical natal wheel">'
    for r in [150, 205, 240]:
        svg += f'<circle cx="250" cy="250" r="{r}" fill="none" stroke="currentColor"/>'
    for si in range(12):
        x, y = xy(si * 30, 240)
        a, b = xy(si * 30, 205)
        svg += f'<path d="M{x},{y}L{a},{b}" stroke="currentColor"/>'
        x, y = xy(si * 30 + 15, 222)
        svg += text_svg(x, y, [SIGNS[si][:3]], 11)
    for i, cusp in enumerate(chart["cusps"]):
        x, y = xy(cusp, 205)
        a, b = xy(cusp, 55)
        svg += f'<path d="M{x},{y}L{a},{b}" stroke="#b7bdc6"/>'
        mid = cusp + ((chart["cusps"][(i + 1) % 12] - cusp) % 360) / 2
        x, y = xy(mid, 85)
        svg += text_svg(x, y, [str(i + 1)], 12)
    # Radial lanes retain exact longitude while reducing label overlap.
    ordered = sorted(chart["planets"].items(), key=lambda x: x[1]["longitude"])
    for i, (n, p) in enumerate(ordered):
        radius = 112 + (i % 4) * 22
        x, y = xy(p["longitude"], radius)
        a, b = xy(p["longitude"], 201)
        svg += f'<path d="M{a},{b}L{x},{y}" stroke="#7390ae"/>'
        svg += text_svg(x, y, [ABBR[n] + ("R" if p["retrograde"] else "")], 11)
    svg += text_svg(250, 245, ["Tropical", chart["house_method"]], 12)
    return svg + "</svg>"


def atlas(data):
    w, v = data["western"], data["jyotisha"]
    esc = html.escape
    content = (
        "<h1>"
        + esc(data["label"])
        + "</h1><p>Computed chart atlas. Astrology is a traditional symbolic practice, not established prediction. Private birth data is included in this local file.</p>"
    )
    content += "<h2>Calculation manifest</h2>" + table(
        ["Field", "Value"],
        [
            (k, json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else x)
            for k, x in data["provenance"].items()
        ],
    )
    content += (
        "<h2>Western natal wheel</h2><p>Tropical zodiac; "
        + esc(w["house_method"])
        + ' houses. Planet ticks show exact longitudes; labels use radial lanes. Detailed degrees are in the table.</p><div class="single">'
        + wheel(w)
        + "</div>"
    )
    for title, c in [("D1 Rashi", v), ("D9 Navamsha", v["D9"]), ("D10 Dashamsha", v["D10"])]:
        content += (
            "<h2>"
            + title
            + "</h2><p>Sidereal "
            + esc(data["provenance"]["settings"]["ayanamsha"])
            + '; whole-sign houses. North: fixed houses; South: fixed signs. Numbers H1–H12 are houses.</p><div class="grid"><figure>'
            + north(c, title)
            + "<figcaption>North Indian — "
            + title
            + "</figcaption></figure><figure>"
            + south(c, title)
            + "<figcaption>South Indian — "
            + title
            + "</figcaption></figure></div>"
        )
    for title, c in [("Western", w), ("Jyotisha D1", v), ("D9", v["D9"]), ("D10", v["D10"])]:
        content += (
            "<h2>"
            + title
            + " placements</h2>"
            + table(
                ["Body", "Position", "House", "Motion"],
                [
                    (
                        n,
                        degree(p["longitude"]),
                        p["house"],
                        ("R" if p.get("retrograde") else "D") if "retrograde" in p else "derived",
                    )
                    for n, p in c["planets"].items()
                ],
            )
        )
    content += "<h2>House boundaries</h2>" + table(
        ["House", "Western", "Jyotisha D1"],
        [(i + 1, degree(w["cusps"][i]), degree(v["cusps"][i])) for i in range(12)],
    )
    content += "<h2>Western major natal aspects</h2>" + table(
        ["From", "To", "Aspect", "Separation", "Orb"],
        [
            (r["from"], r["to"], r["aspect"], round(r["angle"], 4), round(r["orb"], 4))
            for r in w["aspects"]
        ],
    )
    content += "<h2>Parashari sign-based full graha drishti</h2>" + table(
        ["Graha", "Count", "Target sign", "House", "Grahas"],
        [
            (
                r["graha"],
                r["aspect_count"],
                r["target_sign"],
                r["target_house"],
                ", ".join(r["target_grahas"]),
            )
            for r in v["graha_drishti"]
        ],
    )
    content += "<h2>Moon and lunar day</h2>" + table(
        ["Item", "Value"],
        [
            ("Nakshatra", v["moon_nakshatra"]["name"]),
            ("Pada", v["moon_nakshatra"]["pada"]),
            ("Birth dasha lord", v["moon_nakshatra"]["lord"]),
            ("Tithi at instant", str(v["tithi_at_instant"])),
        ],
    )
    d = data["vimshottari"]
    content += (
        "<h2>Vimshottari</h2><p>Approximate period boundaries; "
        + str(d["year_days"])
        + " days per year. Birth balance "
        + str(round(d["birth_balance_years"], 6))
        + " years. Current: "
        + esc(str(d["current"]))
        + "</p>"
        + table(
            ["MD", "Start UTC", "End UTC"],
            [(x["lord"], x["start_utc"], x["end_utc"]) for x in d["mahadashas"]],
        )
    )
    for md in d["mahadashas"]:
        content += (
            "<details><summary>"
            + esc(md["lord"])
            + " antardashas</summary>"
            + table(
                ["AD", "Start UTC", "End UTC"],
                [(a["lord"], a["start_utc"], a["end_utc"]) for a in md["antardashas"]],
            )
            + "</details>"
        )
    for system, t in data["transits"].items():
        content += (
            "<h2>"
            + system
            + " transit snapshot</h2>"
            + table(
                ["Moving planet", "Position", "Natal Rashi house"],
                [
                    (n, degree(p["longitude"]), p.get("natal_rashi_house", "—"))
                    for n, p in t["planets"].items()
                ],
            )
        )
        if system == "western":
            content += table(
                ["Moving", "Natal", "Aspect", "Orb"],
                [
                    (r["from"], r["to"], r["aspect"], round(r["orb"], 4))
                    for r in t["major_aspect_snapshot"]
                ],
            )
        else:
            content += table(
                [
                    "Moving graha",
                    "Count",
                    "Target natal sign",
                    "Target natal house",
                    "Natal grahas",
                ],
                [
                    (
                        r["graha"],
                        r["aspect_count"],
                        r["target_sign"],
                        r["target_house"],
                        ", ".join(r["target_grahas"]),
                    )
                    for r in t["graha_drishti_to_natal"]
                ],
            )
    content += (
        "<h2>Uncertainty and checks</h2><pre>"
        + esc(
            json.dumps(
                {
                    "checks": data["internal_checks"],
                    "uncertainty": data["uncertainty"],
                    "warnings": data["warnings"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        + "</pre>"
    )
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Private astrology chart atlas</title><style>body{font:16px system-ui;max-width:1120px;margin:auto;padding:28px;color:#243247;background:#faf8f2}h1,h2{color:#163f56}table{border-collapse:collapse;width:100%;margin:18px 0;font-size:14px}td,th{border:1px solid #ccd2d7;padding:7px;text-align:left;overflow-wrap:anywhere}th{background:#e7eef3}.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}svg{width:100%;max-height:520px;display:block}figcaption{text-align:center;padding:8px}.single{max-width:600px;margin:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#edf0f2;padding:16px}summary{cursor:pointer;padding:10px}@media(max-width:650px){.grid{grid-template-columns:1fr}body{padding:12px}table{font-size:11px}}@media print{details{display:block}summary{display:none}h2{break-after:avoid}figure,table{break-inside:avoid}}</style><body>'
        + content
        + "</body></html>"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    request = json.loads(args.input.read_text(encoding="utf-8-sig"))
    data = calculate(request)
    # Serialize everything before touching the output directory: failed calculations leave no partial report.
    json_text = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    html_text = atlas(data)
    p = data["provenance"]
    md = (
        "# Calculation record\n\n"
        + "\n".join("- " + k + ": " + str(v) for k, v in p.items())
        + "\n\n## Checks\n\n"
        + json.dumps(data["internal_checks"])
        + "\n\n## Warnings\n\n"
        + "\n".join("- " + x for x in data["warnings"])
        + "\n\nSee chart.json for the full tables and charts.html for diagrams. Interpretation must be written separately in reading.md.\n"
    )
    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in [
        ("chart.json", json_text),
        ("charts.html", html_text),
        ("calculation.md", md),
    ]:
        target = args.out / name
        if target.exists():
            raise ValueError(
                f"Refusing to overwrite existing report: {target}; choose a new output directory"
            )
    for name, content in [
        ("chart.json", json_text),
        ("charts.html", html_text),
        ("calculation.md", md),
    ]:
        (args.out / name).write_text(content, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "computed",
                "out": str(args.out.resolve()),
                "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
                "checks": data["internal_checks"],
            },
            ensure_ascii=False,
        )
    )


def cli():
    """Return a process exit code for script and installed-command use."""
    try:
        main()
        return 0
    except (ValueError, TypeError, OverflowError, KeyError, OSError, swe.Error) as exc:
        print(
            json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr
        )
        return 2


if __name__ == "__main__":
    sys.exit(cli())
