# Calculation contract

## Inputs and conventions

JSON schema is exemplified in assets/request.example.json. ISO Gregorian birth date, local wall time HH:MM[:SS], IANA timezone, east-positive longitude and north-positive latitude are required. Dates 1800–2399 are supported by this helper. Place text is metadata, never geocoded implicitly. `birth.fold` must explicitly be 0/1 for an ambiguous repeated local time; nonexistent DST times are rejected. `as_of` must include a UTC offset; if omitted the current UTC instant is recorded in output.

Default Moshier analytical ephemeris is intentionally requested through Swiss Ephemeris, so no external ephemeris files, paid service, silent file fallback or network is necessary. This is **not** the Swiss/JPL file ephemeris. Report the actual engine and returned flags. Output positions are geocentric apparent ecliptic longitudes of date; Western houses use ecliptic longitude membership, not a latitude-aware mundane house-position algorithm. Near-cusp interpretation must disclose this.

House methods: P=Placidus, W=whole sign, E=equal (Ascendant cusp), K=Koch, O=Porphyry. Polar failures are errors; ask for an explicit supported alternative. Jyotisha uses whole-sign Rashi houses, not Sripati/bhava-chalit. Ayanamshas: lahiri, raman, krishnamurti. Mean/true node switch changes both Rahu and Ketu. Rahu/Ketu retrograde labels follow computed node speed; do not assume true-node motion is always negative.

## Derived computations

- Degrees use [0,360); signs start at Aries; houses 1–12. D9 = 9 × sidereal longitude modulo 360. This is standard Parashari Navamsha (movable same sign, fixed ninth, dual fifth).
- D10: divide a Rashi into ten 3° parts; odd numbered signs start from themselves, even numbered signs from their ninth. Advance a sign for each part; preserve the fractional position within that part. D9/D10 houses are whole-sign relative to the corresponding varga Ascendant. These vargas use the stated Parashari rules; alternatives are not silently substituted.
- Nakshatras: 27 equal divisions starting with Ashwini at sidereal 0° Aries; pada = quarter. Krittika's lord is Sun. This helper does not use Abhijit as a 28th division.
- Vimshottari order: Ketu 7, Venus 20, Sun 6, Moon 10, Mars 7, Rahu 18, Jupiter 16, Saturn 19, Mercury 17 years. Moon's fraction through birth nakshatra determines elapsed birth mahadasha. Antardasha starts with MD lord, lengths = MD years × AD years / 120. Timeline begins before birth at the initial MD's calculated start. A year is a configurable fixed positive number of days, default 365.25; calendars/360-day conventions can change boundaries. Output includes first full 120-year cycle from that start; current period can be null outside it.
- Major Western aspects: conjunction 0°, sextile 60°, square 90°, trine 120°, opposition 180°. A uniform configurable 6° orb is a software convention, not a universal tradition. Reports include exact angular separation and deviation; no applying/separating classification or minor aspects is implied. Only planets Sun–Pluto are in the aspect matrix; no angle/node aspects are asserted.
- Parashari full sign-based graha drishti: Sun/Moon/Mercury/Venus 7th; Mars 4th/7th/8th; Jupiter 5th/7th/9th; Saturn 3rd/7th/10th, counting own sign as first. No node aspects by default. This is not exact degree-based sphuta drishti, Western aspects or Jaimini Rashi drishti.
- Tithi = floor((Moon−Sun mod 360)/12)+1. Paksha follows tithi 1–15/16–30. This is the tithi at the instant, not a sunrise-based day panchanga. No sunrise, karana, yoga, vara or muhurta calculation is implied.
- Western transit output compares tropical moving-to-natal major aspects. Jyotisha gochara output supplies sidereal moving grahas, houses from natal Rashi Lagna and Parashari full sign-based moving-to-natal drishti. Western degree aspects are not substituted for Jyotisha drishti. Both include nodes using the chosen mode. These are snapshots, not exact-hit dates or forecasts.

## Validation and uncertainty

The helper runs one chart request per process. Swiss Ephemeris sidereal settings are process-global; use separate processes for concurrent requests with different settings.

Request `uncertainty_minutes` when known. Endpoint comparisons include ASC sign, Moon nakshatra, planetary houses, D9/D10 Lagna and planet signs. These are diagnostics, not exhaustive interval proof. Full rectification requires evidence beyond astrology and is not implemented here.

Two separately named checks: (1) automated arithmetic/range/UTC invariants; (2) comparison with an independent engine or external chart using matching settings. Only (1) is bundled. Never call two uses of this library independent. Recomputed cross-system offsets are internal consistency checks.

Before software distribution/public service review dependencies' AGPL licensing; a paid license is not required for the free compliant route. No proprietary book text is bundled.
