---
name: astrology-structured
description: Calculate, display and interpret Western and Vedic astrology charts with explicit settings, sources and uncertainty. Use for natal readings, kundli, Jyotisha, career, relationships, dashas, transits, chart comparison and astrology lessons.
license: AGPL-3.0-or-later
metadata:
  version: "1.2.0"
---

# Structured Western and Vedic astrology

Produce reproducible chart data before interpretation. Keep Western and Jyotisha rules distinct. Use free local tools and legally available sources; do not activate paid services or subscriptions. Match the requested detail and format.

## Choose the mode

- **Complete reading:** intake → calculation → validation → diagrams/tables → both traditions → topic synthesis → timing → sources and limitations → saved files.
- **Focused question:** calculate or reuse a matching verified chart, read the requested topic in `references/interpretation.md`, and explain only the relevant factors.
- **Compare people:** calculate separately with identical settings within each tradition, then use the compatibility procedure in `references/interpretation.md`.
- **Lesson:** read `references/learning.md`. Teach one lesson at a time; a lesson needs no birth data unless practicing a chart.
- **Fortune Report:** read `references/fortune-report.md`. The user asks for a branded "Fortune Report" like a sample PDF (purple cover, Index 01–16, Lucky Things, Mulank/Bhagyank, Lo Shu Grid, career, month-wise, Life-Path). Calculate with `chart_engine.py` as usual, derive numerology from the user's own DOB + name (never copy sample-report data), then build HTML + PDF with `scripts/fortune_report.py` and write the full interpretation prose following the Fortune template in `references/fortune-report.md`. No remedies/gems prescribed, especially for minors; no health/finance prediction; approximate birth times carry the uncertainty caveat.
- **Existing chart:** transcribe placements and settings, flag unreadable or missing details, and distinguish supplied data from independently computed data.
- **Electional, horary, mundane, rectification, specialized vargas:** use the advanced-mode procedure in `references/interpretation.md`. These require extra rules and calculations; do not pretend natal output implements them.

Natural-language astrology questions should select this skill without requiring a slash command. Discovery is advisory: if Hermes does not load it, the user can explicitly say “Use astrology-structured”. Do not install background hooks or autonomous forecasts.

## 1. Intake and data quality

Reuse confirmed information from the current conversation or an explicitly saved local profile. Do not ask again for established facts. Ask in one concise batch for missing date (ISO YYYY-MM-DD or clarify ambiguous day/month), local time, time source/uncertainty, birthplace, desired traditions/topics and forecast interval. Confirm ambiguous places and obtain coordinates from a cited gazetteer; do not guess a similarly named town.

Record coordinate source and whether village centroid or exact coordinates. Use an IANA timezone and historical DST rules, not a present-day offset applied to every date. Resolve DST folds/gaps. A recorded precise time is a reported precision, not proof of clock accuracy. No birth time: omit Ascendant, houses, varga Lagna and precise dasha boundaries; explain what remains interpretable. Never use noon as though it were the actual birth time.

Defaults, disclosed before interpretation: Western tropical + Placidus; Jyotisha sidereal Lahiri + whole-sign Rashi houses; mean nodes; Parashari graha drishti; Vimshottari 365.25-day year. Allow requested alternatives. Grahas traditionally include Sun through Saturn plus Rahu/Ketu; outer planets are supplementary modern material. A Western house method and Jyotisha bhava-chalit are not interchangeable.

## 2. Calculate

Read `references/calculation.md` and use `scripts/chart_engine.py`. Build a private request JSON using `assets/request.example.json`; the example uses fictional birth data. Resolve paths relative to this SKILL.md.

Use the skill-local `.venv` created by `scripts/setup.ps1` (Windows) or `scripts/setup.sh` (Linux/macOS). Resolve the interpreter and script paths from this skill's directory, not the current working directory. If that environment is absent, ask Hermes to run the appropriate setup script or use an existing compatible environment with `requirements.txt` installed.

```sh
python scripts/chart_engine.py --input /absolute/path/request.json --out /absolute/path/report-directory
```

Replace `python` with the environment's interpreter. Never install dependencies into a global Python environment by default.

The helper generates `chart.json` (facts/provenance), `charts.html` (Western wheel, north/south Indian D1, D9, D10 and tables), and `calculation.md`. It does not generate interpretation. Use all three as evidence. Open the HTML for the user if a local-file viewing tool exists; do not start a public server or upload birth data.

