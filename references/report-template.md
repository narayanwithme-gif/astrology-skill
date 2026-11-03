# Complete report contract

Scale explanation to the question. A complete report includes the following, while a focused reading uses only relevant sections. Report missing computations in the calculation status table, rather than creating empty headings or false results.

1. **Purpose and data quality:** requested topics; date format; supplied time and uncertainty; place/coordinates/source; historical timezone/UTC; privacy/output location. One plain sentence identifying astrology as a symbolic/traditional practice without established predictive validity.
2. **Calculation manifest:** engine/version and actual flags, geocentric frame, Western zodiac/houses; Jyotisha ayanamsha/value/houses/nodes, aspect convention/orbs, dasha-year convention, exact as-of time. State internal vs independent validation status.
3. **Chart atlas:** link/embed Western natal wheel; north Indian D1; south Indian D1; D9 and D10 diagrams. Label every chart's zodiac, ayanamsha and house conventions. Western wheel positions use actual longitude; Vedic north Indian positions are fixed houses, south Indian positions fixed signs. A compact sign grid must be labelled as a grid, not falsely called a traditional north Indian chart.
4. **Data tables:** both traditions' planet sign/degree/house/motion, nodes, ASC/MC, 12 cusps or whole-sign boundaries, nakshatra/pada, D9/D10 placements, major Western aspects and Parashari graha drishti. Cite chart.json as the computed artifact. Include tithi-at-instant if requested; no claim of a complete panchanga.
5. **Western analysis:** chart overview, evidence-linked planet/ruler/house patterns, all 12 houses with topic emphasis, supportive and competing indications. Separate modern Pluto/Uranus/Neptune claims from classical ones.
6. **Jyotisha analysis:** Lagna/lord, Moon/nakshatra, graha lordship/condition, all 12 bhavas, D1/D9/D10 synthesis, rule-specific yogas/doshas actually checked. Degree-based strengths/combustion must be computed/sourced; otherwise mark not assessed.
7. **Topic readings:** identity, learning, work/business, resources, relationships, family/home, creativity, networks, travel/meaning, wellbeing. Each topic: Western evidence, Jyotisha evidence, agreement/differences, practical questions, limits. Do not give the same generic paragraph under every heading.
8. **Timing:** birth MD balance, complete calculated MD sequence, current MD/AD, requested AD schedule, separate tropical and sidereal transit tables. Interpret requested window conditionally. Do not present a snapshot as exact-event timing. If no requested window use a current snapshot and ask before generating a long future forecast.
9. **Actionable reflection:** a few experiments/checks rooted in user goals, labelled practical inference rather than astrological proof. Do not prescribe investments, medical treatment or irreversible life choices.
10. **Quality and sources:** calculation warnings; uncertainty effects; what was/wasn't assessed; actual checks; sources with verified locators. Separate astronomical calculation confidence from interpretive tradition.
11. **Continuity:** concise study/progress note, corrections and next lesson, locally saved artifact paths when requested. No birth data copied into reusable skill source.

Deliverable set: request.json (private), chart.json, charts.html, calculation.md, reading.md, and optionally study-note.md. PDFs/spreadsheets are optional if the user requests them and the relevant tool exists; do not claim exported files that were not produced. Cite free references by link; no copied book chapters.

## Calculation status table

Use four statuses: computed, interpreted, not requested, unavailable/not implemented. Include D1/D9/D10, Western aspects, graha drishti, tithi, MD/AD, transit snapshot, event search, panchanga, shadbala, ashtakavarga, other vargas and compatibility scoring as relevant. Completeness means truthful coverage of requested scope, not fabricated output for every technique.
