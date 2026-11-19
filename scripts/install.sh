#!/usr/bin/env bash
# Install skills from this repo into a project or your user profile.
#
#   scripts/install.sh [--tool claude|cursor|codex] (--target <project> | --global)
#                      [--skills all|docs,warrior,gordonmurray] [--symlink]
#
# --tool claude (default) installs to .claude/skills, which BOTH Claude Code and
#   Cursor read. Use --tool cursor for .cursor/skills only, --tool codex for
#   .agents/skills. Do not install the same skills for two tools that Cursor
#   reads, or Cursor will list them twice.
# --skills picks which sets: docs = data-architecture-docs, warrior = The Data
#   Warrior, gordonmurray = Iceberg/Flink/Paimon/etc. Default: all.
# --symlink links instead of copying, so `git pull` here updates the install.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="claude"; TARGET=""; GLOBAL=0; SETS="all"; LINK=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tool) TOOL="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --global) GLOBAL=1; shift ;;
    --skills) SETS="$2"; shift 2 ;;
    --symlink) LINK=1; shift ;;
    -h|--help) sed -n 2,16p "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done

if [[ $GLOBAL -eq 1 && -n "$TARGET" ]] || [[ $GLOBAL -eq 0 && -z "$TARGET" ]]; then
  echo "Give exactly one of --target <project> or --global" >&2; exit 2
fi

case "$TOOL" in
  claude) PROJ=".claude/skills"; USERDIR="$HOME/.claude/skills" ;;
  cursor) PROJ=".cursor/skills"; USERDIR="$HOME/.cursor/skills" ;;
  codex)  PROJ=".agents/skills"; USERDIR="$HOME/.codex/skills" ;;
  *) echo "--tool must be claude, cursor or codex" >&2; exit 2 ;;
esac
if [[ $GLOBAL -eq 1 ]]; then DEST="$USERDIR"; else
  [[ -d "$TARGET" ]] || { echo "Target not found: $TARGET" >&2; exit 2; }
  DEST="$(cd "$TARGET" && pwd)/$PROJ"
fi

declare -a FOLDERS=()
[[ "$SETS" == "all" ]] && SETS="docs,warrior,gordonmurray"
IFS=',' read -ra PICK <<< "$SETS"
for s in "${PICK[@]}"; do
  case "$s" in
    docs) FOLDERS+=("data-architecture-docs") ;;
    warrior) FOLDERS+=("data-warrior") ;;
    gordonmurray) FOLDERS+=("gordonmurray") ;;
    *) echo "Unknown skill set: $s" >&2; exit 2 ;;
  esac
done

mkdir -p "$DEST"
for f in "${FOLDERS[@]}"; do
  src="$ROOT/skills/$f"; dst="$DEST/$f"
  [[ -d "$src" ]] || { echo "Missing $src (run scripts/sync-upstream.sh?)" >&2; exit 1; }
  rm -rf "$dst"
  if [[ $LINK -eq 1 ]]; then ln -s "$src" "$dst"
  else cp -RL "$src" "$dst"; fi    # -L: resolve reviewers/ and contracts/ links into real files
  n=$(find -L "$dst" -name SKILL.md | wc -l | tr -d ' ')
  echo "Installed $f ($n skills) -> $dst"
done
echo "Done. Restart or reload your agent so it picks up the skills."
