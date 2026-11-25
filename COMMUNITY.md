# Community

This project uses GitHub for collaboration. This document describes the community
features and how to enable the one setting that cannot be committed as a file.

## Enabling GitHub Discussions (one-time manual step)

GitHub Discussions is a repository setting. It cannot be enabled by pushing a file,
so a maintainer must enable it once:

### Via the GitHub web UI

1. Go to https://github.com/narayanwithme-gif/astrology-skill
2. Click **Settings** (top right, only visible to maintainers).
3. Scroll to the **Features** section, near the top of the General page.
4. Tick **Discussions**.
5. Click **Save changes**.
6. A **Discussions** tab appears in the repository navigation bar.

### Via the GitHub API (requires a Personal Access Token)

If you have a token with `repo` scope:

```bash
curl -X PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/repos/narayanwithme-gif/astrology-skill \
  -d '{"has_discussions": true}'
```

### Via GitHub CLI

```bash
gh api -X PATCH repos/narayanwithme-gif/astrology-skill -f has_discussions=true
```

## Suggested discussion categories

After enabling Discussions, create these categories under Settings → Discussions:

| Category | Purpose |
|----------|---------|
| **Announcements** | Release notes and project news (maintainers only) |
| **Q&A** | Questions about chart calculations, settings, and interpretation |
| **Ideas** | Feature proposals before filing an issue |
| **Show and tell** | Charts, reports, and projects built with the skill |
| **General** | Everything else |

## Community guidelines

- Be respectful. Astrology is a symbolic practice, not an established science.
- Do not share real birth data of other people without consent. Use fictional data
  for bug reports and examples (see the bug report template).
- No medical, financial, legal, or safety advice derived from chart output.
- Search existing discussions and issues before opening a new one.

## Related files

- `CONTRIBUTING.md` — how to contribute code and documentation
- `SECURITY.md` — how to report security issues
- `.github/ISSUE_TEMPLATE/` — issue templates for bugs, features, and skill feedback
- `.github/pull_request_template.md` — PR review checklist

---
_GitHub Discussions guidance was added as part of the kerykeion-inspired maturity improvements._