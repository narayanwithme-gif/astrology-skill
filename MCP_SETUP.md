# GitHub MCP Setup for Astrology Skill

This document explains how to configure the GitHub Model Context Protocol (MCP) server so that AI agents (Hermes, Claude Code, OpenCode, etc.) can access the `narayanwithme-gif/astrology-skill` repository.

## What the GitHub MCP server enables

Once connected, agents can:

- Read repository contents (SKILL.md, README.md, chart data, reference docs)
- Read and create issues (bug reports, feature requests, skill feedback)
- Read and create pull requests
- Add labels, assign reviewers, trigger workflows
- Read workflow runs and CI status
- Access file contents across branches

## Step 1: Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens/new
2. Token name: `astrology-skill-mcp` (or similar)
3. **Expiration:** Choose a duration (e.g., 90 days) or no expiration
4. **Select scopes (required):**
   - `repo` (full control of private/public repositories — needed for read/write access)
   - `workflow` (to trigger and read GitHub Actions runs)
5. Click **Generate token**
6. Copy the token immediately — you won't see it again

> **Security warning:** Never commit this token to the repository. Store it in your agent's environment variables or secret manager.

## Step 2: Configure the MCP server

### Option A: OpenCode / Claude Code

Add to your OpenCode MCP configuration (`~/.config/opencode/mcp.json` or your platform's MCP config):

```json
{
  "mcpServers": {
    "github-astrology-skill": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
```

### Option B: Hermes Agent

Add to your Hermes MCP configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
```

### Option C: Repo-local config (`.mcp/github-mcp.json`)

The file at `.mcp/github-mcp.json` in this repo contains a template. Copy it to your agent's MCP config location and replace `${GITHUB_PERSONAL_ACCESS_TOKEN}` with your actual token:

```bash
cp .mcp/github-mcp.json ~/.config/opencode/mcp.json
# Then edit and insert your token
```

## Step 3: Install the MCP server dependency

The GitHub MCP server is distributed as an npm package. Install it globally or let your agent's MCP runner install it on demand:

```bash
npm install -g @modelcontextprotocol/server-github
```

Or if your agent handles MCP installation automatically (most do), just ensure `npx` is available.

## Step 4: Verify the connection

After configuration, ask your agent to:

- "List the open issues in narayanwithme-gif/astrology-skill"
- "Read the SKILL.md file from narayanwithme-gif/astrology-skill"
- "What pull requests are open in narayanwithme-gif/astrology-skill?"

If the agent can access this information, the MCP connection is working.

## Step 5: Token security

- **Never** commit `GITHUB_PERSONAL_ACCESS_TOKEN` to this repository
- **Never** share your token in chat or paste it into public channels
- Rotate the token periodically (every 90 days recommended)
- If you suspect the token is compromised, revoke it immediately at https://github.com/settings/tokens

## Required token scopes

| Scope | Purpose |
|-------|---------|
| `repo` | Read/write repository contents, issues, PRs |
| `workflow` | Read/write GitHub Actions workflows |

For read-only access, you can use `public_repo` instead of `repo`, but write operations (creating issues, PRs, comments) will not work.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `npx: command not found` | Install Node.js (includes npm/npx) |
| Token invalid or expired | Regenerate at github.com/settings/tokens |
| 403 Forbidden on repo access | Ensure token has `repo` scope and repo is accessible |
| MCP server not found | Run `npm install -g @modelcontextprotocol/server-github` |

## Files in this repo

| File | Purpose |
|------|---------|
| `.mcp/github-mcp.json` | Template MCP server configuration |
| `MCP_SETUP.md` | This setup guide |

---
_This setup guide is auto-injected by the gh-upskill GitHub automation skill._