# Hermes Astrology

A Hermes skill and local calculator for Western astrology and Jyotisha.

Hermes Astrology is an early-stage, open-source tool for Western astrology and Jyotisha. It combines local chart calculations and visual reports with AI-assisted interpretation. The project is documented and usable, but it’s new and has not yet attracted visible community engagement. Feedback, testing, and contributions are welcome.
The calculator produces chart data, diagrams, planetary periods and transit tables. Hermes uses the included references to write a reading from those results. Western and Jyotisha calculations remain separate throughout the report.

![Western, north Indian and south Indian chart examples](docs/images/charts.svg)

## Features

| Area | Supported calculations |
| --- | --- |
| Western natal | Tropical positions, Ascendant, Midheaven, houses and five major aspects |
| House systems | Placidus, whole sign, equal, Koch and Porphyry |
| Jyotisha | Sidereal positions, whole-sign Rashi houses and Parashari sign-based graha drishti |
| Ayanamsha | Lahiri, Raman, Krishnamurti and Drik (True Chitra) |
| Divisional charts | D9 Navamsha and D10 Dashamsha using the stated Parashari rules |
| Lunar data | Moon nakshatra, pada and tithi at the birth instant |
| Periods | Vimshottari birth balance, mahadashas and antardashas |
| Timing | Western transit aspects; Jyotisha gochara houses and graha drishti |
| Composite charts | Midpoint composite and Davison relationship charts |
| Progressions | Secondary progressions (day-for-a-year), solar and lunar returns |
| Relocation | Locality charts for the natal instant at new coordinates |
| Shadbala | Estimates for the six strength components, with degree-based Uccha |
| Ashtakavarga | Chart-dependent Bhinna and Sarva bindu counts using the unreduced 337-point table |
| KP system | Star, sub, and sub-sub lords for planets and Placidus cusps |
| Jaimini | Seven chara karakas and Rashi Drishti |
| Data checks | Historical timezones, repeated/nonexistent local times and birth-time uncertainty endpoints |
| Output | JSON, a standalone HTML chart atlas and a Markdown calculation record |

Calculations run locally through PySwissEph with the Moshier analytical ephemeris. No astrology API key or external ephemeris download is needed. Hermes's language-model provider is configured separately.

## Requirements

- Python 3.11 or newer. On Windows, PySwissEph needs the Microsoft Visual C++ runtime. Python versions without a prebuilt PySwissEph wheel also need a C/C++ build toolchain.
- Hermes for assisted readings. The calculator also works by itself.
- Internet access for the initial dependency installation. Calculations work offline afterward.

## Install as a Hermes skill

Clone or extract this repository into an `astrology-structured` folder inside the active Hermes profile's `skills` directory. Keep `SKILL.md` at that folder's root. Use `HERMES_HOME` if configured; otherwise use the profile directory reported by your Hermes installation.

From that folder, create a local Python environment.

**Windows PowerShell**

```powershell
./scripts/setup.ps1
./.venv/Scripts/python.exe scripts/self_check.py
```

**Linux or macOS**

```sh
sh scripts/setup.sh
./.venv/bin/python scripts/self_check.py
```

Start a new Hermes chat so its skill catalog is refreshed. Say:

> Use astrology-structured to calculate and read my Western and Jyotisha charts. Ask for missing birth details, show the chart settings, generate the supported diagrams and tables, and explain each conclusion from its placements. Save the report locally.

Automatic selection depends on Hermes and the model. Naming the skill explicitly is the fallback.

## Run the calculator

With the environment activated, install the command-line entry point:

```sh
python -m pip install .
hermes-astrology --input assets/request.example.json --out reports/demo
```

You can also run the script directly without installing the project:

```sh
python scripts/chart_engine.py --input assets/request.example.json --out reports/demo
```

### Local JSON API

Install the project, then start the optional localhost API:

```sh
hermes-astrology-api
```

Send the same JSON request used by the CLI to `POST http://127.0.0.1:8765/chart`.
The server binds to localhost only, accepts bodies up to 1 MB, does not log
request contents, and returns the chart JSON or a 400 error. It has no
authentication and is intended for local integrations, not public deployment.

Open `reports/demo/charts.html` in a browser. Choose a new output directory for each run; the calculator refuses to overwrite report files.

## Run an advanced report

```sh
hermes-astrology --input assets/request.advanced.example.json --out reports/advanced
```

Open `reports/advanced/chart.json` and look under `advanced`. The [advanced chart guide](docs/advanced-features.md) explains each input, calculation, and output, with a Python example and method references.

The [example request](assets/request.example.json) is fictional. For a personal reading, keep your request in the ignored `private/` directory. See [input settings](docs/input.md) for the fields and conventions.

## Reports

| File | Contents |
| --- | --- |
| `chart.json` | Positions, settings, periods, transits, uncertainty checks and provenance |
| `charts.html` | Western wheel; north and south Indian D1/D9/D10 charts; tables |
| `calculation.md` | Engine settings, internal checks and calculation warnings |
| `reading.md` | Written by Hermes using the skill's report instructions |
| `study-note.md` | Optional learning progress saved at the user's request |
| Fortune Report (Fortune Report mode) | Branded HTML + PDF, Index 01–16, Lucky Things, numerology, Lo Shu Grid, career, month-wise, Kundali, Life-Path — `scripts/fortune_report.py --lang en|hi|hinglish|mr|or` |
| Guna Milan 36 | Deterministic Ashtakoota (Varna, Vashya, Tara, Yoni, Graha Maitri, Gana, Bhakoot, Nadi) + modern 0–100 synastry — `scripts/guna_milan.py --chart-a A.json --chart-b B.json` |
| Ayanamsha | Lahiri, KP (Krishnamurti), Raman via `settings.ayanamsha` |
| Multilingual output | English, Hindi, Hinglish, Marathi, Odia templates (`references/templates.md`) + `scripts/pdf_export.py` |

