# /debug

Debug from evidence, not repo-wide exploration.

```
failure → affected subsystem (SKILL.md) → graphify (path/explain/query)
  → relevant execution path → relevant source → hypothesis → verification
  → minimal fix → regression test
```

Do not refactor while debugging unless the fix requires it. Do not inspect files outside
the identified execution path. Report root cause and fix concisely.
