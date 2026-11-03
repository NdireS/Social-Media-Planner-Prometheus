#!/usr/bin/env bash
# Smoke test for the deterministic parts of the pipeline, using synthetic sample data.
set -euo pipefail
cd "$(dirname "$0")/.."
T="$(mktemp -d)"
python3 .claude/skills/suggester-prometheus/scripts/score.py --validate examples/sample-research.json
python3 .claude/skills/undying-prometheus/scripts/cadence.py --input examples/sample-research.json --out "$T/undying.json"
python3 .claude/skills/suggester-prometheus/scripts/score.py --research examples/sample-research.json --undying "$T/undying.json" --out "$T/suggester.json"
python3 .claude/skills/planner-prometheus/scripts/render_posters.py --spec examples/sample-posters.json --brand brand/brand.example.json --out "$T/posters"
echo "selftest OK, outputs in $T"
