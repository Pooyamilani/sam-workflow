---
name: sam-task
model: opus
effort: medium
description: End-to-end Jira card workflow - investigate the card in the browser, plan, create the branch, implement after approval, live-test in the browser, commit after approval, then write the Jira card + MR content, and on request push + create the GitLab merge request (title, description, reviewers) and put its link on the Jira card. Use when the user gives a Jira URL/key (e.g. PROJ-1234) and says "work on", "investigate", "pick up" or "/sam-task". Arg: Jira URL or key, optional phase to resume from (plan | implement | review | test | commit | jira | mr).
---

# Jira task workflow

Arg: `<jira-url-or-key> [phase]`. With no phase given, start at phase 1. With a phase, resume there.
Read the project skill (`.claude/skills/project/SKILL.md`) first. Its rules beat this file's defaults.

**One session per card.** This session (the orchestrator) does investigation and planning itself, and delegates the rest to
subagents: implement → review → test → commit + Jira. It stays the only one talking to the user. Never suggest a new session for a phase.
Models/effort per role: `~/.claude/sam-models.conf` (synced into each file's frontmatter at session start).
Pass every subagent the card key and plan path; they don't see this conversation.

There are **three hard stops**, marked ⛔. At each one, end the turn and wait for an explicit yes.

## 1. Investigate the card (browser or MCP)

- Read `jira` and `gitlab` in `~/.claude/sam-models.conf` (missing → `browser`). `mcp` → use the Jira MCP (tools named `mcp__jira__*`,
  load via ToolSearch) to read the card, comments, links and attachments, and the GitLab MCP (`mcp__gitlab-mcp__*`) for linked MRs/branches.
  Tool missing or auth failing → say so in one line and fall back to the browser steps below. With `mcp`, the browser is only needed for testing.

- Open the card in the browser chosen per the `browser-test` skill, section 0 (`browser` in `~/.claude/sam-models.conf`). Given only a key, open `jira_url` (from the same conf) + the key. If the Jira login page shows up, ask the user to log in, wait, then continue. Never type credentials.
- Read everything: the title, type, description, acceptance criteria, environment/template, **all comments**, linked issues, and links inside comments.
  Follow a link or linked card when it changes how the card should be read.
- Attachments: look at every screenshot. For a video, ask the user to download it (or convert it to mp4) and tell you the path. Pull frames with
  `ffmpeg -i in.mp4 -vf fps=1 /tmp/.../f_%02d.png` and look at them. Say what the attachment shows that the text doesn't.
- If the card gives URLs or steps to reproduce, **reproduce the bug yourself in the browser** before you decide on the root cause.

## 2. Investigate the code

- Use the `docs/` the project skill points to, then the code (grep/rg; graphify only for cross-file "what depends on X").
- API involved? The API docs/OpenAPI are the source of truth. Never invent endpoints, DTOs or response shapes.
- Find the actual root cause, not the symptom. Grep every caller of the function you plan to change.
- Classify the issue as one of: bug, missing feature, API/data problem, template-specific, shared, or a misread report.
  The reporter's suggested fix is a hint, not the spec.
- Scope check: list which templates or apps the change reaches, and what has to stay the same.
  Consider state, routing, localization/RTL, responsive layout and auth where they apply.

## 3. Plan + branch ⛔

- Work out the branch name from `git branch -a` / `git log` merge commits (for example `PROJ-1234_short-kebab-summary`). Never invent a new pattern.
- Run `git status` first. If there is uncommitted work, stop and ask. Otherwise branch from the base branch in the project skill (default `develop`), after `git fetch` and a fast-forward.
- Report briefly:
  - **Problem:** what the card means.
  - **Root cause:** include the evidence (Jira, attachment, code `file:line`).
  - **Fix:** say why it fits the existing architecture.
  - **Files:** only ones you verified.
  - **Risks / what other templates are affected.**
  - **Validation plan.**
  - **Unknowns:** what is unproven and how implementation will verify it.
  - **The branch you created.**
- Save the plan to `.claude/plans/<KEY>.md` (gitignored), detailed enough that a fresh session can run
  `/sam-task <KEY> implement` without re-investigating. On resume, read that file first.
- ⛔ Stop. Don't implement until the user approves the plan. Then continue in this same session.

## Session hygiene

One session per card, covering all phases. When the user brings a different card or an unrelated tangent, suggest a new session for *that*.
Keep `.claude/plans/<KEY>.md` updated with what's done and what's left (it feeds the subagents and survives compaction).

## 4. Implement (subagent: `sam-implementer`)

- Spawn `sam-implementer` (foreground, `run_in_background: false`) with: card key, plan path, base branch, anything learned since the plan was written.
- If it reported a plan contradiction: re-investigate, update the plan, tell the user if the approach changed, then continue it via SendMessage.

## 4b. Review (subagent: `sam-reviewer`)

- Spawn `sam-reviewer` (foreground) with card key, plan path, implementer's summary.
- `changes needed`: send the findings to the same `sam-implementer` via SendMessage, then re-review. Max 2 loops, then ask the user.
  Drop findings you can show are wrong (say why).

## 5. Live test (subagent: `sam-browser-tester`)

- Spawn `sam-browser-tester` (foreground) with: card key, plan path, implementer's summary, the scope-check list of templates/apps,
  the invariants and real-user sequences to cover (e.g. zoom, then drag, then check zoom is kept).
- If it returns `BLOCKED` (login/OTP, app won't start): tell the user, wait, then resume the same agent with SendMessage.
- Failures: send them to the same `sam-implementer` (SendMessage to the same agent, so it keeps context), then re-run the tester. Max 2 loops, then stop and ask the user.
- Show the user the pass/fail table and key screenshots.

## 6. Commit ⛔ + 7. Jira/MR content (subagent: `sam-closer`)

- Spawn `sam-closer` (foreground) with card key, plan path, implementer summary, review verdict, test results table.
- ⛔ Show the user its diff summary and proposed commit message, then wait for approval.
- On approval, SendMessage the same `sam-closer`: `approved` (+ the user's edits to the message). It commits (no `Co-Authored-By`)
  and writes the Persian Jira card + MR content via `~/.claude/commands/jira.md`.
- Show its output to the user as-is (the card must stay in one copyable code block).
- Never push or force-push without asking. Pushing happens only in phase 8, after its own approval.

## 8. Merge request + Jira link ⛔ (orchestrator)

Runs after phase 7, only when the user says so ("MR", "create the merge request") or accepts your offer at the end of phase 7.
You do this yourself (the MCP tools and the browser are yours, not the subagents'). Follow the `jira` / `gitlab` modes from phase 1:
`gitlab mcp` → create the MR with the GitLab MCP tools (load via ToolSearch); `jira mcp` → write the link with the Jira MCP.
A mode set to `browser`, or an MCP tool that is missing or failing auth, means doing that step in the browser instead. Say so in one line.
Settings come from `~/.claude/sam-models.conf`: `gitlab_project`, `mr_reviewers`, `mr_target`, `jira_mr_field`.

1. **Resolve inputs.**
   - Project: `gitlab_project`, else derive from `git remote get-url origin` (path after the host, without `.git`).
   - Target: `mr_target`, else the project skill's base branch, else `develop`.
   - Source: the current branch (`BRANCH:` from the closer). Check it contains the card's commit.
   - Title and description: the closer's `MR_TITLE` and MR description, verbatim. English, GitLab Markdown.
   - Reviewers: `mr_reviewers` usernames → numeric ids via the GitLab `search` tool (users scope). If the conf is empty or a
     username can't be resolved, ask the user; never guess a reviewer. Don't set assignee unless asked.
   - Labels: only if the project skill names them (check with `search_labels`). Never invent labels.
2. **Check for an existing MR** for the source branch (GitLab MCP `list_merge_requests`, or the project's MR list in the browser). If one is open, reuse it and skip to step 4.
3. ⛔ Show the user: source → target, title, reviewers, and say that you will `git push -u origin <branch>` (plain push, never `--force`).
   Wait for an explicit yes. Then push, and `create_merge_request` with title, description, `reviewer_ids`, `source_branch`, `target_branch`.
   Keep the returned `web_url`. If the push or creation fails, report the error as is; do not retry with force.
4. **Put the link on the Jira card.** With the Jira MCP, set the card's merge-request field through whatever field-update tool it exposes
   and read the card back to confirm the link is there. Otherwise use the browser (same one as phase 1): open the card, find the field labelled `jira_mr_field`, paste the `web_url`, save, reload and confirm.
   If the login page appears, ask the user to log in and wait. If the field is missing or not editable, don't hunt for
   workarounds: give the user the URL and say which field was missing.
5. Report: MR link, reviewers set, and whether the Jira field now shows the link. Add the MR link to `.claude/plans/<KEY>.md`.
