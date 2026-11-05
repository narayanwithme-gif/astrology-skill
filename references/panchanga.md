# Panchanga and exact transit-event search

## Panchanga (sidereal, Lahiri)
- tithi = floor((Moon - Sun) mod 360 / 12) + 1, paksha = Shukla (1-15) / Krishna (16-30) (at instant).
- nakshatra = floor(Moon_lon / (360/27)), pada within; vara from weekday; karana and yoga are derived from tithi and (Sun+Moon) lon/13°20' respectively.
- Sunrise/sunset require a location + solar ephemeris cross-check; mark as not sunrise-anchored when the instant tithi is used.
- Status: computed (instant), sunrise panchanga pending location-anchored day boundary.

## Exact-event search
- Ingress: solve lon(t) = cusp within [t0, t1] by bisection using PySwissEph (Moshier) at minute resolution; report bracket + solved instant; flag retrograde-touch events separately.
- Exact aspect: solve |sep(t) - angle| minimised; report closest approach instant and orb.
- Transits remain snapshots until solved; never present a snapshot as an event time.
- CLI (planned): scripts/event_search.py --chart chart.json --body Mars --kind ingress --sign Leo --from YYYY-MM-DD --to YYYY-MM-DD
