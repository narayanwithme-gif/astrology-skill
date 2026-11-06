#!/usr/bin/env python3
"""Minute-sensitivity boundary check (±3 min) for D1/D9/D10 cusps.

Perturbs birth instant and reports whether Lagna / Navamsa / Dasamsa /
Moon nakshatra-pada flip. Uses chart_engine.make_chart directly.
"""
import argparse, importlib.util, json
from datetime import timedelta
from pathlib import Path

def _load_engine(root):
    SPEC = importlib.util.spec_from_file_location("chart_engine", root / "scripts" / "chart_engine.py")
    m = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(m); return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--request", required=True)
    ap.add_argument("--window-minutes", type=int, default=3)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    root = Path(__file__).resolve().parent.parent
    eng = _load_engine(root)
    req = json.loads(Path(a.request).read_text(encoding="utf-8"))
    b = req["birth"]
    local = eng.parse_birth(b)
    import swisseph as swe
    s = {"western_houses": "P", "ayanamsha": "lahiri", "nodes": "mean", "dasha_year_days": 365.25, "aspect_orb_degrees": 6, **req.get("settings", {})}
    if isinstance(s.get("ayanamsha"), str):
        s["ayanamsha"] = s["ayanamsha"].lower()
        if s["ayanamsha"] == "kp": s["ayanamsha"] = "krishnamurti"
    modes = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN, "krishnamurti": swe.SIDM_KRISHNAMURTI, "drik": swe.SIDM_TRUE_CITRA, "kp": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(modes[s["ayanamsha"]])
    lat, lon = b["latitude"], b["longitude"]
    def sig(instant):
        jd = eng.jd_at(instant)
        w, v = [eng.make_chart(jd, lat, lon, s, sid) for sid in (False, True)]
        return {"d1_lagna": v["ascendant"]["sign"], "d9_navamsa": v["D9"]["ascendant"]["sign"],
                "d10_dasamsa": v["D10"]["ascendant"]["sign"],
                "moon_pada": f"{v['moon_nakshatra']['name']}-{v['moon_nakshatra']['pada']}"}
    base = sig(local.astimezone(eng.UTC))
    flips = {k: [] for k in base}
    for delta in range(-a.window_minutes, a.window_minutes + 1):
        if delta == 0: continue
        cur = sig(local.astimezone(eng.UTC) + timedelta(minutes=delta))
        for k in flips:
            if cur[k] != base[k]:
                flips[k].append({"offset_minutes": f"{delta:+d}m", "from": base[k], "to": cur[k]})
    is_sensitive = any(flips.values())
    rec = bool(flips["d1_lagna"] or flips["d9_navamsa"] or flips["d10_dasamsa"])
    out = {"window_minutes": f"+/-{a.window_minutes}m", "is_cusp_sensitive": is_sensitive,
           "recommend_rectification": rec, "baseline": base,
           "boundary_flips": {k: v for k, v in flips.items() if v},
           "agent_directive": ("BORDERLINE CUSP WARNING: do not assert rigid D9/D10 house lordships without rectify_birth_time." if rec else "STABLE across window.")}
    txt = json.dumps(out, indent=2)
    if a.out: Path(a.out).write_text(txt, encoding="utf-8"); print(f"written: {a.out}")
    print(txt)

if __name__ == "__main__":
    main()
