# /implement

Implement the requested change with minimum context and minimum diff.

- Reuse existing patterns/utilities named in `.claude/skills/project/SKILL.md` before
  writing new code; read any area skill it points to (e.g. a theming skill).
- No speculative abstractions, no unrelated refactoring, no new dependencies unless asked.
- Keep the diff small and preserve existing behavior.

After implementing:
1. Review the diff (`git diff`) and strip anything not required.
2. Run the narrowest validation from the project skill (types, lint, relevant tests).
   Logic fix (calculations, sync, dates, parsing)? Leave one small jest test that fails
   without the fix. Pure UI tweaks need none.
3. Frontend/stateful UI change? Verify in the real browser with the `browser-test` skill
   (invariants, sequences, non-default state), not just lint/types.
4. Report only what changed and the validation result. No verbose narration.
