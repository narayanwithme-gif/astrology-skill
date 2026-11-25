# Full Vedic calendar and dasha catalog

## Local install and privacy

The base calculator remains small. Install the optional, free PyJHora package to
enable the wider dasha catalog and festival/vrata dataset:

```sh
python -m pip install 'hermes-astrology[vedic-full]'
```

This extension accepts coordinates, dates and an IANA timezone directly. It does
not call a hosted astrology API, geocoder, or language-model service. The
upstream package bundles desktop/geocoding dependencies, but this project does
not invoke its UI, geocoding, or web-service modules. PyJHora is
AGPL-3.0-or-later; review [LICENSING.md](../LICENSING.md) before redistribution.

## Commands

```sh
hermes-vedic-full dashas
hermes-vedic-full languages
hermes-vedic-full festivals --start 2026-11-01 --end 2026-11-30 --timezone Asia/Kolkata --latitude 19.076 --longitude 72.878 --calendar traditional --language hi --place Mumbai --out reports/festivals.json
hermes-vedic-full vratas --start 2026-11-01 --end 2026-11-30 --timezone Asia/Kolkata --latitude 19.076 --longitude 72.878 --vrata ekadhashi --place Mumbai --out reports/vratas.json
```

## Source and conventions

The extension pins [PyJHora 5.0.6](https://github.com/naturalstupid/PyJHora)
and uses its `dhasa_selector` wrappers, `panchanga.vratha` rules, and bundled
`hindu_festivals_multilingual_unicode_bom.csv`. The pinned selector exposes 58
root-and-child dasha selectors. This command lists that catalog; it does not
claim this project computes every listed dasha. A count alone is not evidence
that each method has independent validation. The native calculator continues
to compute its documented Vimshottari periods using its own stated 365.25-day
year convention.

The festival matcher uses dataset rows and upstream criteria: calendar type,
tithi at sunrise (plus a kshaya tithi where applicable), nakshatra, month, day,
weekday, adhika masa, and optional day offset. The special-vrata finder uses
the named rule implementation in PyJHora. Results depend on place and calendar
convention. They are not a universal ruling for all regions or sampradayas;
confirm observances with a local panchanga.

Festival searches default to the `traditional` preset, which includes source
solar, amanta, purnimanta, and Nepal Bikram Sambat rows. Use `--calendar solar`,
`amanta`, `purnimanta`, `nepal-bikram-sambat`, or `all` to select another source
calendar set. The `all` preset can also include non-Hindu/Gregorian dataset rows.

PyJHora advertises 22 UI language identifiers. Its bundled festival CSV has
festival-name columns only for English, Tamil, Telugu, Kannada, Hindi, and
Malayalam; other selected language codes fall back to English. This repository
does not claim the upstream translations are independently reviewed. The
original source and its translation caveats are documented in the
[PyJHora repository](https://github.com/naturalstupid/PyJHora).

## Validation status

Project tests check the source-derived dasha catalog, language identifiers,
and festival/vrata calls on representative dates. This is integration coverage,
not independent scholarly validation of every rule or dasha variant. A
practitioner review log belongs in [conventions-review.md](../docs/conventions-review.md);
do not label translations as reviewed until named reviewers sign off.
