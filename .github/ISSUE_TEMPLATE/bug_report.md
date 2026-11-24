---
name: Bug report
about: Report a chart calculation or interpretation bug
title: "[BUG] "
labels: ["bug"]
assignees: ["narayanwithme-gif"]
---

## Bug Description
Briefly describe what went wrong.

## Expected Behavior
What you expected to happen instead.

## Steps to Reproduce
1. Run `scripts/chart_engine.py --input ...` with...
2. Call `hermes-astrology --input ... --out ...`
3. Observe the output...

## Environment
- **OS:** (e.g., Ubuntu 24.04, Windows 11, macOS 15)
- **Python version:** (e.g., 3.11.9)
- **Package version:** (check `pyproject.toml` version, e.g., 1.4.0)
- **Tradition:** (Western / Jyotisha / both)
- **Ayanamsha (Jyotisha):** (Lahiri / KP / Raman / other)
- **House system (Western):** (Placidus / Whole-sign / other)

## Input Data (use fictional data)
Please attach or paste a **fictional** request JSON. Do not share real birth data.

```json
{
  "name": "Fictional Person",
  "dob": "YYYY-MM-DD",
  "time": "HH:MM",
  "timezone": "IANA timezone (e.g., Asia/Kolkata)",
  "place": "City, Country",
  "tradition": "western",
  "topics": []
}
```

## Output / Error
Paste the actual output, error message, or stack trace.

## Additional Context
Add any other context about the problem here.

---
_This issue template is auto-injected by the gh-upskill GitHub automation skill._