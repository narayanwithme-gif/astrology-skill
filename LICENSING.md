# Licensing overview

This project uses dual licensing. Pick the option that fits your use case.

| Option | License | Best for |
|--------|---------|----------|
| Open source | AGPL-3.0-or-later (`LICENSE`) | Hobbyists, researchers, open-source projects, forks that stay open |
| Commercial | `COMMERCIAL-LICENSE.md` | Proprietary products, closed-source services, commercial distribution |

## Open-source track (AGPL-3.0-or-later)

- Free to use, modify, and distribute.
- If you modify the software and make it available over a network, the AGPL
  requires you to offer the corresponding source to users interacting with it
  remotely.
- Derivatives distributed to others must remain under AGPL-3.0-or-later.
- See `LICENSE` for the full legal text and `NOTICE` for attribution.

## Commercial track

- Removes the AGPL's source-disclosure and network-copyleft obligations.
- Permits inclusion in closed-source / proprietary products.
- Requires a paid license; see `COMMERCIAL-LICENSE.md` for terms and how to
  inquire.
- Attribution and the `NOTICE` file must still be retained.

## Third-party components

This project depends on:

- `pyswisseph` (Swiss Ephemeris) — see its own license; note that Swiss Ephemeris
  has separate conditions for the Moshier fallback versus the full ephemeris
  data files.
- `tzdata` — Python timezone database, distributed under its own license.

You are responsible for complying with the licenses of these dependencies when
redistributing the software.

## How to choose

1. If you are an individual or open-source project and can comply with AGPL,
   just use the repo under `LICENSE`. No action needed.
2. If AGPL obligations conflict with your distribution model, contact the
   maintainer for a commercial license (see `COMMERCIAL-LICENSE.md`).

---
_This document was added as part of the kerykeion-inspired maturity improvements.
It is a summary, not legal advice._