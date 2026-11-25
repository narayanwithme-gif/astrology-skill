# Conventions review (practitioner sign-off)

This doc records where the engine's conventions diverge from other schools,
so practitioners can see the choices. No single school is presented as
universal.

## Chosen defaults
- Western: tropical, Placidus (P), ecliptic-longitude house membership.
- Jyotisha: Lahiri ayanamsha, whole-sign Rashi houses, mean nodes.
- Dasha year: 365.25 days. Aspect orb: 6° (software convention).
- D9/D10: Parashari rules (see references/calculation.md).

## Known divergences to review
- House membership by ecliptic longitude vs bhava-chalit / Sripati.
- Mean vs true nodes (engine default: mean).
- 365.25-day year vs 360-day or calendar-year dasha boundaries.
- Whole-sign vs Placidus for Western houses.

## Review log
| Date | Reviewer | Tradition | Status |
|---|---|---|---|
| — | pending | Jyotisha | awaiting practitioner review |
| — | pending | Western | awaiting practitioner review |
| — | pending | Festival and vrata dates | PyJHora 5.0.6 adapter; region-specific sign-off still required |
| — | pending | Indian-language labels | Source data available in six festival languages; independent native-speaker review pending |

Record agreements and disagreements here; do not silently change conventions.
