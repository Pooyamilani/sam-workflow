# /ctx

Load the minimum context needed for the current task. Never scan the whole repo.

1. Read `.claude/skills/project/SKILL.md` and any project skill it points to for this area.
2. From its doc routing table, read only the relevant `docs/en/*.md` chapter(s).
3. Locate code with grep/rg. Use `graphify path`/`explain` only for "what depends on X"
   questions that span many files.
4. Inspect only the source files the above point to.
5. Report a short context summary: subsystem, files, docs consulted. No dumps.
