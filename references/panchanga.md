# Panchanga and exact transit-event search

## Panchanga at the birth instant

The chart reports vara, tithi, nakshatra, yoga, and karana for the recorded
birth instant. This is an instant snapshot, not the traditional sunrise-based
Panchanga for a civil day.

- Tithi number is `floor((Moon - Sun) mod 360 / 12) + 1`; 1–15 are Shukla and
  16–30 Krishna.
- Nakshatra number is `floor(Moon longitude / (360/27)) + 1`.
- Yoga number is `floor((Sun + Moon) mod 360 / (360/27)) + 1`.
- Karana number is `floor((Moon - Sun) mod 360 / 6) + 1`. Kimstughna occurs
  first, the seven movable karanas repeat, and Shakuni, Chatushpada, and Naga
  close the 60-half-tithi cycle.
- Vara is the weekday of the local birth date. No sunrise boundary is inferred.

## Monthly sunrise calendar

`hermes-vedic-calendar` finds the local sunrise for each date with the local
PySwissEph Moshier calculation, then evaluates the same five limbs at that
instant. It requires an IANA timezone and coordinates and produces JSON. This
is suitable for inspecting calculated sunrise limbs; it is not a regional
festival/vrat engine. Festival observance can depend on sunrise rules, local
tradition, multiple-day tithi rules, and school-specific decisions that are not
implemented here.

## Exact-event search
- Ingress: solve lon(t) = cusp within [t0, t1] by bisection using PySwissEph (Moshier) at minute resolution; report bracket + solved instant; flag retrograde-touch events separately.
- Exact aspect: solve |sep(t) - angle| minimised; report closest approach instant and orb.
- Transits remain snapshots until solved; never present a snapshot as an event time.
- CLI (planned): scripts/event_search.py --chart chart.json --body Mars --kind ingress --sign Leo --from YYYY-MM-DD --to YYYY-MM-DD
