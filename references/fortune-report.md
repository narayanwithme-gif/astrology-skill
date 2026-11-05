# Fortune Report mode

A presentation format layered on top of the standard complete reading. The user
asks for a "Fortune Report" / "fortune report like [sample PDF]" with a branded
cover, Index, Lucky Things, numerology, Lo Shu Grid, career, month-wise themes,
and a Life-Path appendix. The calculations (chart.json) are the same as the
standard mode; this mode only changes presentation and adds numerology derived
from the given birth date and name.

## Rules (non-negotiable)

1. **Never copy sample-report data.** The sample PDF (e.g. Narayan Prajapati
   01/12/1990) is a style reference only. Every number, date, colour and claim
   must be derived from the user's own input. If a value cannot be derived,
   mark it as not assessed rather than inventing it.
2. **Numerology from the given DOB and name only.** Use the formulas below.
   Do not use a second person's numbers as placeholders.
3. **No remedies, gems, rudraksh, fasting or donations prescribed**, especially
   for minors. Traditional correspondences may be listed "for completeness of
   the requested format only" with an explicit safety note. Any health,
   education or finance decision must defer to a qualified professional.
4. **No health or finance prediction.** Wellness and finance sections are
   pattern/practical-inference only, with the boundary stated.
5. **Birth-time caveat.** Approximate times (±30 min or more) must carry the
   uncertainty note, including any Lagna/bhava shift at the endpoints (see
   chart.json `uncertainty`).
6. **Branding.** Cover shows the user's chosen author/brand name (default:
   the user's service name). Do not put a third party's name/website on the
   cover unless the user supplies it.
7. **Truthful numerators.** If a numerology convention varies (e.g. Bhagyank
   9 vs 6 by addition method), show both and state which the report uses.

## Numerology formulas (from DOB + name)

- **Mulank (Psychic Number):** reduce the birth day (DD) to a single digit
  (26 → 8). Ruling planet: 1 Sun, 2 Moon, 3 Jupiter, 4 Rahu, 5 Mercury,
  6 Venus, 7 Ketu, 8 Saturn, 9 Mars.
- **Bhagyank (Destiny Number):** sum all digits of DD/MM/YYYY, reduce
  (e.g. 10/10/2026 → 12 → 3). Ruling planet as above.
- **Name Number:** Pythagorean letter values (A=1…Z=26, reduce per letter)
  summed and reduced. Show the raw sum and reduction. Chaldean may be shown
  as an alternative.
- **Soul Urge:** vowels only, reduced. **Personality:** consonants only, reduced.
- **Kua Number (Feng Shui):** year digits sum → reduce to s; step = 4 if male/5
  if female (Feng Shui convention: s>9 → s−9 after adding); Kua = 10 − step,
  adjusted: male 5→5, female 5→8 (state the method used). Directions follow
  the Kua table in the generator.
- **Lo Shu Grid:** place the non-zero digits of DD/MM/YYYY in the 3×3 magic
  square (4-9-2 / 3-5-7 / 8-1-6 positions). Count occurrences (e.g. "66").
  Missing numbers are the digits 1–9 absent from the grid.

## Report structure (16 sections + appendix)

Cover (purple, gold border, ॥ ॐ श्री गणेशाय नमः ॥, YOUR FORTUNE REPORT,
BY [brand], name pill) → Disclaimer → Message from Author → Best Way to
Study → Index 01–16 → 01 Introduction / Lucky Things table → 02
Numerological Analysis (Mulank, Bhagyank, combination) → 03 Colour and Date
Insights (lucky colours/dates/years, zodiac traits, ruling deity) →
04 Spiritual Elements (tradition only) → 05 Body and Health Insights
(pattern only, no diagnosis) → 06 Career and Professional Insights →
07 Fortune Grid Analysis (grid, element analysis, missing-number
practical equivalents) → 08 Fengshui and Directional Insights (Kua
directions) → 09 Name and Signature Analysis (name number, soul urge,
personality, name grid planes) → 10 Future Fortune Trends (Vimshottari
MD table) → 11 Month-Wise Themes for Next 12 Months (family/practical
themes, not predictions) → 12 Challenge of Life (by dasha) →
13 Are You on the Right Path? → 14 Success Path Analysis →
15–16 Signature Analysis / Understanding Your Nature → Kundali
(Western + Jyotisha tables, D9/D10, uncertainty note) → Life-Path Appendix
(Career, Health, Family, Finance, Luck, Growth, Turning Points table,
one-page choice summary).

## Generator

`scripts/fortune_report.py --chart chart.json --request request.json --name "FULL NAME" --brand "BRAND" --out-dir DIR`

- Derives numerology from request.json (birth date) + --name.
- Reads chart.json for Lagna, nakshatra, D9/D10, dashas, uncertainty.
- Writes `NAME-Fortune-Report.html` and `NAME-Fortune-Report.pdf`
  (purple cover, parchment pages, header/footer with name + brand).
- Requires `reportlab` and `pillow` for the PDF. HTML needs no build.
- Original interpretive text only. Do not copy sample-report prose.

## Deliverables

`request.json` (private), `chart.json`, `charts.html`, `calculation.md`,
`reading.md` (the full 11-section reading), plus the Fortune HTML/PDF.
Do not copy birth data into this reusable skill source.
