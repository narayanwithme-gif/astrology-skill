# Input settings

Start with `assets/request.example.json`. JSON must be UTF-8; a UTF-8 byte-order mark is accepted. The calendar is Gregorian, with supported birth and snapshot years 1800–2399.

## Birth data

| Field | Required | Meaning |
| --- | --- | --- |
| `birth.date` | Yes | `YYYY-MM-DD` |
| `birth.time` | Yes | Local wall time, `HH:MM` or `HH:MM:SS`, without an offset |
| `birth.timezone` | Yes | IANA name, such as `Asia/Kolkata` |
| `birth.latitude` | Yes | North positive, −89.9 to 89.9 degrees |
| `birth.longitude` | Yes | East positive, −180 to 180 degrees |
| `birth.fold` | When ambiguous | `0` for the first occurrence of a repeated local time, `1` for the second |
| `birth.uncertainty_minutes` | No | Symmetric uncertainty around the supplied instant, 0–1440 minutes |
| `birth.place` | No | Display metadata; no automatic geocoding |
| `birth.coordinate_source` | No | Where the coordinates came from |
| `birth.time_source` | No | Source of the recorded time |

The helper needs a birth time to calculate a full chart. It does not infer missing coordinates or use noon for an unknown time. The skill can explain what remains interpretable without a timed chart.

Nonexistent local times during a DST transition are rejected. Repeated local times require an explicit `fold`. An omitted uncertainty interval does not establish that the recorded time is exact.

## Calculation settings

| Field under `settings` | Default | Options |
| --- | --- | --- |
| `western_houses` | `P` | `P` Placidus, `W` whole sign, `E` equal, `K` Koch, `O` Porphyry |
| `ayanamsha` | `lahiri` | `lahiri`, `raman`, `krishnamurti` |
| `nodes` | `mean` | `mean`, `true` |
| `dasha_year_days` | `365.25` | Fixed year length from 350 to 370 days |
| `aspect_orb_degrees` | `6` | Uniform major-aspect orb, 0–12 degrees |

Jyotisha uses whole-sign Rashi houses. The Western house selection does not change that. Polar failures in a requested house system are errors; the calculator does not silently substitute another method.

## Snapshot and label

`label` is a report heading. `as_of` is an ISO timestamp with an explicit offset, such as `2026-11-03T12:00:00+05:30`. If omitted, the current UTC instant is recorded. Use a fixed timestamp for reproducible results.

## Output conventions

All longitudes are in `[0, 360)`. Sign indexes begin with Aries at 0; houses are numbered 1–12. Stored positions retain floating-point precision; displayed positions round to the nearest arcsecond.

The output identifies the engine, dependency versions, UTC conversion and settings. `chart.json` retains the original request, so treat it as private when it contains real data.

The calculator writes `chart.json`, `charts.html` and `calculation.md`. A malformed request or failed calculation returns exit code 2. Existing report files are not overwritten. Error output is JSON on stderr, except standard command-line usage errors.
