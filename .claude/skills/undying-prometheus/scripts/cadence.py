#!/usr/bin/env python3
"""Undying Prometheus cadence engine: applies the Doubling Law.

Reads research.json (prometheus.research.v1) or a bare {"competitors": [...]} file and
writes undying.json (prometheus.undying.v1):

{
  "contract": "prometheus.undying.v1",
  "generated_at": "YYYY-MM-DD",
  "multiplier": 2.0,
  "benchmark_mode": "leader",
  "platforms": {
    "<platform>": {
      "benchmark_competitor": "Rival A" | null,
      "benchmark_posts_per_week": 14.0,
      "empty_arena": false,
      "target_posts_per_week": 28,
      "target_posts_per_day": 4.0,
      "surface_mix": {"reel": 21, "carousel": 7},          # posts per week per surface
      "share_of_voice_estimate": 0.41,
      "share_of_attention": 0.3,
      "priority_arena": true,
      "competitors_tracked": 3
    }
  },
  "totals": {"posts_per_week": 140, "posts_per_day": 20.0, "engagement_actions_per_day": 40},
  "notes": ["..."]
}

Standard library only. Usage:
  python3 cadence.py --input research.json --out undying.json [--multiplier 2] [--benchmark leader|top3|average]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import sys
from pathlib import Path

PLATFORMS = ["linkedin", "facebook", "instagram", "tiktok", "x", "bluesky", "youtube", "telegram"]

FLOORS = {"linkedin": 5, "facebook": 7, "instagram": 10, "tiktok": 14,
          "x": 21, "bluesky": 14, "youtube": 7, "telegram": 7}

# (surface, safe max per day) in fill order. Keep in sync with references/volume-science.md
DEFAULT_SURFACES = {
    "linkedin": [("feed_post", 2), ("document_carousel", 1), ("short_video", 1), ("article", 0.3)],
    "facebook": [("reel", 3), ("feed_post", 3), ("story", 6), ("group_post", 2)],
    "instagram": [("reel", 3), ("carousel", 2), ("story", 10), ("broadcast", 3)],
    "tiktok": [("video", 5), ("photo_carousel", 3), ("story", 5)],
    "x": [("post", 15), ("thread", 2)],
    "bluesky": [("post", 15), ("thread", 2)],
    "youtube": [("short", 4), ("long_form", 0.5), ("community_post", 2), ("live", 0.3)],
    "telegram": [("channel_post", 6), ("poll", 1), ("story", 3)],
}

# Preferred share of the weekly target per surface before ceilings apply (variety, not just fill order).
DEFAULT_SPLIT = {
    "linkedin": {"feed_post": 0.55, "document_carousel": 0.25, "short_video": 0.15, "article": 0.05},
    "facebook": {"reel": 0.45, "feed_post": 0.35, "story": 0.15, "group_post": 0.05},
    "instagram": {"reel": 0.5, "carousel": 0.35, "story": 0.0, "broadcast": 0.15},
    "tiktok": {"video": 0.75, "photo_carousel": 0.25, "story": 0.0},
    "x": {"post": 0.85, "thread": 0.15},
    "bluesky": {"post": 0.85, "thread": 0.15},
    "youtube": {"short": 0.7, "long_form": 0.1, "community_post": 0.2, "live": 0.0},
    "telegram": {"channel_post": 0.8, "poll": 0.15, "story": 0.05},
}


def load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def benchmark(values: list[tuple[str, float]], mode: str) -> tuple[str | None, float]:
    if not values:
        return None, 0.0
    ranked = sorted(values, key=lambda v: v[1], reverse=True)
    if mode == "leader":
        return ranked[0]
    if mode == "top3":
        top = ranked[:3]
        return "mean(top3: " + ", ".join(n for n, _ in top) + ")", sum(v for _, v in top) / len(top)
    if mode == "average":
        return "mean(all)", sum(v for _, v in ranked) / len(ranked)
    raise ValueError(f"unknown benchmark mode {mode}")


def surface_mix(platform: str, weekly: int) -> dict[str, int]:
    surfaces = DEFAULT_SURFACES[platform]
    split = DEFAULT_SPLIT[platform]
    caps = {s: math.floor(cap * 7) for s, cap in surfaces}
    mix = {s: 0 for s, _ in surfaces}
    # first pass: preferred split, bounded by caps
    for s, _ in surfaces:
        mix[s] = min(caps[s], round(weekly * split.get(s, 0)))
    remaining = weekly - sum(mix.values())
    # overflow pass: fill in order up to caps
    for s, _ in surfaces:
        if remaining <= 0:
            break
        room = caps[s] - mix[s]
        add = min(room, remaining)
        mix[s] += add
        remaining -= add
    if remaining > 0:  # above every ceiling: push onto the first surface, flagged by caller
        first = surfaces[0][0]
        mix[first] += remaining
    if remaining < 0:  # rounding overshoot: trim from the largest surface
        largest = max(mix, key=mix.get)
        mix[largest] += remaining
    return {k: v for k, v in mix.items() if v > 0}


def run(data: dict, multiplier: float, mode: str) -> dict:
    if multiplier < 2.0:
        raise SystemExit("Doubling Law: multiplier must be >= 2.0")
    competitors = data.get("competitors", [])
    channels = data.get("audience_channels", {}) or {}
    category = data.get("category_activity", {}) or {}
    notes: list[str] = []
    out_platforms: dict[str, dict] = {}

    for p in PLATFORMS:
        vals: list[tuple[str, float]] = []
        for c in competitors:
            stats = (c.get("platforms") or {}).get(p) or {}
            ppw = stats.get("posts_per_week")
            if isinstance(ppw, (int, float)) and ppw > 0:
                vals.append((c.get("name", c.get("id", "?")), float(ppw)))
        name, bench = benchmark(vals, mode)
        empty = bench == 0
        if empty:
            target = FLOORS[p]
            notes.append(f"{p}: no tracked competitor activity, so it is an empty arena. Using floor {target}/wk (first-mover land grab).")
        else:
            target = max(math.ceil(bench * multiplier), FLOORS[p])  # never below the platform floor
        mix = surface_mix(p, target)
        ceiling_week = sum(math.floor(cap * 7) for _, cap in DEFAULT_SURFACES[p])
        if target > ceiling_week:
            notes.append(f"{p}: target {target}/wk exceeds all safe surface ceilings ({ceiling_week}/wk). "
                         "Volume is kept (Doubling Law) but the excess is flagged for quality review.")
        others = sum(v for _, v in vals)
        sov = target / (target + others) if (target + others) else 1.0
        soa = (channels.get(p) or {}).get("share_of_attention")
        priority = bool(soa is not None and soa >= 0.15 and (empty or bench <= 7))
        out_platforms[p] = {
            "benchmark_competitor": name,
            "benchmark_posts_per_week": round(bench, 2),
            "empty_arena": empty,
            "target_posts_per_week": int(target),
            "target_posts_per_day": round(target / 7, 2),
            "surface_mix": mix,
            "share_of_voice_estimate": round(sov, 3),
            "share_of_attention": soa,
            "priority_arena": priority,
            "competitors_tracked": len(vals),
            "category_user_posts_per_week": (category.get(p) or {}).get("user_posts_per_week_estimate"),
        }

    total_week = sum(v["target_posts_per_week"] for v in out_platforms.values())
    per_day = total_week / 7
    return {
        "contract": "prometheus.undying.v1",
        "generated_at": dt.date.today().isoformat(),
        "multiplier": multiplier,
        "benchmark_mode": mode,
        "platforms": out_platforms,
        "totals": {
            "posts_per_week": total_week,
            "posts_per_day": round(per_day, 2),
            "engagement_actions_per_day": max(10, math.ceil(2 * per_day)),
        },
        "notes": notes,
    }


def print_table(result: dict) -> None:
    print(f"{'platform':<10} {'leader':<22} {'bench/wk':>8} {'target/wk':>9} {'per day':>7}  SoV   mix")
    for p, v in result["platforms"].items():
        leader = (v["benchmark_competitor"] or "(empty arena)")[:22]
        mix = ", ".join(f"{k}:{n}" for k, n in v["surface_mix"].items())
        print(f"{p:<10} {leader:<22} {v['benchmark_posts_per_week']:>8} {v['target_posts_per_week']:>9} "
              f"{v['target_posts_per_day']:>7}  {v['share_of_voice_estimate']:.2f}  {mix}")
    t = result["totals"]
    print(f"TOTAL {t['posts_per_week']}/wk = {t['posts_per_day']}/day · engagement actions/day: {t['engagement_actions_per_day']}")
    for n in result["notes"]:
        print("note:", n)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--multiplier", type=float, default=2.0)
    ap.add_argument("--benchmark", choices=["leader", "top3", "average"], default="leader")
    args = ap.parse_args(argv)
    result = run(load(args.input), args.multiplier, args.benchmark)
    print_table(result)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
