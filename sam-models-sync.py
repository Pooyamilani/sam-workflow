#!/usr/bin/env python3
"""Apply ~/.claude/sam-models.conf to the sam-task skill + agent frontmatter."""
import re
from pathlib import Path

home = Path.home() / ".claude"
files = {"orchestrator": home / "skills/sam-task/SKILL.md"}
for line in (home / "sam-models.conf").read_text().splitlines():
    parts = line.split("#")[0].split()
    if not parts:
        continue
    if parts[0] == "browser":  # read at runtime by the skills, not synced
        if len(parts) != 2 or parts[1] not in ("auto", "builtin", "chrome", "playwright", "devtools"):
            raise SystemExit(f"sam-models.conf: bad browser line: {line!r}")
        continue
    if parts[0] in ("jira", "gitlab"):  # how to reach it: browser (default) or mcp
        if len(parts) != 2 or parts[1] not in ("browser", "mcp"):
            raise SystemExit(f"sam-models.conf: bad {parts[0]} line: {line!r}")
        continue
    if parts[0] in ("ticket_prefix", "jira_url", "card_language"):  # read at runtime by the skills
        continue
    if len(parts) != 3:
        raise SystemExit(f"sam-models.conf: bad line: {line!r}")
    role, model, effort = parts
    path = files.get(role, home / f"agents/sam-{role}.md")
    if not path.exists():
        raise SystemExit(f"sam-models.conf: no file for role {role!r} ({path})")
    text = path.read_text()
    head, sep, body = text.partition("\n---\n")  # frontmatter only
    for key, val in (("model", model), ("effort", effort)):
        head, n = re.subn(rf"^{key}: .*$", f"{key}: {val}", head, flags=re.M)
        if not n:
            head = head.replace("---\n", f"---\n{key}: {val}\n", 1)
    new = head + sep + body
    if new != text:
        path.write_text(new)
        print(f"{role}: {model} / {effort}")
