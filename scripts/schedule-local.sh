#!/usr/bin/env bash
# Install local cron jobs that run Prometheus headlessly with the Claude Code CLI.
#   daily  : /prometheus-daily at schedule.daily_time (local machine time)
#   weekly : /prometheus on schedule.weekly_day
# Usage: bash scripts/schedule-local.sh [--remove]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$REPO/prometheus.config.yaml"
TAG="# prometheus-social-planner"
CLAUDE_BIN="$(command -v claude || true)"

if [[ "${1:-}" == "--remove" ]]; then
  crontab -l 2>/dev/null | grep -v "$TAG" | crontab - && echo "Removed Prometheus cron entries."
  exit 0
fi
[[ -z "$CLAUDE_BIN" ]] && { echo "Claude Code CLI not found. Install it from https://code.claude.com first."; exit 1; }
[[ -f "$CONFIG" ]] || { echo "Missing $CONFIG. Copy prometheus.config.example.yaml first."; exit 1; }

read_cfg() { python3 - "$CONFIG" "$1" <<'PY'
import sys, yaml
cfg = yaml.safe_load(open(sys.argv[1])) or {}
print((cfg.get("schedule") or {}).get(sys.argv[2], ""))
PY
}
DAILY="$(read_cfg daily_time)"; DAILY="${DAILY:-06:30}"
WEEKLY="$(read_cfg weekly_day)"; WEEKLY="${WEEKLY:-sunday}"
H="${DAILY%%:*}"; M="${DAILY##*:}"
declare -A DOW=([sunday]=0 [monday]=1 [tuesday]=2 [wednesday]=3 [thursday]=4 [friday]=5 [saturday]=6)
WD="${DOW[${WEEKLY,,}]:-0}"
mkdir -p "$REPO/output/logs"
TOOLS='--allowedTools "WebSearch,WebFetch,Read,Write,Edit,Glob,Grep,Bash,Task,Skill"'
DAILY_JOB="$((10#$M)) $((10#$H)) * * * cd $REPO && $CLAUDE_BIN -p '/prometheus-daily' $TOOLS >> output/logs/daily.log 2>&1 $TAG"
WEEKLY_H=$(( (10#$H + 23) % 24 ))   # one hour before the daily run (approx.; adjust if needed)
WEEKLY_JOB="$((10#$M)) $WEEKLY_H * * $WD cd $REPO && $CLAUDE_BIN -p '/prometheus' $TOOLS >> output/logs/weekly.log 2>&1 $TAG"
( crontab -l 2>/dev/null | grep -v "$TAG"; echo "$DAILY_JOB"; echo "$WEEKLY_JOB" ) | crontab -
echo "Installed:"; crontab -l | grep "$TAG"
