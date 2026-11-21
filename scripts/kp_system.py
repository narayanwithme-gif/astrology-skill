#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""KP longitude subdivisions and seven-karaka Jaimini calculations."""

from engine_utils import LORDS, NAK, SIGNS, YEARS

KP_AYANAMSHA = "krishnamurti"
SIGN_LORD = (
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
)
WEEKDAY_LORD = ("Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun")
NAKSHATRA_SPAN = 360 / 27
KARAKAS = ("AK", "AmK", "BK", "MK", "PK", "GK", "DK")


def subdivision(lon):
    """Return the nesting of Vimshottari-weighted segments at a sidereal longitude."""
    lon %= 360
    nak_index = int(lon / NAKSHATRA_SPAN)
    star_index = nak_index % len(LORDS)
    remainder = lon - nak_index * NAKSHATRA_SPAN
    sub_index, remainder, sub_span = _segment(star_index, remainder, NAKSHATRA_SPAN)
    sub_sub_index, _, _ = _segment(sub_index, remainder, sub_span)
    return {
        "sign": SIGNS[int(lon // 30)],
        "nakshatra": NAK[nak_index],
        "star_lord": LORDS[star_index],
        "sub_lord": LORDS[sub_index],
        "sub_sub_lord": LORDS[sub_sub_index],
        "degree_in_sign": round(lon % 30, 4),
    }


def _segment(first, position, span):
    for offset in range(len(LORDS)):
        index = (first + offset) % len(LORDS)
        width = span * YEARS[LORDS[index]] / 120
        if position < width or offset == len(LORDS) - 1:
            return index, position, width
        position -= width


def kp_star_sub_sub(chart_data, planet_name):
    planet = chart_data["planets"].get(planet_name)
    if planet is None:
        return None
    return {"planet": planet_name, **subdivision(planet["longitude"]), "kp_method": True}


def ruling_planet(chart_data, as_of_dt):
    """Return the Moon and Ascendant sign/star lords and optional local weekday lord."""
    moon = chart_data["planets"]["Moon"]
    asc = chart_data["ascendant"]
    result = {
        "ascendant_sign_lord": SIGN_LORD[asc["sign_index"]],
        "ascendant_star_lord": subdivision(asc["longitude"])["star_lord"],
        "moon_sign_lord": SIGN_LORD[moon["sign_index"]],
        "moon_star_lord": subdivision(moon["longitude"])["star_lord"],
    }
    if as_of_dt is not None:
        result["weekday_lord"] = WEEKDAY_LORD[as_of_dt.weekday()]
    return result


def cuspal_interlink(chart_data, house_num):
    """Identify a Placidus cusp's lords and the natal house of its sub lord."""
    if not 1 <= house_num <= 12:
        raise ValueError("KP cusp number must be 1–12")
    longitude = chart_data["cusps"][house_num - 1]
    lords = subdivision(longitude)
    return {
        "longitude": longitude,
        **lords,
        "sub_lord_natal_house": chart_data["planets"][lords["sub_lord"]]["house"],
    }


def calculate_kp(chart_data, instant=None):
    if (
        chart_data["zodiac"] != "sidereal"
        or chart_data.get("ayanamsha") != KP_AYANAMSHA
        or chart_data["house_method"] != "P"
    ):
        raise ValueError("KP requires sidereal Krishnamurti positions and Placidus cusps")
    return {
        "status": "computed",
        "method": "KP longitude subdivisions with Vimshottari proportions",
        "ayanamsha": KP_AYANAMSHA,
        "star_sub_sub": {p: kp_star_sub_sub(chart_data, p) for p in chart_data["planets"]},
        "ruling_planet": ruling_planet(chart_data, instant),
        "cuspal_interlink": {house: cuspal_interlink(chart_data, house) for house in range(1, 13)},
    }


def jaimini_karakas(chart_data):
    """Rank the seven visible planets by their advancement within their signs."""
    from chart_engine import CLASSICAL

    planets = chart_data["planets"]
    ranked = sorted(CLASSICAL[:7], key=lambda name: planets[name]["longitude"] % 30, reverse=True)
    result = {
        role: {
            "planet": name,
            "sign": planets[name]["sign"],
            "house": planets[name]["house"],
            "longitude": planets[name]["longitude"],
            "degree_in_sign": planets[name]["longitude"] % 30,
        }
        for role, name in zip(KARAKAS, ranked, strict=True)
    }
    return {"status": "computed", "method": "Seven chara karakas", **result}


def jaimini_special_aspects(chart_data):
    """Movable and fixed signs aspect one another except neighbors. Dual signs interaspect."""
    from chart_engine import CLASSICAL

    aspects = []
    lagna = chart_data["ascendant"]["sign_index"]
    for name in CLASSICAL[:7]:
        source = chart_data["planets"][name]["sign_index"]
        for target in range(12):
            offset = (target - source) % 12
            modalities = (source % 3, target % 3)
            if (
                modalities == (2, 2)
                and offset
                or (modalities in ((0, 1), (1, 0)) and offset not in (1, 11))
            ):
                aspects.append(
                    {
                        "graha": name,
                        "aspect_type": "Jaimini_Rashi_Drishti",
                        "target_sign": SIGNS[target],
                        "target_house": (target - lagna) % 12 + 1,
                    }
                )
    return {"status": "computed", "method": "Jaimini Rashi Drishti", "aspects": aspects}


def jaimini_chara_dasha(chart_data, birth_jd, as_of_dt, year_days=365.25):
    """Report the status of this school-dependent calculation."""
    return {
        "status": "unavailable",
        "reason": "Chara Dasha requires a documented school-specific rule set",
    }


def calculate_jaimini(chart_data, birth_jd=None, as_of_dt=None):
    if chart_data["zodiac"] != "sidereal":
        raise ValueError("Jaimini requires a sidereal natal chart")
    return {
        "status": "computed",
        "method": "Jaimini seven-karaka and Rashi Drishti",
        "karakas": jaimini_karakas(chart_data),
        "special_aspects": jaimini_special_aspects(chart_data),
        "chara_dasha": jaimini_chara_dasha(chart_data, birth_jd, as_of_dt),
    }
