#!/usr/bin/env bash
# Pull the latest sam-workflow and install it into ~/.claude without deleting anything.
# Files that differ are backed up to ~/.claude/.sam-workflow-backups/<timestamp>/ first.
set -euo pipefail
cd "$(dirname "$0")"
git pull --ff-only
C=~/.claude; B=$C/.sam-workflow-backups/$(date +%Y%m%d-%H%M%S)
for f in $(find skills agents commands -type f); do
  if [ -e "$C/$f" ] && ! cmp -s "$f" "$C/$f"; then mkdir -p "$B/$(dirname "$f")"; cp -a "$C/$f" "$B/$f"; fi
  mkdir -p "$C/$(dirname "$f")"; cp "$f" "$C/$f"
done
[ -e "$C/sam-models.conf" ] || cp sam-models.conf.example "$C/sam-models.conf"
cp sam-models-sync.py "$C/" && chmod +x "$C/sam-models-sync.py" && "$C/sam-models-sync.py"
[ -d "$B" ] && echo "replaced files backed up to $B" || echo "no local files were replaced"
