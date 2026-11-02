# sam-workflow

A Claude Code workflow for working a Jira card end to end: investigate → plan ⛔ → implement → review → live browser test → commit ⛔ → Jira/MR text.
The orchestrator skill (`sam-task`) talks to you; subagents do implement / review / test / close.

## Install
```bash
bash update.sh   # installs into ~/.claude (backs up anything it replaces), re-run after every pull
```
Edit `~/.claude/sam-models.conf` (created from `sam-models.conf.example`; never overwritten): model/effort per role, browser MCP, `ticket_prefix`, `jira_url`, `card_language`. Local-only skills in `~/.claude/skills/` are untouched. Re-run `~/.claude/sam-models-sync.py` after editing.

Expects a per-repo `.claude/skills/project/SKILL.md` (dirs, validate commands, base branch, commit conventions) — write your own.
Plans are saved to `.claude/plans/<KEY>.md` (gitignore it). Browser testing needs one browser MCP (built-in, Claude in Chrome, Playwright, or chrome-devtools).
`/jira` writes the card in Persian by default; set `card_language` in the conf for another language.