After a fresh runtime setup or engine change, run `scripts/self_check.py` with the same Python executable. It checks arithmetic, supported settings and DST failure behavior; it is not independent astronomical verification.

The helper supports Western Placidus/whole-sign/equal/Koch/Porphyry, Lahiri/Raman/Krishnamurti sidereal modes, D9/D10, major Western aspects, Parashari full sign-based graha drishti, nakshatra/pada, tithi, Vimshottari MD/AD and transit snapshots. Read its limitations before making claims. Do not label these computations “all astrology”.

## 3. Verify before reading

- Check UTC conversion, coordinates/sign conventions, ephemeris flags, sidereal mode and requested house method. A house-calculation failure must stop house interpretation; never silently substitute.
- Confirm ascending/descending nodes differ by 180°, Western and sidereal longitudes differ by the stated ayanamsha, 12 houses partition the ecliptic, and D9/D10 rules match the chosen school.
- Check time uncertainty endpoints and disclose any Lagna, house, nakshatra or varga changes. Endpoint agreement does not prove stability throughout an interval.
- Compare against an independent trusted ephemeris/chart when available, using identical settings. A second call to the same library is an internal consistency check, not independent verification. If unavailable, state “computed locally; not independently verified”.
- Do not say “verified twice” without naming two actual checks and their limitations. Never infer an event from a coding test.

## 4. Read structurally

Read `references/interpretation.md` and `references/report-template.md`. For each substantial claim show **placement → named traditional rule → interpretation → modifying factors → practical question**. Include contrary factors and birth-time uncertainty. No “one placement proves X”.

For complete analysis cover all 12 houses in each tradition and synthesize identity, learning, career/work, income/resources, relationships, home/family, creativity/children, friendships/networks, travel and meaning. Health is limited to symbolic wellbeing themes; do not diagnose, predict death, infertility or calamity. Financial themes are reflection, not investment instructions. Avoid gender/caste stereotypes and fear-based dosha or remedy selling.

Distinguish **calculated fact**, **traditional doctrine**, **modern interpretation**, **your inference**, and **not calculated**. Astrological interpretations are not scientifically established predictions. Explain this once plainly; do not repeat a disclaimer under every bullet.

Never equate Western aspects to graha drishti, tropical signs to same-named sidereal signs, or Western dignity to every Jyotisha strength measure. A yoga/dosha needs a precise rule, supporting positions and contextual evaluation; “condition matched” is not “outcome guaranteed”. Shadbala/Ashtakavarga/KP/Jaimini require their own specified method; do not invent scores.

## 5. Timing and output

State an explicit as-of date/time and forecast window. Dashas are periods; gochara/transits are moving positions. A snapshot does not establish an exact hit, ingress or retrograde sequence: bracket and solve the event separately if requested. Use conditional themes, not promised marriage/job/wealth dates. Read `references/report-template.md` for complete deliverables and the calculation status table.

Use bullet form for readings. Keep exact degrees/settings in tables, diagrams labelled with zodiac/house method, and text tied to chart evidence. Save a coherent `reading.md` alongside computed files, with no empty headings or fabricated “notable yogas”. Chart output remains facts even when interpretation is unavailable.

## 6. Sources and continuity

Read `references/sources.md` when sourcing rules. Cite author/title/edition/chapter/page only when inspected; otherwise cite the accessible section URL and disclose edition uncertainty. Never fabricate quotations or download copyrighted scans merely because a PDF is reachable.

When the user requests saved study progress, save a concise checkpoint using Hermes's available memory mechanism or an established local study file. Store settings, topics learned, corrections, unanswered questions and output paths. Keep raw birth details in a separate local profile only when requested; do not hardcode them in this reusable skill. Update interpretations when calculation settings change. Say “saved locally”, not “permanently trained”.

## 7. Fortune Report mode

Read `references/fortune-report.md` before generating a Fortune Report. It defines the 16-section structure, the numerology formulas (Mulank, Bhagyank, Name/Soul/Personality, Kua, Lo Shu Grid), the HTML/PDF design contract, and the non-negotiable safety boundaries: never copy a sample report's data (derive everything from the user's own DOB + name), never prescribe remedies/gems/rudraksh (especially for minors), never predict health or finance outcomes, and always carry the birth-time uncertainty caveat. Generate the chart with `scripts/chart_engine.py`, then build the branded HTML + PDF with `scripts/fortune_report.py --chart chart.json --request request.json --name "FULL NAME" --brand "BRAND" --out-dir DIR`, and write the full interpretation prose in `reading.md` following the Fortune template.
