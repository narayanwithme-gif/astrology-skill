# Validation report

## Method
- Internal consistency (bundled): Rahu/Ketu 180°, tropical-sidereal offset =
  ayanamsha, 12 houses partition the ecliptic. Run on every chart.
- Independent engine comparison: `scripts/validate_engine.py --chart chart.json`
  recomputes Sun–Saturn longitudes with a second ephemeris path
  (FLG_SWIEPH, Swiss/JPL file ephemeris) and reports per-body deltas.
  Tolerance: 0.01° (configurable). Publication of the delta table is
  required before any "independently verified" claim.

## How to run
```sh
python scripts/chart_engine.py --input request.json --out report-dir
python scripts/validate_engine.py --chart report-dir/chart.json --tol 0.01
```

## Status
- Dual-engine drift reporting: implemented (validate_engine.py).
- Known-answer test vectors from Jagannatha Hora / Drik Panchang: pending.
- Until the vector suite passes in CI, charts are described as
  "computed locally; dual-engine drift measured" (not "independently verified"
  against an external panchanga).
