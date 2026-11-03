#!/usr/bin/env bash
# Install Prometheus skills so they appear in Claude Code's "/" menu in EVERY project.
#
#   bash scripts/install-skills.sh                      # all 7 skills -> ~/.claude/skills
#   bash scripts/install-skills.sh researcher outlier   # only the ones you name
#   bash scripts/install-skills.sh --project ~/my-repo undying   # into another repo's .claude/skills
#   bash scripts/install-skills.sh --uninstall          # remove them
#
# Short names: researcher undying suggester outlier planner prometheus prometheus-daily
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)/.claude/skills"
DEST="$HOME/.claude/skills"; UNINSTALL=0; PICK=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) DEST="$(cd "$2" && pwd)/.claude/skills"; shift 2 ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) PICK+=("$1"); shift ;;
  esac
done
ALL=(researcher-prometheus undying-prometheus suggester-prometheus outlier-prometheus planner-prometheus prometheus prometheus-daily)
resolve() { case "$1" in prometheus|prometheus-daily|*-prometheus) echo "$1" ;; *) echo "$1-prometheus" ;; esac; }
SKILLS=()
if [[ ${#PICK[@]} -eq 0 ]]; then SKILLS=("${ALL[@]}"); else for p in "${PICK[@]}"; do SKILLS+=("$(resolve "$p")"); done; fi
# the one-call pipeline needs the five building blocks
for s in "${SKILLS[@]}"; do
  if [[ "$s" == prometheus || "$s" == prometheus-daily ]] && [[ $UNINSTALL -eq 0 ]]; then
    for dep in researcher-prometheus undying-prometheus suggester-prometheus outlier-prometheus planner-prometheus; do
      [[ " ${SKILLS[*]} " == *" $dep "* ]] || SKILLS+=("$dep")
    done
  fi
done
mkdir -p "$DEST"
for s in "${SKILLS[@]}"; do
  [[ -d "$SRC/$s" ]] || { echo "unknown skill: $s"; exit 1; }
  rm -rf "${DEST:?}/$s"
  if [[ $UNINSTALL -eq 1 ]]; then echo "removed  /$s"; else cp -R "$SRC/$s" "$DEST/$s"; echo "installed /$s -> $DEST/$s"; fi
done
[[ $UNINSTALL -eq 1 ]] || echo "Done. Restart Claude Code (or open a new session), then type / to see them."
