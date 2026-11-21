# SPDX-License-Identifier: AGPL-3.0-or-later
"""Optional advanced calculations requested through the main chart workflow."""

from datetime import datetime

from ashtakavarga import calculate_ashtakavarga
from composite_charts import composite_report, davison_chart
from engine_utils import number
from kp_system import calculate_jaimini, calculate_kp
from progressions import lunar_return, secondary_progressions, solar_return
from relocation import relocation_chart
from shadbala import calculate_shadbala


def calculate_advanced(options, data, birth, as_of, lat, lon, settings):
    from chart_engine import jd_at, make_chart, parse_birth

    if not isinstance(options, dict):
        raise ValueError("advanced must be an object")
    supported = {"composite", "progressions", "relocation", "solar_return", "lunar_return", "vedic"}
    if unknown := options.keys() - supported:
        raise ValueError(f"Unknown advanced options: {', '.join(sorted(unknown))}")

    result = {}
    if "composite" in options:
        second = options["composite"]
        other_birth = parse_birth(second)
        other_lat, other_lon = _coordinates(second)
        other_chart = make_chart(jd_at(other_birth), other_lat, other_lon, settings, False)
        relationship = composite_report(data["western"], other_chart, lat, lon, settings)
        location = options["composite"].get("davison_location")
        if location is not None:
            davison_lat, davison_lon = _coordinates(location)
            relationship["davison"] = davison_chart(
                birth,
                other_birth,
                davison_lat,
                davison_lon,
                settings,
            )
        result["composite"] = relationship

    if "progressions" in options:
        if type(options["progressions"]) is not bool:
            raise ValueError("advanced.progressions must be true or false")
        if options["progressions"]:
            if not data["input"].get("as_of"):
                raise ValueError("Secondary progressions require an explicit as_of timestamp")
            if as_of < birth:
                raise ValueError("Progression target must be at or after birth")
            result["progressions"] = secondary_progressions(birth, as_of, lat, lon, settings)

    if "relocation" in options:
        new_lat, new_lon = _coordinates(options["relocation"])
        result["relocation"] = relocation_chart(data, new_lat, new_lon, settings)

    if "solar_return" in options:
        year = options["solar_return"]
        if type(year) is not int or not 1800 <= year <= 2399:
            raise ValueError("advanced.solar_return must be a Gregorian year 1800–2399")
        result["solar_return"] = solar_return(birth, year, lat, lon, settings)

    if "lunar_return" in options:
        target = datetime.fromisoformat(options["lunar_return"])
        if target.utcoffset() is None or not 1800 <= target.year <= 2399:
            raise ValueError(
                "advanced.lunar_return requires an offset-aware timestamp in 1800–2399"
            )
        result["lunar_return"] = lunar_return(birth, target, lat, lon, settings)

    systems = options.get("vedic", [])
    if not isinstance(systems, list) or any(
        system not in ("shadbala", "ashtakavarga", "kp", "jaimini") for system in systems
    ):
        raise ValueError("advanced.vedic must list shadbala, ashtakavarga, kp, or jaimini")
    if systems:
        vedic = data["jyotisha"]
        calculations = {
            "shadbala": lambda: calculate_shadbala(vedic, birth.hour + birth.minute / 60),
            "ashtakavarga": lambda: calculate_ashtakavarga(vedic),
            "kp": lambda: calculate_kp(
                make_chart(
                    jd_at(birth),
                    lat,
                    lon,
                    {**settings, "ayanamsha": "krishnamurti"},
                    True,
                    house_system="P",
                ),
                birth,
            ),
            "jaimini": lambda: calculate_jaimini(vedic),
        }
        result["vedic"] = {system: calculations[system]() for system in dict.fromkeys(systems)}
    return result


def _coordinates(location):
    return (
        number(location["latitude"], "latitude", -89.9, 89.9),
        number(location["longitude"], "longitude", -180, 180),
    )
