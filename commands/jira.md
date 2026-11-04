---
description: Write a Jira card description in Persian summarizing this session's work
---

Write a Jira card in Persian summarizing the work done in this session.
(If `card_language` is set in `~/.claude/sam-models.conf`, write the card and test scenarios in that language instead, keeping the same structure and wiki markup.)

Audience: a mixed team — product owner, QA, and developers who do not know this
codebase. Focus on business impact, not implementation detail.

Structure it as:

1. **Card title** — one short line in Persian, business-facing (what changed for the
   user/business, not the technical mechanism).

2. **Description** — in Persian, business/user impact only: what the user or business
   could not do before, what they can do now, and why it matters. Avoid code
   identifiers, file names, module names, or implementation mechanics — write it so a
   product owner or QA with zero codebase knowledge fully understands the value.
   Prefer a bullet list, one line per distinct change, each phrased as a business
   outcome. If a change does not stand on its own as a bullet (needs context, is a
   caveat, or explains the "why" behind another bullet), keep it as a short
   descriptive sentence instead — before or after the list, wherever it reads best.
   Keep the whole thing tight — no padding, no restating the title.

   **Format for the card (title + description): Jira wiki markup, not Markdown.**
   It is pasted into the Jira "Text" tab, so output the card inside ONE fenced code block
   (so it can be copied as-is) and write it in wiki markup to get the visual styling:
   - Section headings: `h3. عنوان` (never `##`).
   - Status words: `{color:#157a4a}*(انجام شد)*{color}` for good/fixed,
     `{color:#b3261e}*(مشکل)*{color}` for problems/failures.
   - Colored panels for emphasis: `{panel:borderColor=#157a4a|bgColor=#e3f4ea}...{panel}`
     (green = done/working), `{panel:borderColor=#b3261e|bgColor=#fbe9e7}...{panel}`
     (red = error/risk), `{panel:borderColor=#1f5fd6|bgColor=#eef3fd}...{panel}`
     (blue = info, summary, action needed from someone).
   - Bullets: `* item`. Bold: `*text*`. Inline code/identifiers/IDs: `{{text}}`
     (text inside must not contain `}}`).
   - Comparisons or before/after/test results: a table with `||header||header||` and
     `|cell|cell|` rows. A literal pipe inside a cell must be written `\|`.
   - Raw errors, logs, responses: `{noformat}...{noformat}` (inside a red panel for errors).
     Commands/code/JSON: `{code:language=bash|title=...|collapse=true}...{code}`; use
     `collapse=true` for anything longer than ~15 lines. Put placeholders like `<TOKEN>`
     only inside code/noformat blocks.
   - Do not use Markdown syntax (`**`, `##`, backtick fences, `- ` bullets) inside the card.
   Use these only where they add clarity (one panel for the key outcome, a table only for
   real comparisons) — do not decorate everything. Mention in one line after the code
   block: "Paste in the Text tab, then switch to Visual".
   Branch names and the MR description stay outside the card block (MR description is
   GitLab Markdown, as specified below, and goes in its own fenced code block).

3. **Branch names** — a short English section (not in Persian, since branch names are
   written in English) with 3 suggestions, following the convention already used in
   this repository (check `git log`/`git branch` for the real pattern — e.g.
   `PROJ-1234_short-kebab-case-summary`). Use the ticket number from the current branch
   if one exists there; otherwise use a `<PREFIX>-XXXX` placeholder (prefix = `ticket_prefix` in `~/.claude/sam-models.conf`) rather than inventing a
   number. Show the structure clearly (e.g. `<TICKET>_<short-kebab-case-summary>`)
   before listing the 3 suggestions.

