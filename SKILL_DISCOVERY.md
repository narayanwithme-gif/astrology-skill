# Skill Discovery Mapping — narayanwithme-gif/astrology-skill

This document maps GitHub tasks (PRs, issues, commits) to the applicable agent skills
that should be invoked when working on the `astrology-skill` repository.

Use this as a reference for the gh-upskill `--action discover-skills` command and for
manual skill selection when working on this repo.

## Task → Skill Mapping

| GitHub Task | Applicable Agent Skills | When to Invoke |
|-------------|------------------------|----------------|
| **SKILL.md changes** | `astrology-structured`, `avoid-ai-writing`, `documentation-and-adrs` | When editing skill metadata, description, patterns, or workflow steps |
| **Python code changes** | `python-patterns`, `python-testing`, `test-driven-development` | When modifying `chart_engine.py`, `engine_utils.py`, `advanced/`, or other `.py` files |
| **Chart calculation logic** | `astrology-structured` | When changing Western/Jyotisha calculation rules, ayanamsha, house systems, or dasha logic |
| **MCP server updates** | `mcp-server-builder`, `mcp-server-patterns` | When changing MCP tool definitions, server config, or agent integration |
| **README.md / docs updates** | `documentation-and-adrs`, `doc-coauthoring` | When editing `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `RELEASE.md` |
| **Test additions / changes** | `python-testing`, `test-driven-development` | When adding or modifying files in `tests/` directory |
| **Chart diagrams / visualizations** | `diagram-design`, `scientific-visualization` | When adding chart wheel diagrams, house overlays, or visualization assets in `assets/` |
| **Workflow / CI changes** | `ci-cd-and-automation`, `deployment-patterns` | When editing `.github/workflows/*.yml` |
| **Release / version bump** | `changelog-generator`, `version-bump` | When updating `pyproject.toml` version or `CHANGELOG.md` |
| **Dependency changes** | `dependency-auditor`, `python-patterns` | When editing `requirements.txt` or `requirements-dev.txt` |
| **Fortune Report / reading templates** | `astrology-structured`, `documentation-and-adrs` | When editing `references/fortune-report.md`, `reading_templates.json`, or `scripts/fortune_report.py` |
| **Guna Milan / compatibility** | `astrology-structured` | When editing `scripts/guna_milan.py` or `references/guna-milan.md` |

## Platform-Specific Skill Activation

| Agent Platform | Primary Skills for This Repo |
|----------------|------------------------------|
| **Hermes Agent** | `astrology-structured` (native), `mcp-server-builder`, `documentation-and-adrs` |
| **Claude Code / OpenCode** | `astrology-structured`, `python-patterns`, `test-driven-development`, `ci-cd-and-automation` |
| **OpenAI Agents** | `astrology-structured`, `avoid-ai-writing` (for prose quality in skill docs) |

## Discovery Rules (for gh-upskill `--action discover-skills`)

### Rule 1: SKILL.md modified
- **Trigger:** Any PR or commit that touches `SKILL.md`
- **Skills to invoke:** `astrology-structured` (validate skill semantics), `avoid-ai-writing` (check prose quality), `documentation-and-adrs` (verify documentation structure)
- **Validation:** Run `skills-ref validate` on the skill directory; check `metadata.version` bump if public interface changed

### Rule 2: Python source modified
- **Trigger:** Any PR or commit that touches `.py` files in `scripts/` or root
- **Skills to invoke:** `python-patterns` (idiomatic Python), `test-driven-development` (verify test coverage), `ci-cd-and-automation` (verify CI still passes)

### Rule 3: Test files modified
- **Trigger:** Any PR or commit that touches files in `tests/`
- **Skills to invoke:** `python-testing`, `test-driven-development`

### Rule 4: Documentation modified
- **Trigger:** Any PR or commit that touches `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`, `RELEASE.md`, `docs/`, or `references/`
- **Skills to invoke:** `documentation-and-adrs`, `doc-coauthoring`

### Rule 5: CI/CD workflow modified
- **Trigger:** Any PR or commit that touches `.github/workflows/*.yml`
- **Skills to invoke:** `ci-cd-and-automation`

### Rule 6: Dependencies modified
- **Trigger:** Any PR or commit that touches `requirements.txt`, `requirements-dev.txt`, or `pyproject.toml` dependencies
- **Skills to invoke:** `dependency-auditor`, `python-patterns`

## Example Discovery Output

```
Trigger: PR #42 modifies SKILL.md and tests/test_engine.py

Discovered skills:
1. astrology-structured — SKILL.md semantics validation (required)
2. avoid-ai-writing — SKILL.md prose quality check (recommended)
3. python-testing — Test file changes detected (required)
4. test-driven-development — Verify red-green-refactor cycle (recommended)

Recommended command sequence:
  /gh-upskill --action discover-skills --pr 42
  /astrology-structured --validate-skill SKILL.md
  /python-testing --run tests/test_engine.py
```

## Files in This Section

| File | Purpose |
|------|---------|
| `SKILL_DISCOVERY.md` | This task-to-skill mapping reference |

---
_This skill discovery mapping is auto-injected by the gh-upskill GitHub automation skill._