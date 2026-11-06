# Release v1.4.0 — 2026-11-06

Tag: `v1.4.0` → `f5157c5` (main). Versions synced: SKILL.md 1.4.0, pyproject.toml 1.4.0, CHANGELOG [1.4.0].

## Highlights
- Guna Milan 36 + modern 0–100 synastry, dosha parihara
- Ayanamsha: lahiri / kp (Krishnamurti) / raman / drik (True Chitra)
- Minute-sensitivity boundary check (±3 min)
- Multilingual reports: English, Hindi, Hinglish, Marathi, Odia + `pdf_export.py`
- Deterministic reader (byte-identical), dual-engine drift check
- Modularised: `scripts/engine_utils.py` extracted from `chart_engine.py` (constants/helpers)

## Tests
34/34 passing locally. CI: `.github/workflows/ci.yml` (ubuntu + windows, py3.11–3.13).

## Known limitations
- External Jagannatha Hora / Drik Panchang known-answer vectors pending
- Practitioner review pending (see docs/conventions-review.md)
- GitHub Release object: create via UI (tag already pushed) — releases need a token/`gh` auth unavailable in the build agent:
  Releases → Draft new release → Tag v1.4.0 → paste [1.4.0] CHANGELOG notes → Publish.