4. **MR description** — a separate section, in English (merge request descriptions are
   read by developers and reviewers, unlike the Persian card above). Unlike the card,
   this one IS technical: name real files, components, keys and commands. Use exactly
   these headings, in this order, as Markdown. Output the whole MR description inside ONE
   fenced code block tagged `markdown`, so it can be copied as-is into the GitLab
   description text box. Because the description contains inline backticks, open and
   close that block with a four-backtick fence (````markdown ... ````). Write GitLab
   Markdown only (`##` headings, `-` bullets, backticks for code); no Jira wiki markup:

   - Before the code block, one line: `MR title:` followed by the title in a one-line code span,
     English, same format as the commit subject (`fix(PROJ-1234): ...`), no trailing period.
   - `## Summary` — 1-2 sentences: what the MR adds/fixes and the visible result.
   - `## Technical Changes` — bullets: one per file or unit changed, with what changed
     and why (e.g. which existing helper/key/library was reused). Also note what did
     NOT need to change when that is relevant to a reviewer.
   - `## Affected Areas` — the app → module → page/feature path(s) touched.
   - `## Behavior` — what the user sees/does now, including the resulting URL or flow
     when there is one.
   - `## Validation` — the checks actually run in this session (exact command, app
     directory, result). State plainly what was NOT done (e.g. "Not tested manually in
     the browser. Lint was not run.") — never imply a check that did not happen.
   - `## Risk / Regression Considerations` — honest risk level and why, external
     dependencies or failure modes, and open questions for design/product.

   Example of the tone and level of detail (abridged):

   ```
   ## Summary
   Adds a "Compare products" button to the product page. Clicking it opens the compare
   page with the current product already in the first slot.

   ## Technical Changes
   - `product-info.view.tsx`: added a `Link` next to `SharePopover` pointing to
     `/compare?compare=<productInfo.id>`, using the existing icon library.
   - The compare page already reads `?compare=`, so no changes were needed there.

   ## Affected Areas
   - apps/web → module → pages/product

   ## Behavior
   A compare icon now shows in the product info header. Clicking it goes to
   `/{locale}/compare?compare={id}` with this product in slot 1.

   ## Validation
   - `npx tsc --noEmit -p .`: no errors in the changed file.
   - Not tested manually in the browser. Lint was not run.

   ## Risk / Regression Considerations
   - Low. One additive UI element, only in one theme.
   - The button is icon-only; design may want a labelled button.
   ```

5. **سناریوهای تست** — a separate section in Persian, for QA, pasted into Jira too, so it
   uses the same Jira wiki markup as the card (inside its own fenced code block, same
   rules and restraint as above; paste in the Text tab, then switch to Visual).
   - Start with `h3. سناریوهای تست`.
   - Main body: one table with `||#||سناریو||مراحل||نتیجه مورد انتظار||` and one row per
     scenario. Steps are short, numbered with `#` only if the cell stays readable;
     otherwise one sentence. Cover the normal path, the edge case this work fixes, and
     any neighbouring flow that could regress (e.g. online vs offline, empty vs filled
     input).
   - Use `{color:#157a4a}*(قبول)*{color}` / `{color:#b3261e}*(رد)*{color}` only in a
     separate result column when a scenario was actually run in this session; never mark
     a scenario as passed that was not run. Scenarios not run get no status.
   - Put preconditions (test data, environment, login, online/offline state) in a blue
     panel above the table: `{panel:borderColor=#1f5fd6|bgColor=#eef3fd}...{panel}`.
   - Known limits or things QA must not expect to work (e.g. a backend dependency) go in
     a red panel below the table.
   - Written in business/QA language: what to click and what to see, no file names or
     code identifiers (except inline `{{field names}}` QA actually sees on screen or in
     the network tab).

Rules:
- Summarize what was actually built and verified in this session — not the plan, not
  what the diff might imply.
- Do not invent ticket numbers, dates, effort estimates, or reviewer names.
- Branch names must describe the same work as the description — no scope that was not
  actually done in this session.
- The MR description must follow the same honesty rules: only what was built and
  verified in this session, and Validation must list only checks actually run.
- Output the title, description paragraph, branch names, MR title + description, and test scenarios sections only — no
  preamble, no "here's your card". The only extra line allowed is the one-line "Paste in the
  Text tab, then switch to Visual" note after the card's code block.

$ARGUMENTS
