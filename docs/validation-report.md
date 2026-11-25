# Calculation validation status

This page separates checks the project runs today from the independent reference
comparisons that still need contributed source data.

## Checks in CI

- **Internal invariants:** Rahu/Ketu are opposite, the stated tropical/sidereal
  offset is applied, house cusps form a complete 360° partition, and supported
  settings and date/time failures behave as expected.
- **Regression snapshot:** the fictional demo checks that the project's output
  does not drift from a recorded project-generated Sun longitude. This is a
  regression check, not an external accuracy reference.
- **Ephemeris-mode agreement:** `scripts/validate_engine.py` compares the
  calculator's Moshier output with a Swiss-file ephemeris request through the
  same PySwissEph library. This is not an independent engine comparison. The
  report includes returned flags because Swiss ephemeris files may be missing
  and the library may fall back to another mode. The check uses the ayanamsha
  recorded in the chart settings.

Run the suite with:

```sh
python -m unittest discover -s tests -v
```

Run the ephemeris-mode agreement check on a chart:

```sh
python scripts/chart_engine.py --input assets/request.example.json --out reports/demo
python scripts/validate_engine.py --chart reports/demo/chart.json --tol 0.01
```

Inspect each body's `returned_flags` in the JSON report. A passing result means
the selected calculation modes agree within the configured tolerance; it does
not prove agreement with a separate astrology application or establish
predictive accuracy.

## Independent reference vectors

**Status: not yet established.** No test vector is currently enabled from a
reviewed Jagannatha Hora, Drik Panchang, or other independent chart export.
Until such vectors are captured and checked into the repository, describe
charts as “computed locally; not independently verified against an external
chart reference.”

`tests/test_vectors.py` now provides a fixture validator and runner for this
purpose. A fixture must identify its source and version, retrieval date,
settings, request, expected values, tolerance, and redistribution note. Numeric
expected values use dotted paths into the chart JSON; angular differences wrap
at 360°. Pending fixtures are rejected and cannot silently count as passing
validation. This is infrastructure for contributed evidence, not evidence by
itself.

When contributing a vector, include:

1. A fictional or public-domain birth record, with local date/time, IANA
   timezone, coordinates, and any fold choice for an ambiguous clock time.
2. The comparison application's name and version, plus the retrieval date or
   an archived export that can be redistributed.
3. Matching settings: zodiac, ayanamsha, node mode, house system, ephemeris,
   and the exact bodies/points compared.
4. The exported values, a justified tolerance, and a note for known convention
   differences.

Do not add real private birth data, screenshots containing personal data, or
values copied from another test run of this project as an external reference.

Before enabling a contributed fixture, a reviewer should reproduce the source
values independently, check the calculation conventions, and confirm that the
fixture's birth record and exported values may be redistributed.
