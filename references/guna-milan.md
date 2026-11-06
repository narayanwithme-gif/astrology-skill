# Guna Milan (Ashtakoota 36)

Deterministic 8-Koota scoring in `scripts/guna_milan.py`. Person A = groom/boy, B = bride/girl (Varna/Vashya/Gana are directional).

| Koota | Max | From |
|---|---|---|
| Varna | 1 | Moon sign varna rank |
| Vashya | 2 | Moon sign vashya group (Sag/Cap split at 15°) |
| Tara | 3 | Nakshatra count both ways (remainder 3/5/7 inauspicious) |
| Yoni | 4 | Nakshatra yoni (Saravali/Maitreya matrix) |
| Graha Maitri | 5 | Sign lords friendship |
| Gana | 6 | Deva/Manushya/Rakshasa (Drik counting) |
| Bhakoot | 7 | Moon-sign distance (2-12/5-9/6-8 = 0) |
| Nadi | 8 | Aadi/Madhya/Antya (different = 8) |
| **Total** | **36** | Bands: >=25 excellent, >=18 good, <18 below-minimum |

Plain count: Bhakoot/Nadi cancellations NOT applied; dosha flags reported.
Modern synastry (0-100) = total/36*100, shown alongside the traditional score.
CLI: `python scripts/guna_milan.py --chart-a chartA.json --chart-b chartB.json`
