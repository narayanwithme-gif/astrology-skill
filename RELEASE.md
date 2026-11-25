# Release v1.5.0 — 2026-11-25

Tag: `v1.5.0`. Versions synced: `SKILL.md` 1.5.0, `pyproject.toml` 1.5.0,
all packaged skills 1.5.0. Full curated notes: [release_notes/v1.5.0.md](release_notes/v1.5.0.md).

## Highlights

- Instant-based Panchanga (five limbs) in chart JSON and the HTML atlas.
- Offline sunrise Vedic calendar CLI (`hermes-vedic-calendar`).
- Offline festival and vrata dates via an optional PyJHora adapter, plus a
  source-backed 58-system dasha catalog.
- 252-rule deterministic Jyotisha indicator library (`hermes-vedic-predictions`).
- Ten Tamil Dasa Porutham checks beside Ashtakoota (`--method porutham10|both`).
- Offline report visuals: percentage bars, timelines, tables, step diagrams
  (`hermes-report-visuals`), plus D1 distribution and dasha timeline in the atlas.
- Standalone SVG chart export (`hermes-astrology-svg` or `hermes-astrology --svg`).
- Optional localhost-only JSON chart API (`hermes-astrology-api`).
- Dual licensing (AGPL-3.0-or-later or commercial).
- Packaged SKILL.md variants for Hermes, Claude Code, OpenCode, and OpenAI.
- Deterministic installs (`uv.lock`) and type checking (`pyrightconfig.json`).

## Tests

82 passed, 6 skipped (optional external datasets). CI: `.github/workflows/ci.yml`
(ubuntu + windows, Python 3.11–3.13). Installed-command smoke test included.

## CLI commands

| Command | Purpose |
|---------|---------|
| `hermes-astrology` | Calculate charts and write the report atlas |
| `hermes-astrology-svg` | Export standalone SVG chart files |
| `hermes-astrology-api` | Localhost-only JSON chart API |
| `hermes-vedic-calendar` | Sunrise-based monthly Panchanga JSON |
| `hermes-vedic-full` | Extended Vedic tools |
| `hermes-vedic-predictions` | 252-rule indicators and Porutham checks |
| `hermes-report-visuals` | Render offline report visualizations |

## Known limitations

- Regional festival/vrata lookups need the optional PyJHora adapter and have
  source and translation limits.
- General transit-event searches, rectification, and vargas beyond D9/D10 are
  outside calculator scope.
- Jyotisha indicators are evidence-linked themes, not guaranteed events.
- External Jagannatha Hora / Drik Panchang known-answer vectors remain pending;
  practitioner review is in `docs/conventions-review.md`.
- Astrology is a traditional symbolic practice, not an established science.

## Publishing the GitHub Release object

The release workflow (`.github/workflows/release.yml`) triggers on the `v1.5.0`
tag and creates the GitHub Release, attaching the built sdist and wheel. It uses
`release_notes/v1.5.0.md` as the release body when present. If a Release must be
created manually: Releases -> Draft a new release -> Tag `v1.5.0` -> paste
`release_notes/v1.5.0.md` -> Publish.
