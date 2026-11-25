#!/usr/bin/env python3
"""Deterministic Ashtakoota / 36-Guna Milan + modern 0-100 synastry.

Rules: Muhurta Chintamani Vivaha Prakarana 21-34 as summarised at
sanatanbodh.in/en/kundli/milan (Drik Panchang counting for Vashya/Gana,
Avakahada Yoni table via Maitreya/Saravali matrix). Plain calculation:
Bhakoot/Nadi cancellations are NOT applied; dosha flags are reported.

Inputs are Moon sign (0-11) + degree in sign (0-30) and Moon nakshatra (0-26)
for each person. Person A is scored as groom/boy, person B as bride/girl
because Varna, Vashya and Gana are directional.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Varna rank (higher = higher varna): Brahman 4, Kshatriya 3, Vaishya 2, Shudra 1
# Meena/Vrishchika/Karka Brahman; Mesha/Simha/Dhanu Kshatriya; Vrishabha/Kanya/Makara Vaishya; Mithuna/Tula/Kumbha Shudra
VARNA_RANK = {0:3,1:2,2:1,3:4,4:3,5:2,6:1,7:4,8:3,9:2,10:1,11:4}
SIGNS_LORD = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}

def varna_score(a_sign, b_sign):
    return 1.0 if VARNA_RANK[a_sign] >= VARNA_RANK[b_sign] else 0.0

def _vashya_group(sign_idx, deg):
    # 0=Four-footed,1=Human,2=Water,3=Wild,4=Insect ; Sag/Cap split at 15 deg
    if sign_idx in (0,1): return 0
    if sign_idx in (2,5,6,10): return 1
    if sign_idx == 3: return 2
    if sign_idx == 4: return 3
    if sign_idx == 7: return 4
    if sign_idx == 8: return 1 if deg < 15 else 0
    if sign_idx == 9: return 0 if deg < 15 else 2
    if sign_idx == 11: return 2
    raise ValueError(sign_idx)

VASHYA = [[2,1,1,1.5,1],[1,2,0.5,0,1],[1,0.5,2,1,1],[0,0,0,2,0],[1,1,1,0,2]]
def vashya_score(a_sign, a_deg, b_sign, b_deg):
    return VASHYA[_vashya_group(a_sign, a_deg)][_vashya_group(b_sign, b_deg)]

def tara_score(a_nak, b_nak):
    def auspicious(count):
        r = count % 9
        return r not in (3,5,7)
    c1 = (b_nak - a_nak) % 27 + 1
    c2 = (a_nak - b_nak) % 27 + 1
    return (1.5 if auspicious(c1) else 0.0) + (1.5 if auspicious(c2) else 0.0)

YONI_PER_NAK = [0,1,2,3,3,4,5,2,5,6,6,7,8,9,8,9,10,10,4,11,12,11,13,0,13,7,1]
YONI_NAMES = ["Horse","Elephant","Ram","Serpent","Dog","Cat","Rat","Cow","Buffalo","Tiger","Deer","Monkey","Mongoose","Lion"]
# Saravali/Maitreya matrix (rows bride, cols groom order as in source table)
YONI_MATRIX = [
 [4,2,2,3,2,2,2,1,0,1,3,3,2,1],
 [2,4,3,3,2,2,2,2,3,1,2,3,2,0],
 [2,3,4,2,1,2,1,3,3,1,2,0,3,1],
 [3,3,2,4,2,1,1,1,1,2,2,2,0,2],
 [2,2,1,2,4,2,1,2,2,1,0,2,1,1],
 [2,2,2,1,2,4,0,2,2,1,3,3,2,1],
 [2,2,1,1,1,0,4,2,2,2,2,2,1,2],
 [1,2,3,1,2,2,2,4,3,0,3,2,2,1],
 [0,3,3,1,2,2,2,3,4,1,2,2,2,1],
 [1,1,1,2,1,1,2,0,1,4,1,1,2,1],
 [1,2,2,2,0,3,2,3,2,1,4,2,2,1],
 [3,3,0,2,2,3,2,2,2,1,2,4,3,2],
 [2,2,3,0,1,2,1,2,2,2,2,3,4,2],
 [1,0,1,2,1,1,2,1,2,1,1,2,2,4],
]
def yoni_score(a_nak, b_nak):
    return float(YONI_MATRIX[YONI_PER_NAK[a_nak]][YONI_PER_NAK[b_nak]])

FRIEND = {"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},"Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},"Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},"Saturn":{"Mercury","Venus"}}
NEUTRAL = {"Sun":{"Mercury"},"Moon":{"Mars","Jupiter","Venus","Saturn"},"Mars":{"Venus","Saturn"},"Mercury":{"Mars","Jupiter","Saturn"},"Jupiter":{"Saturn"},"Venus":{"Mars","Jupiter"},"Saturn":{"Jupiter"}}
def _rel(a,b):
    if a==b: return "same"
    if b in FRIEND.get(a,()): return "friend"
    if b in NEUTRAL.get(a,()): return "neutral"
    return "enemy"
def graha_maitri_score(a_sign, b_sign):
    la, lb = SIGNS_LORD[a_sign], SIGNS_LORD[b_sign]
    if la==lb: return 5.0
    ra, rb = _rel(la,lb), _rel(lb,la)
    # mutual friends?
    if ra=="friend" and rb=="friend": return 5.0
    pair = tuple(sorted([ra,rb]))
    if set([ra,rb])=={"friend","neutral"}: return 4.0
    if pair==("neutral","neutral"): return 3.0
    if set([ra,rb])=={"friend","enemy"}: return 1.0
    if set([ra,rb])=={"neutral","enemy"}: return 0.5
    if pair==("enemy","enemy"): return 0.0
    return 0.0

GANA_PER_NAK = ["Deva","Manushya","Rakshasa","Manushya","Deva","Manushya","Deva","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Deva","Rakshasa","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva","Rakshasa","Rakshasa","Manushya","Manushya","Deva"]
GANA = {("Deva","Deva"):6,("Deva","Manushya"):6,("Deva","Rakshasa"):0,
        ("Manushya","Deva"):5,("Manushya","Manushya"):6,("Manushya","Rakshasa"):0,
        ("Rakshasa","Deva"):1,("Rakshasa","Manushya"):0,("Rakshasa","Rakshasa"):6}
def gana_score(a_nak, b_nak):
    return float(GANA[(GANA_PER_NAK[a_nak], GANA_PER_NAK[b_nak])])

def bhakoot_score(a_sign, b_sign):
    d = (b_sign - a_sign) % 12 + 1
    pair = tuple(sorted([d, 13-d]))  # 2-12,5-9,6-8 are symmetric complements
    # distance pair as (d, other): check set
    if {d, (a_sign-b_sign)%12+1} in [{2,12},{5,9},{6,8},{12,2},{9,5},{8,6}]:
        pass
    # Simpler: compute both directions
    d1 = (b_sign - a_sign) %12 + 1
    d2 = (a_sign - b_sign) %12 + 1
    if {d1,d2} in ({2,12},{5,9},{6,8}):
        return 0.0
    return 7.0

NADI_PER_NAK = ["Aadi","Madhya","Antya","Antya","Madhya","Aadi","Aadi","Madhya","Antya","Antya","Madhya","Aadi","Aadi","Madhya","Antya","Antya","Madhya","Aadi","Aadi","Madhya","Antya","Antya","Madhya","Aadi","Aadi","Madhya","Antya"]
def nadi_score(a_nak, b_nak):
    return 8.0 if NADI_PER_NAK[a_nak] != NADI_PER_NAK[b_nak] else 0.0

def evaluate_dosha_cancellations(person_a, person_b, koota_scores):
    """Classical Dosha Parihara (cancellation) flags. Inputs use moon_sign/moon_nak/moon_pada/mars houses if present."""
    same_rashi = person_a.get("moon_sign") == person_b.get("moon_sign")
    same_nak = person_a.get("moon_nak") == person_b.get("moon_nak")
    diff_pada = person_a.get("moon_pada") != person_b.get("moon_pada")
    # sign lords via SIGNS_LORD in guna_milan
    try:
        from guna_milan import SIGNS_LORD
        same_lord = SIGNS_LORD.get(person_a.get("moon_sign")) == SIGNS_LORD.get(person_b.get("moon_sign"))
    except Exception:
        same_lord = same_rashi
    nadi_raw = koota_scores.get("Nadi", 8) == 0.0
    nadi_cancelled = nadi_raw and ((same_rashi and not same_nak) or (same_nak and not same_rashi) or (same_nak and diff_pada))
    bhakoot_raw = koota_scores.get("Bhakoot", 7) == 0.0
    bhakoot_cancelled = bhakoot_raw and (same_lord or koota_scores.get("Graha Maitri", 0) >= 4.0)
    mang_houses = {1,2,4,7,8,12}
    a_m = person_a.get("mars_house_lagna") in mang_houses or person_a.get("mars_house_moon") in mang_houses
    b_m = person_b.get("mars_house_lagna") in mang_houses or person_b.get("mars_house_moon") in mang_houses
    mang_cancelled = (a_m and b_m) if (a_m or b_m) else True
    eff = sum(koota_scores.values()) + (8.0 if nadi_cancelled else 0) + (7.0 if bhakoot_cancelled else 0)
    return {"raw_score": sum(koota_scores.values()), "effective_score_after_parihara": min(36.0, eff),
            "max_score": 36.0,
            "nadi_dosha": {"present": nadi_raw, "cancelled": nadi_cancelled},
            "bhakoot_dosha": {"present": bhakoot_raw, "cancelled": bhakoot_cancelled},
            "mangalik_dosha": {"person_a": a_m, "person_b": b_m, "cancelled": mang_cancelled}}

def guna_milan(a, b):
    """a,b = dicts with moon_sign, moon_deg, moon_nak (0-26)"""
    breakdown = {
        "Varna": varna_score(a["moon_sign"], b["moon_sign"]),
        "Vashya": vashya_score(a["moon_sign"], a.get("moon_deg",0), b["moon_sign"], b.get("moon_deg",0)),
        "Tara": tara_score(a["moon_nak"], b["moon_nak"]),
        "Yoni": yoni_score(a["moon_nak"], b["moon_nak"]),
        "Graha Maitri": graha_maitri_score(a["moon_sign"], b["moon_sign"]),
        "Gana": gana_score(a["moon_nak"], b["moon_nak"]),
        "Bhakoot": bhakoot_score(a["moon_sign"], b["moon_sign"]),
        "Nadi": nadi_score(a["moon_nak"], b["moon_nak"]),
    }
    total = sum(breakdown.values())
    doshas = []
    if breakdown["Nadi"] == 0:
        doshas.append("Nadi Dosha (same nadi)")
    if breakdown["Bhakoot"] == 0:
        doshas.append("Bhakoot Dosha (2-12 / 5-9 / 6-8)")
    return {
        "breakdown": breakdown,
        "total": total,
        "max": 36.0,
        "doshas": doshas,
        "modern_synastry_100": round(total / 36 * 100, 1),
        "band": "excellent" if total >= 25 else "good" if total >= 18 else "below-minimum",
        "notes": "Plain Ashtakoota count (Muhurta Chintamani). Bhakoot/Nadi cancellations not applied. Traditional count, not a prediction.",
    }


# Classical South Indian Dasa Porutham (10 checks). The ordering below is
# bride then groom, unlike the existing Ashtakoota API (groom then bride).
RAJJU_GROUPS = {
    "Pada": {0, 8, 9, 17, 18, 26},
    "Kati": {1, 7, 10, 16, 19, 25},
    "Nabhi": {2, 6, 11, 15, 20, 24},
    "Kantha": {3, 5, 12, 14, 21, 23},
    "Siro": {4, 13, 22},
}
RAJJU_FOR_NAK = {nak: group for group, nakshatras in RAJJU_GROUPS.items() for nak in nakshatras}
VEDHA_PAIRS = {
    frozenset(pair)
    for pair in (
        (0, 17), (1, 16), (2, 15), (3, 14), (5, 21), (6, 20), (7, 19),
        (8, 18), (9, 26), (10, 25), (11, 24), (12, 23),
    )
}
VEDHA_TRIPLE = {4, 13, 22}
VASHYA_SIGNS = {
    0: {4, 7}, 1: {3, 6}, 2: {5}, 3: {7, 8}, 4: {6}, 5: {2, 11},
    6: {9}, 7: {9}, 8: {3, 5}, 9: {11}, 10: {0}, 11: {9},
}
YONI_BY_NAK = [
    "horse", "elephant", "sheep", "serpent", "serpent", "dog", "cat", "ram", "cat",
    "rat", "bandicoot", "bull", "buffalo", "tiger", "buffalo", "tiger", "doe", "stag",
    "dog", "monkey", "cow", "monkey", "human", "horse", "human", "cow", "elephant",
]
YONI_HOSTILE = {"rat", "dog", "serpent", "cat", "tiger"}
YONI_FRIENDLY = {"deer", "sheep", "horse", "dog", "human", "cat", "elephant", "cow"}
_CLASSICAL_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"}, "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
_CLASSICAL_NEUTRALS = {
    "Sun": {"Mercury"}, "Moon": {"Mars", "Jupiter", "Venus", "Saturn"},
    "Mars": {"Venus", "Saturn"}, "Mercury": {"Mars", "Jupiter", "Saturn"},
    "Jupiter": {"Saturn"}, "Venus": {"Mars", "Jupiter"}, "Saturn": {"Jupiter"},
}


def _porutham(status, value, evidence):
    return {"status": status, "value": value, "evidence": evidence}


def dasa_porutham(girl, boy):
    """Calculate the ten classical star/sign checks using the documented Tamil convention."""
    g_nak, b_nak = girl["moon_nak"], boy["moon_nak"]
    g_sign, b_sign = girl["moon_sign"], boy["moon_sign"]
    if not (0 <= g_nak < 27 and 0 <= b_nak < 27 and 0 <= g_sign < 12 and 0 <= b_sign < 12):
        raise ValueError("moon_nak must be 0–26 and moon_sign must be 0–11")

    star_count = (b_nak - g_nak) % 27 + 1
    dina_ok = (
        star_count in {2, 4, 6, 8, 9}
        or 10 <= star_count <= 18 and star_count != 17
        or 19 <= star_count <= 27 and star_count not in {24, 27}
    )
    mahendra_ok = star_count in {4, 7, 10, 13, 16, 19, 22, 25}
    yoni_g, yoni_b = YONI_BY_NAK[g_nak], YONI_BY_NAK[b_nak]
    if yoni_g == yoni_b or "monkey" in (yoni_g, yoni_b) or {yoni_g, yoni_b} <= YONI_FRIENDLY:
        yoni_status = "favorable"
    elif yoni_g in YONI_HOSTILE and yoni_b in YONI_HOSTILE:
        yoni_status = "unfavorable"
    else:
        yoni_status = "partial"

    gana_g, gana_b = GANA_PER_NAK[g_nak], GANA_PER_NAK[b_nak]
    if gana_g == gana_b or (gana_g, gana_b) == ("Manushya", "Deva"):
        gana_status = "favorable"
    elif (gana_g, gana_b) == ("Deva", "Manushya"):
        gana_status = "partial"
    else:
        gana_status = "unfavorable"
    sign_count = (b_sign - g_sign) % 12 + 1
    if sign_count == 1 or sign_count >= 7:
        rasi_status = "favorable"
    elif sign_count in {2, 5, 6}:
        rasi_status = "unfavorable"
    else:
        rasi_status = "partial"

    girl_lord, boy_lord = SIGNS_LORD[g_sign], SIGNS_LORD[b_sign]
    if girl_lord == boy_lord:
        lord_status = "favorable"
        lord_relation = "same sign lord"
    else:
        g_to_b = "friend" if boy_lord in _CLASSICAL_FRIENDS[girl_lord] else (
            "neutral" if boy_lord in _CLASSICAL_NEUTRALS[girl_lord] else "enemy"
        )
        b_to_g = "friend" if girl_lord in _CLASSICAL_FRIENDS[boy_lord] else (
            "neutral" if girl_lord in _CLASSICAL_NEUTRALS[boy_lord] else "enemy"
        )
        lord_relation = f"girl-to-boy {g_to_b}; boy-to-girl {b_to_g}"
        lord_status = "unfavorable" if "enemy" in (g_to_b, b_to_g) else (
            "favorable" if g_to_b == b_to_g == "friend" else "partial"
        )

    girl_controls = b_sign in VASHYA_SIGNS[g_sign]
    boy_controls = g_sign in VASHYA_SIGNS[b_sign]
    vashya_status = "favorable" if girl_controls and not boy_controls else (
        "partial" if girl_controls or boy_controls else "unfavorable"
    )

    vedha = frozenset((g_nak, b_nak)) in VEDHA_PAIRS or (
        g_nak != b_nak and g_nak in VEDHA_TRIPLE and b_nak in VEDHA_TRIPLE
    )
    checks = {
        "Dina": _porutham(
            "favorable" if dina_ok else "unfavorable", star_count,
            f"Count girl-to-boy is {star_count}; favorable counts follow Vidhānamālai's three nine-star sections.",
        ),
        "Gana": _porutham(gana_status, f"girl={gana_g}, boy={gana_b}", "Birth-star gana comparison."),
        "Mahendra": _porutham(
            "favorable" if mahendra_ok else "unfavorable", star_count,
            "Favorable girl-to-boy counts: 4, 7, 10, 13, 16, 19, 22, 25.",
        ),
        "Stree Deergha": _porutham(
            "favorable" if star_count > 13 else "unfavorable", star_count,
            "The selected rule requires a girl-to-boy count greater than 13.",
        ),
        "Yoni": _porutham(yoni_status, f"girl={yoni_g}, boy={yoni_b}", "Vidhānamālai animal-symbol convention."),
        "Rasi": _porutham(
            rasi_status, sign_count,
            "Count girl-to-boy; same sign or 7–12 is favorable, 2/5/6 unfavorable, 3/4 partial in this implementation.",
        ),
        "Rasyadhipathi": _porutham(lord_status, f"{girl_lord}/{boy_lord}", lord_relation),
        "Vasya": _porutham(
            vashya_status, f"girl-controls={girl_controls}, boy-controls={boy_controls}",
            "Directional Moon-sign attraction table; girl's sign attracting the boy's is favorable, reverse-only is partial.",
        ),
        "Rajju": _porutham(
            "unfavorable" if RAJJU_FOR_NAK[g_nak] == RAJJU_FOR_NAK[b_nak] else "favorable",
            f"girl={RAJJU_FOR_NAK[g_nak]}, boy={RAJJU_FOR_NAK[b_nak]}",
            "Birth stars in the same Rajju group do not agree.",
        ),
        "Vedha": _porutham(
            "unfavorable" if vedha else "favorable", vedha,
            "Checks the selected Vidhānamālai/Kalaprakasika mutually obstructing star pairs.",
        ),
    }
    counts = {status: sum(check["status"] == status for check in checks.values())
              for status in ("favorable", "partial", "unfavorable")}
    return {
        "checks": checks,
        "counts": counts,
        "max_checks": 10,
        "convention": "Tamil Dasa Porutham; bride-to-groom counting; no dosha cancellation applied.",
        "notes": (
            "Classical compatibility tradition, not a relationship verdict. Regional rule lists "
            "and exceptions vary; this reports raw checks and does not recommend whether to marry."
        ),
    }
def from_chart(chart):
    j = chart["jyotisha"]
    moon = j["planets"]["Moon"]
    return {"moon_sign": moon["sign_index"], "moon_deg": moon["degree_in_sign"], "moon_nak": j["moon_nakshatra"]["index"]}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart-a", required=True)
    ap.add_argument("--chart-b", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--method", choices=["ashtakoota", "porutham10", "both"], default="ashtakoota")
    a = ap.parse_args()
    ca = json.loads(Path(a.chart_a).read_text(encoding="utf-8"))
    cb = json.loads(Path(a.chart_b).read_text(encoding="utf-8"))
    person_a, person_b = from_chart(ca), from_chart(cb)
    if a.method == "ashtakoota":
        result = guna_milan(person_a, person_b)
    elif a.method == "porutham10":
        result = dasa_porutham(person_b, person_a)
    else:
        result = {
            "ashtakoota": guna_milan(person_a, person_b),
            "dasa_porutham": dasa_porutham(person_b, person_a),
        }
    ashtakoota_result = result if a.method == "ashtakoota" else result.get("ashtakoota")
    try:
        pa, pb = person_a.copy(), person_b.copy()
        for _c, _p in ((ca, pa), (cb, pb)):
            _mars = _c["jyotisha"]["planets"]["Mars"]["house"]
            _p["mars_house_lagna"] = _mars; _p["mars_house_moon"] = _mars
        if ashtakoota_result is not None:
            ashtakoota_result["dosha_parihara"] = evaluate_dosha_cancellations(
                pa, pb, ashtakoota_result["breakdown"]
            )
    except Exception as e:
        result["dosha_parihara_error"] = str(e)
    txt = json.dumps(result, indent=2)
    if a.out:
        Path(a.out).write_text(txt, encoding="utf-8")
        print(f"written: {a.out}")
    print(txt)
