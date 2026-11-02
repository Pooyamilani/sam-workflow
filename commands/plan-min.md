# /plan-min

Produce a minimal implementation plan. Do not implement. Do not explore broadly.

1. Identify the affected area from `.claude/skills/project/SKILL.md` (and any skill it
   says to read for that area, e.g. a theming skill).
2. Read only the relevant `docs/en/*` chapter(s) and the necessary source files.
   Grep every caller of anything you plan to change.
3. Output a concise plan: affected files, approach, risks, validation steps
   (use the project skill's Validate commands). Keep it short.
