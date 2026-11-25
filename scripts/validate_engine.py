#!/usr/bin/env python3
"""Compare Moshier output with another PySwissEph ephemeris mode.

This is a useful mode-agreement check, but it is not an independent engine or
an external known-answer validation: both paths use PySwissEph. Swiss Ephemeris
files may be unavailable, in which case PySwissEph can fall back; returned flags
are included in the report so callers can inspect the mode actually used.
"""

import argparse
import json
from pathlib import Path

import swisseph as swe

AYANAMSHA_MODES = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "drik": swe.SIDM_TRUE_CITRA,
}


def max_drift(chart_path, tol=0.01):
    data = json.loads(Path(chart_path).read_text(encoding="utf-8"))
    prov = data["provenance"]
    jd = prov["julian_day_ut"]
    ayanamsha = prov.get("settings", {}).get("ayanamsha", "lahiri").lower()
    if ayanamsha == "kp":
        ayanamsha = "krishnamurti"
    if ayanamsha not in AYANAMSHA_MODES:
        raise ValueError(f"Unsupported ayanamsha in chart provenance: {ayanamsha}")
    swe.set_sid_mode(AYANAMSHA_MODES[ayanamsha])
    deltas = {}
    for western in (True, False):
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | (swe.FLG_SIDEREAL if not western else 0)
        # NOTE: FLG_SWIEPH requests Swiss/JPL file ephemeris; if files are
        # absent the library falls back and we record the returned flag.
        bodies = [
            ("Sun", swe.SUN),
            ("Moon", swe.MOON),
            ("Mercury", swe.MERCURY),
            ("Venus", swe.VENUS),
            ("Mars", swe.MARS),
            ("Jupiter", swe.JUPITER),
            ("Saturn", swe.SATURN),
        ]
        src = data["western"] if western else data["jyotisha"]
        for name, body in bodies:
            x, ret = swe.calc_ut(jd, body, flags)
            ref = src["planets"][name]["longitude"]
            d = abs((x[0] - ref + 180) % 360 - 180)
            key = f"{'tropical' if western else 'sidereal'}:{name}"
            deltas[key] = {"delta_deg": round(d, 6), "returned_flags": ret}
            if d > tol:
                print(f"FAIL {key} delta={d:.6f} > {tol}")
    worst = max(v["delta_deg"] for v in deltas.values())
    print(
        json.dumps(
            {
                "comparison": "Moshier vs PySwissEph Swiss-file request; same library, not independent",
                "sidereal_mode": ayanamsha,
                "tolerance_deg": tol,
                "worst_delta_deg": worst,
                "deltas": deltas,
            },
            indent=2,
        )
    )
    return worst <= tol


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--tol", type=float, default=0.01)
    a = ap.parse_args()
    ok = max_drift(a.chart, a.tol)
    raise SystemExit(0 if ok else 1)
