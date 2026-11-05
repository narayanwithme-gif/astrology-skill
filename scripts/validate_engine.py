#!/usr/bin/env python3
"""Independent validation harness: compare chart_engine vs direct PySwissEph (JPL).

Uses Moshier (engine default) vs Swiss/JPL file ephemeris where available.
Publishes drift deltas; fails if any body exceeds tolerance (default 0.01 deg).
This is a second implementation path, not a second call to the same helper.
"""
import argparse, json
from pathlib import Path

def max_drift(chart_path, tol=0.01):
    import swisseph as swe
    data = json.loads(Path(chart_path).read_text(encoding="utf-8"))
    prov = data["provenance"]
    jd = prov["julian_day_ut"]
    # The engine sets a process-global sidereal mode (Lahiri by default).
    # This check must use the same mode as the chart, or every sidereal body
    # will be offset by the ayanamsha difference.
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    deltas = {}
    for western in (True, False):
        flags = swe.FLG_SWIEPH | swe.FLG_SPEED | (swe.FLG_SIDEREAL if not western else 0)
        # NOTE: FLG_SWIEPH requests Swiss/JPL file ephemeris; if files are
        # absent the library falls back and we record the returned flag.
        bodies = [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
                  ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
                  ("Saturn", swe.SATURN)]
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
    print(json.dumps({"tolerance_deg": tol, "worst_delta_deg": worst, "deltas": deltas}, indent=2))
    return worst <= tol

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--tol", type=float, default=0.01)
    a = ap.parse_args()
    ok = max_drift(a.chart, a.tol)
    raise SystemExit(0 if ok else 1)
