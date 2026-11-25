# Packaged agent skills

This directory packages the astrology skill for multiple agent platforms,
mirroring the pattern used by projects such as
[kerykeion](https://github.com/g-battaglia/kerykeion).

## Layout

| Path | Purpose |
|------|---------|
| `astrology-structured/SKILL.md` | Canonical packaged skill — identical to the root `SKILL.md`. |
| `hermes/SKILL.md` | Variant for Hermes Agent, with platform notes. |
| `claude-code/SKILL.md` | Variant for Claude Code, with platform notes. |
| `opencode/SKILL.md` | Variant for OpenCode, with platform notes. |
| `openai/SKILL.md` | Variant for OpenAI agents, with platform notes. |
| `report-charts/SKILL.md` | Guide for percentage bars, tables, and quantitative reports. |
| `report-diagrams/SKILL.md` | Guide for timelines, workflows, and astrology chart layouts. |

The two report skills are maintained separately. Open them from the repository
alongside the [report visual reference](../references/report-visuals.md) and
the local renderer in `scripts/report_visuals.py`.

## Source of truth

The **root `SKILL.md`** is the maintained source of truth. The copies in this
directory are packaging artifacts. When you change the root skill, regenerate the
variants:

```powershell
$src = Get-Content -Raw -Path "SKILL.md"
$platforms = @("hermes","claude-code","opencode","openai")
foreach ($p in $platforms) {
    $notes = "`n`n---`n`n## Platform notes ($p)`n`nThis SKILL.md is packaged for the **$p** agent platform. The canonical, maintained copy lives at the repository root."
    Set-Content -Path "skills/$p/SKILL.md" -Value ($src + $notes) -Encoding UTF8
}
Copy-Item SKILL.md skills/astrology-structured/SKILL.md -Force
```

## Installation

Copy the desired variant folder into your agent's skills directory, keeping the
folder name `astrology-structured` if you want natural-language discovery by that
name:

- Hermes Agent: `~/.hermes/skills/astrology-structured/`
- OpenCode / Claude Code: `~/.config/opencode/skills/astrology-structured/` or
  `~/.claude/skills/astrology-structured/`

Scripts and reference files resolve relative to the SKILL.md file, so copy the
whole repository (or at minimum `scripts/`, `references/`, `docs/`, `assets/`,
and `reading_templates.json`) alongside the skill.

## Validation

Check that every packaged SKILL.md is valid:

```bash
skills-ref validate skills/astrology-structured
skills-ref validate skills/hermes
```

---
_Packaged skills were added as part of the kerykeion-inspired maturity improvements._
