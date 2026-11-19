#!/usr/bin/env bash
# Vendor skills from upstream repos listed in scripts/upstreams.conf into skills/<name>/.
# Upstream stays canonical. Never hand-edit vendored folders; change upstream, then re-run.
#
# Usage: scripts/sync-upstream.sh            # sync all
#        scripts/sync-upstream.sh data-warrior [local-clone-path]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="$ROOT/scripts/upstreams.conf"
ONLY="${1:-}"; LOCAL="${2:-}"

sync_one() {
  local name="$1" url="$2" sub="$3" extras="$4" src tmp="" dest="$ROOT/skills/$1"
  if [[ -n "$LOCAL" ]]; then src="$LOCAL"; else
    tmp="$(mktemp -d)"; git clone --quiet --depth 1 "$url" "$tmp/src"; src="$tmp/src"; fi
  local commit; commit="$(git -C "$src" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  rm -rf "$dest"; mkdir -p "$dest"
  # copy every folder that contains a SKILL.md (keeps bucket nesting)
  (cd "$src/$sub" && find . -name SKILL.md -not -path './.git/*' -not -path './.*/*' -print0 \
     | while IFS= read -r -d '' f; do d="$(dirname "$f")"; mkdir -p "$dest/$d"; cp -R "$d/." "$dest/$d/"; done)
  # bucket README files (data-warrior groups skills in ring folders)
  (cd "$src/$sub" && find . -mindepth 2 -maxdepth 2 -name README.md -not -path './.*/*' -print0 \
     | while IFS= read -r -d '' f; do mkdir -p "$dest/$(dirname "$f")"; cp "$f" "$dest/$f"; done)
  for e in $extras; do [[ -f "$src/$e" ]] && cp "$src/$e" "$dest/$(basename "$e")"; done
  cat > "$dest/UPSTREAM.md" <<MD
# Upstream: $name

Vendored from $url at commit \`$commit\` on $(date -u +%Y-%m-%d).
Do not edit files here. Change them upstream and run \`scripts/sync-upstream.sh $name\`.
License: see LICENSE in this folder.
MD
  [[ -n "$tmp" ]] && rm -rf "$tmp"
  echo "$name: $(find "$dest" -name SKILL.md | wc -l | tr -d ' ') skills from $commit"
}

grep -v '^\s*#' "$CONF" | grep -v '^\s*$' | while IFS='|' read -r name url sub extras; do
  name="$(echo $name)"; url="$(echo $url)"; sub="$(echo $sub)"; extras="$(echo $extras)"
  [[ -n "$ONLY" && "$ONLY" != "$name" ]] && continue
  sync_one "$name" "$url" "$sub" "$extras"
done
