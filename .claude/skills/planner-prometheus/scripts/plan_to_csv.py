#!/usr/bin/env python3
"""Convert weekly-plan.json or daily-plan.json into a scheduler-friendly CSV (one row per post).

Usage: python3 plan_to_csv.py output/<slug>/<date>/weekly-plan.json [--out weekly-plan.csv]
Accepts {"slots":[...]} or a bare list of slots. Standard library only.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

COLS = ["id", "date", "time", "timezone", "platform", "surface", "format", "pillar", "source_ids",
        "hook", "copy", "hashtags", "cta", "asset_type", "asset_refs", "alt_text", "kpi", "status"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("plan", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    data = json.loads(a.plan.read_text(encoding="utf-8"))
    slots = data.get("slots", data) if isinstance(data, dict) else data
    out = a.out or a.plan.with_suffix(".csv")
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for s in slots:
            asset = s.get("asset") or {}
            w.writerow({**{k: s.get(k, "") for k in COLS},
                        "source_ids": " ".join(s.get("source_ids", [])),
                        "hashtags": " ".join(s.get("hashtags", [])),
                        "asset_type": asset.get("type", ""),
                        "asset_refs": " ".join(asset.get("refs", []))})
    print(f"wrote {len(slots)} rows to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