The calculator writes the first three files. Interpretation and study notes require Hermes or another assistant following `SKILL.md`. See the [fictional sample atlas](examples/demo/charts.html) and [report instructions](references/report-template.md).

### Fortune Report mode

When the user asks for a branded "Fortune Report" (like a sample PDF with a purple cover, Index, Lucky Things, Mulank/Bhagyank, Lo Shu Grid, career options, month-wise themes and a Life-Path appendix), follow `references/fortune-report.md`. It defines the 16-section structure, the numerology formulas (Mulank, Bhagyank, Name/Soul Urge/Personality, Kua, Lo Shu Grid), and the safety boundaries: derive every number from the user's own birth date and name (never copy a sample report's data), never prescribe remedies/gems/rudraksh (especially for minors), never predict health or finance outcomes, and always carry the birth-time uncertainty caveat. Generate the chart with `chart_engine.py`, then build the HTML + PDF with:

```sh
python scripts/fortune_report.py --chart chart.json --request request.json --name "FULL NAME" --brand "BRAND" --out-dir reports/name
```

The PDF requires `reportlab` and `pillow`. The HTML is self-contained.

## Install (one line)

```bash
# Hermes Agent native install
hermes skills install github:narayanwithme-gif/astrology-skill

# Universal SKILL.md installer
npx skills add narayanwithme-gif/astrology-skill
```

## Scope and limits

Astrology is treated here as a traditional symbolic practice. Its interpretations are not scientifically established predictions.

The [advanced chart guide](docs/advanced-features.md#jyotisha-methods) describes the scope of Shadbala, Ashtakavarga, KP and Jaimini. A complete Panchanga, general transit-event searches, rectification and divisional charts beyond D9/D10 remain outside the calculator's scope. See [calculation conventions](references/calculation.md).

## Calculation validation status

CI checks internal calculation invariants, input handling, recorded regression
snapshots, and agreement between two PySwissEph ephemeris modes. That mode check
uses the same library on both paths and is not an independent engine or an
external chart comparison. The current test suite does not yet contain a
reviewed known-answer vector from Jagannatha Hora, Drik Panchang, or another
independent chart source. See the [validation status and contribution protocol](docs/validation-report.md).

Until an external reference vector has been reviewed, describe output as
“computed locally; not independently verified against an external chart
reference.” Birth-time uncertainty checks compare endpoints; they do not inspect
every instant within the interval. None of these checks establishes predictive
accuracy.

The test suite includes a fixture validator for future independent references.
It requires source/version, retrieval date, settings, expected values, tolerance,
and redistribution notes; pending fixtures are rejected. This makes contributed
validation reproducible, but does not replace the external vectors that are
still needed. See the [fixture protocol](docs/validation-report.md#independent-reference-vectors).

## Development

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
ruff check .
ruff format --check .
python -m build
```

GitHub Actions runs the test suite and an installed-command smoke test on Windows and Linux. To rebuild the fictional sample and README diagram:

```sh
python scripts/build_example.py
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for changes and [SECURITY.md](SECURITY.md) for reporting defects without exposing birth data.

## Standalone SVG charts

The `charts.html` atlas embeds its diagrams inline. To get standalone `.svg` files
(like the kerykeion library) for documents, websites, or graphic tools:

```sh
# Option 1: pass --svg to the engine
python scripts/chart_engine.py --input assets/request.example.json --out reports/demo --svg

# Option 2: export from an existing chart.json
python scripts/svg_export.py --chart reports/demo/chart.json --out reports/demo/svg
```

This writes `western-wheel.svg`, `d1-north.svg`, `d1-south.svg`, `d9-north.svg`,
`d9-south.svg`, `d10-north.svg`, and `d10-south.svg`. Each is a valid, self-contained
SVG with an XML declaration and namespace. The installed commands
`hermes-astrology` and `hermes-astrology-svg` expose the same functionality.

## Reproducible development

`uv.lock` pins the dependency graph for deterministic installs. For static checks,
`pyrightconfig.json` configures type checking for the `scripts/` directory.

```sh
uv sync                 # install from uv.lock
uv run python -m unittest discover -s tests -v
```

## Packaged skills for multiple agents

The `skills/` directory contains packaged `SKILL.md` variants for Hermes, Claude
Code, OpenCode, and OpenAI agents, plus a canonical copy. See
[skills/README.md](skills/README.md) for layout and regeneration steps. The root
`SKILL.md` remains the source of truth.

## Community

See [COMMUNITY.md](COMMUNITY.md) for the one-time step to enable GitHub Discussions
and suggested discussion categories. Bug reports, feature requests, and skill
feedback have dedicated issue templates under `.github/ISSUE_TEMPLATE/`.

## License

Dual-licensed: AGPL-3.0-or-later (see [LICENSE](LICENSE) and [NOTICE](NOTICE)) or a
commercial license for proprietary use (see [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)
and the overview in [LICENSING.md](LICENSING.md)). PySwissEph and Swiss Ephemeris have
their own license terms; the project uses their free AGPL route. Review those terms
before distributing a modified version or operating a public service.

Astrology is a traditional symbolic practice, not an established science. This
software does not provide medical, financial, legal, or other professional advice.
