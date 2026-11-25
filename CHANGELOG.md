# 1.5.0 (2026-11-25)

- Add an optional localhost-only JSON API (`hermes-astrology-api`) for chart
  calculations; request bodies are not written to access logs.
- Add external-vector fixture validation that requires source/version,
  retrieval date, settings, expected values, tolerance, and redistribution notes.
- Document that fixture tooling is not itself independent accuracy evidence.
- Add all five instant-based Panchanga limbs to chart JSON and the HTML atlas,
  with an explicit warning that results are not sunrise-anchored.
- Add an offline sunrise-based monthly Panchanga JSON CLI, with calendar
  generation and CLI smoke coverage in CI.
- Add an optional offline PyJHora adapter for regional festival and vrata-date
  searches, a source-derived 58-system dasha selector catalog, and 22 upstream
  language identifiers; document six-language festival translation coverage,
  convention sources, licensing, and review limits.
- Add 252 deterministic Jyotisha interpretive templates with chart-specific
  indicators, plus ten Tamil Dasa Porutham compatibility checks beside the
  existing Ashtakoota workflow; publish selected source conventions and limits.
- Add Report Charts and Report Diagrams agent skills, an offline HTML visual
  renderer, and chart-derived distribution and timeline visuals for reports.

# Changelog

## Unreleased

- Expose midpoint and Davison charts, synastry, secondary progressions, solar and lunar returns, and relocation through the calculator request.
- Add chart-dependent Ashtakavarga, Shadbala component estimates, KP subdivisions and cusps, and Jaimini karakas and sign aspects to the advanced JSON report.
- Fix the KP exceptions and package the helper modules used by the installed command. Exercise the advanced example in CI.
- Document advanced inputs, conventions, and validation limits with a fictional request.

## [1.4.0] - 2026-11-06
- **Minute-sensitivity boundary check**: `scripts/boundary_check.py` perturbs birth time ±3 min and flags D1/D9/D10 + Moon-pada flips with rectification directive
- **Dosha parihara**: `guna_milan.evaluate_dosha_cancellations` (Nadi/Bhakoot/Mangalik flags + effective score after cancellation)
- **Ayanamsha**: added `drik` (True Chitra) alongside `lahiri` / `kp` (Krishnamurti) / `raman`
- **Multilingual PDF**: `references/templates.md` (English, Hindi/Hinglish, Marathi, Odia) + `scripts/pdf_export.py`; `fortune_report.py --lang`
- **Distribution**: one-line install in README; tests 34/34 passing

## [1.3.0] - 2026-11-06
- **Guna Milan 36**: deterministic Ashtakoota (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) in `scripts/guna_milan.py`, with modern 0–100 synastry alongside. CLI: `guna_milan.py --chart-a A.json --chart-b B.json`
- **Selectable ayanamsha**: `lahiri`, `kp` (Krishnamurti alias), `raman` in `settings.ayanamsha`; KP practitioners no longer need a separate tool
- **Multilingual + PDF**: `references/templates.md` (English, Hindi/Hinglish, Marathi, Odia) driven by user language preference; `fortune_report.py --lang` and lightweight `scripts/pdf_export.py` for marketplace-ready listing (Agensi x Narayan)

## [1.2.0] - 2026-11-05
- Fortune Report mode (branded HTML+PDF, Kua, Lo Shu Grid, HTML/XML escaping)
- Deterministic reading generator (byte-identical from chart.json)
- Dual-engine validation harness and external-vector test suite
- Panchanga / transit-event-search and Ashtakavarga/Shadbala/KP-Jaimini specs
- Docs: validation report, conventions review, golden tests (22+)

Known limitations: external Jagannatha Hora / Drik Panchang vectors pending;
practitioner review pending; Shadbala/Ashtakavarga/KP-Jaimini not implemented.
