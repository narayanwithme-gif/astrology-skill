## Description
Briefly describe the changes in this PR.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Chart calculation logic change (Western or Jyotisha)
- [ ] SKILL.md / documentation update
- [ ] Test addition or update
- [ ] Refactor (no functional change)
- [ ] Dependency / requirements change

## Testing
- [ ] `python -m unittest discover -s tests -v` passes locally
- [ ] `pip install -r requirements.txt reportlab pillow` succeeds
- [ ] `ruff check .` passes (if ruff is available)
- [ ] New chart calculation paths tested with `scripts/chart_engine.py`
- [ ] SKILL.md updated if behavior or public interface changed

## Astrology Skill Specific
- [ ] Western and Jyotisha rules kept distinct (no cross-tradition assumptions)
- [ ] Default settings disclosed: tropical + Placidus (Western), Lahiri + whole-sign Rashi (Jyotisha)
- [ ] Any new advanced feature documented in `docs/advanced-features.md` or `references/`
- [ ] Fictional data used in `assets/request.example.json` and `assets/request.advanced.example.json`
- [ ] No paid services, subscriptions, remedies, gems, health, or finance predictions introduced

## Checklist
- [ ] I have read the CONTRIBUTING.md guidelines
- [ ] I have updated SKILL.md version if the public interface changed
- [ ] I have added or updated tests for changed functionality
- [ ] PR title follows conventional commits format (e.g., `feat:`, `fix:`, `docs:`)

---
_This template is auto-injected by the gh-upskill GitHub automation skill._