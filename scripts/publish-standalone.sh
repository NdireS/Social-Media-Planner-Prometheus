#!/usr/bin/env bash
# Publish this folder as its own public GitHub repo: Social-Media-Planner-Prometheus
# Requires the GitHub CLI (gh) logged in as the repo owner.
# Usage: bash scripts/publish-standalone.sh [owner]
set -euo pipefail
OWNER="${1:-NdireS}"
NAME="Social-Media-Planner-Prometheus"
SRC="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
cp -a "$SRC/." "$TMP/"
cd "$TMP"
rm -rf .git
git init -b main
git add -A
git commit -m "Social Media Planner: Prometheus v1.0 (five skills + orchestrator)"
gh repo create "$OWNER/$NAME" --public \
  --description "Five cooperating Claude skills that research a market and produce a 7-day, 8-platform social media plan" \
  --source . --push
echo "Published: https://github.com/$OWNER/$NAME"
