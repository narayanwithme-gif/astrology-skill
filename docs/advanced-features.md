# Advanced chart guide

Use Python 3.11 or newer and install [the calculator](../README.md#run-the-calculator). The example uses fictional birth data and requests every advanced calculation.

```sh
hermes-astrology --input assets/request.advanced.example.json --out reports/advanced
```

You can also run `python scripts/chart_engine.py` with the same arguments from a checkout. Open `reports/advanced/chart.json` and look under `advanced` for the requested results. The accompanying HTML atlas shows the natal charts and transit tables. The optional request leaves the normal natal and transit workflow available with the same input fields.

## Request fields

Add an `advanced` object to a [normal request](input.md). The object can contain any combination of these keys.

| Key | Value | Result |
| --- | --- | --- |
| `composite` | Second birth object with date, local time, IANA timezone, latitude, longitude, and `fold` when needed | Shortest-arc midpoint positions and inter-chart major aspects, using the configured aspect orb |
| `composite.davison_location` | Optional object with latitude and longitude | House chart for the exact UTC midpoint between the two births at the supplied coordinates |
| `progressions` | `true`, with the root `as_of` field set | Secondary progressions at the target instant |
| `relocation` | Object with destination latitude and longitude | Natal planets with houses and angles recalculated at the destination |
| `solar_return` | Integer near-birthday year, 1800–2399 | Sun's return to its natal longitude near the UTC birthday in that year |
| `lunar_return` | ISO timestamp with a UTC offset | Moon's return to its natal longitude closest to that instant |
| `vedic` | List containing any of `shadbala`, `ashtakavarga`, `kp`, and `jaimini` | Selected Jyotisha calculations |

For latitude and longitude, use decimal degrees with north and east positive. See the [complete request](../assets/request.advanced.example.json). `chart.json` retains the input, including both birth records when calculating a composite.

## Western methods

- **Composite and synastry.** The midpoint method averages each pair of longitudes along the shorter arc, including the Ascendant and Midheaven. At exact opposition, either arc is equally short and the implementation chooses the midpoint 90° past the smaller normalized longitude. The midpoint result contains positions and angles. The optional Davison calculation uses your supplied location, so enter a geographic midpoint yourself if that is the convention you want. Synastry lists the inter-chart pairs and their exact orb.
- **Secondary progressions.** Each 365.25 days elapsed from birth moves the ephemeris time forward by one day. The result records the target instant, progressed instant, age, and the chart for the progressed instant at the birth location. The target must be at or after birth.
- **Returns.** The engine brackets the tropical longitude crossing and narrows it numerically. Solar returns use a three-day window on either side of the UTC birthday. February 29 uses February 28 as the search anchor in common years. Lunar returns use a 16-day window on either side of the target. The result records the UTC instant and residual orb. Both use the birth location for house calculation.
- **Relocation.** The birth UTC instant stays fixed. Changing location changes the angles, cusps, and house placements. Geocentric planetary longitudes stay the same. If the requested Western house system fails at a high latitude, request a supported house system explicitly.

## Jyotisha methods

| System | What the report computes | Scope |
| --- | --- | --- |
| [Shadbala](../references/shadbala.md) | Sthana, Dig, Kala, Cheshta, Naisargika, and Drik estimates, with Uccha included in Sthana | Results carry their assumptions. Kala and Cheshta use clock time and motion direction. The total has no classical pass threshold. |
| [Ashtakavarga](../references/ashtakavarga.md) | Bhinna rows for seven grahas, Sarva sums by sign, and the totals in house order | Unreduced tables with eight contributors per row, including Lagna. The twelve Sarva totals sum to 337. |
| [KP](../references/kp-jaimini.md#krishnamurti-paddhati) | Star, sub, and sub-sub lords for planets and cusps, natal house of each cusp's sub lord, and natal ruling-planet factors | Uses a dedicated Krishnamurti sidereal Placidus chart. The main Jyotisha chart keeps its selected ayanamsha and whole-sign houses. The result covers these factors rather than a full KP event workflow. |
| [Jaimini](../references/kp-jaimini.md#jaimini) | Seven chara karakas and Rashi Drishti sign aspects | Uses the main sidereal chart. Chara Dasha is marked unavailable pending a documented school-specific implementation. |

## Python usage

```python
import json
from pathlib import Path

from chart_engine import calculate

request = json.loads(Path("assets/request.advanced.example.json").read_text(encoding="utf-8"))
report = calculate(request)
print(report["advanced"]["vedic"]["ashtakavarga"]["sarva"]["sign_totals"])
```

For a direct module API, see the functions in [composite_charts.py](../scripts/composite_charts.py), [progressions.py](../scripts/progressions.py), and [relocation.py](../scripts/relocation.py). Standalone sidereal calculations accept a chart settings dictionary containing the desired ayanamsha and node mode. The relocation module also offers a coarse single-latitude ecliptic planet-angle search.

## Verification

The automated suite checks a worked Ashtakavarga table against the source text, KP subdivision examples, and chart invariants such as unchanged relocation longitudes and small return orbs. For comparison with external software, match the UTC instant, coordinates, sidereal mode, node mode, house system, and calculation variant first. See the [validation report](validation-report.md) for external chart validation status.
