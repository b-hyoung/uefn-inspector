#!/usr/bin/env bash
# Install the uefn-* slash skills into ~/.claude/skills so they load in Claude Code.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)/game-loop-kit/skills"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
KIT="$(cd "$(dirname "$0")" && pwd)/game-loop-kit"

mkdir -p "$DEST"
for s in uefn-game-loop uefn-intake uefn-level uefn-review; do
  mkdir -p "$DEST/$s"
  # rewrite the KIT path so the skills point at THIS clone
  sed "s#^\*\*KIT\*\* = .*#**KIT** = \`$KIT\`#" "$SRC/$s/SKILL.md" > "$DEST/$s/SKILL.md"
  echo "installed: /$s"
done
echo
echo "done -> $DEST"
echo "restart Claude Code (or open a new session) to load them."
