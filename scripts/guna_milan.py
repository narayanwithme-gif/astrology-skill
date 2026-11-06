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
    if breakdown["Nadi"] == 0: doshas.append("Nadi Dosha (same nadi)")
    if breakdown["Bhakoot"] == 0: doshas.append("Bhakoot Dosha (2-12 / 5-9 / 6-8)")
    return {
        "breakdown": breakdown,
        "total": total, "max": 36.0,
        "doshas": doshas,
        "modern_synastry_100": round(total/36*100, 1),
        "band": "excellent" if total>=25 else "good" if total>=18 else "below-minimum",
        "notes": "Plain Ashtakoota count (Muhurta Chintamani). Bhakoot/Nadi cancellations not applied. Traditional count, not a prediction.",
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
    a = ap.parse_args()
    ca = json.loads(Path(a.chart_a).read_text(encoding="utf-8"))
    cb = json.loads(Path(a.chart_b).read_text(encoding="utf-8"))
    result = guna_milan(from_chart(ca), from_chart(cb))
    txt = json.dumps(result, indent=2)
    if a.out:
        Path(a.out).write_text(txt, encoding="utf-8")
        print(f"written: {a.out}")
    print(txt)
