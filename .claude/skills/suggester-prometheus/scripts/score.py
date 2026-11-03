#!/usr/bin/env python3
"""Suggester Prometheus scoring model.

Turns research.json (prometheus.research.v1) + undying.json (prometheus.undying.v1)
into a ranked, weighted opportunity model (suggester.json, prometheus.suggester.v1).

Model
-----
Pain-point score (0-100) =
    100 * ( w_freq*F + w_int*I + w_gap*G + w_status*S + w_rel*R + w_conf*C )
  F = log(1+mentions) / log(1+max_mentions)          frequency, log-normalised
  I = intensity / 5                                  emotional intensity
  G = 1 - competitor_coverage                        white space
  S = status weight {ignored 1.0, unsolved .9, partially_solved .6, solved .2}
  R = relevance to the business's service
  C = min(1, evidence_sources / 5)                   confidence

Trend score (0-100) =
    100 * ( w_vel*V + w_rel*R + w_aud*A + w_sat*(1-saturation) + w_conf*C )
  V = velocity weight {rising 1.0, peak .6, declining .2}

Robustness: Monte-Carlo perturbation of every weight by +/-25 % (N runs, fixed seed),
re-ranking pain points and trends together. k = min(--top, n // 2).
For each item we report p_top_k = probability it stays in the top-k, and its mean rank, so the
Suggester knows which recommendations are robust and which depend on the weighting.

Platform allocation: undying target posts/week per platform x pillar share,
where pillar share is proportional to the summed scores of the items in that pillar.

Usage:
  python3 score.py --research research.json --undying undying.json --out suggester.json [--top 10] [--runs 500]
  python3 score.py --validate research.json
Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

PLATFORMS = ["linkedin", "facebook", "instagram", "tiktok", "x", "bluesky", "youtube", "telegram"]
STATUS_W = {"ignored": 1.0, "unsolved": 0.9, "partially_solved": 0.6, "solved": 0.2}
VELOCITY_W = {"rising": 1.0, "peak": 0.6, "declining": 0.2}

PAIN_WEIGHTS = {"freq": 0.25, "int": 0.20, "gap": 0.20, "status": 0.15, "rel": 0.15, "conf": 0.05}
TREND_WEIGHTS = {"vel": 0.30, "rel": 0.25, "aud": 0.20, "sat": 0.15, "conf": 0.10}


def clamp01(x, default=0.5) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, x))


# --------------------------------------------------------------------------- validation
def validate(research: dict) -> list[str]:
    errs: list[str] = []
    for key in ("business", "competitors", "pain_points", "trends", "persona"):
        if key not in research:
            errs.append(f"missing top-level key '{key}'")
    for i, p in enumerate(research.get("pain_points", [])):
        for k in ("id", "statement", "status", "mentions", "intensity", "competitor_coverage", "relevance"):
            if k not in p:
                errs.append(f"pain_points[{i}] missing '{k}'")
        if p.get("status") not in STATUS_W:
            errs.append(f"pain_points[{i}].status '{p.get('status')}' not in {list(STATUS_W)}")
        if not isinstance(p.get("intensity"), (int, float)) or not 1 <= p.get("intensity", 0) <= 5:
            errs.append(f"pain_points[{i}].intensity must be 1-5")
    for i, t in enumerate(research.get("trends", [])):
        for k in ("id", "name", "velocity"):
            if k not in t:
                errs.append(f"trends[{i}] missing '{k}'")
        if t.get("velocity") not in VELOCITY_W:
            errs.append(f"trends[{i}].velocity '{t.get('velocity')}' not in {list(VELOCITY_W)}")
    for i, c in enumerate(research.get("competitors", [])):
        for pl in (c.get("platforms") or {}):
            if pl not in PLATFORMS and pl not in ("reddit", "blog", "newsletter", "podcast", "threads", "pinterest"):
                errs.append(f"competitors[{i}].platforms has unknown key '{pl}'")
    return errs


# --------------------------------------------------------------------------- features
def pain_features(pains: list[dict]) -> list[dict]:
    max_m = max([p.get("mentions", 0) or 0 for p in pains] + [1])
    feats = []
    for p in pains:
        m = max(0, p.get("mentions", 0) or 0)
        feats.append({
            "freq": math.log1p(m) / math.log1p(max_m),
            "int": clamp01((p.get("intensity", 3) or 3) / 5),
            "gap": 1 - clamp01(p.get("competitor_coverage"), 0.5),
            "status": STATUS_W.get(p.get("status"), 0.5),
            "rel": clamp01(p.get("relevance"), 0.5),
            "conf": min(1.0, len(p.get("evidence", []) or []) / 5),
        })
    return feats


def trend_features(trends: list[dict]) -> list[dict]:
    return [{
        "vel": VELOCITY_W.get(t.get("velocity"), 0.5),
        "rel": clamp01(t.get("relevance"), 0.5),
        "aud": clamp01(t.get("audience_overlap"), 0.5),
        "sat": 1 - clamp01(t.get("competitor_saturation"), 0.5),
        "conf": min(1.0, len(t.get("evidence", []) or []) / 5),
    } for t in trends]


def score(feats: list[dict], weights: dict) -> list[float]:
    total = sum(weights.values())
    return [100 * sum(weights[k] * f[k] for k in weights) / total for f in feats]


def robustness(pf: list[dict], tf: list[dict], k: int, runs: int, rng: random.Random) -> tuple[list[float], list[float]]:
    """Perturb both weight sets together and re-rank the combined list.

    Returns (p_top_k, mean_rank) per item, pain points first and then trends."""
    n = len(pf) + len(tf)
    if n == 0:
        return [], []
    hits, ranks = [0] * n, [0.0] * n
    for _ in range(runs):
        wp = {key: v * rng.uniform(0.75, 1.25) for key, v in PAIN_WEIGHTS.items()}
        wt = {key: v * rng.uniform(0.75, 1.25) for key, v in TREND_WEIGHTS.items()}
        s = score(pf, wp) + score(tf, wt)
        order = sorted(range(n), key=lambda i: s[i], reverse=True)
        for r, i in enumerate(order, 1):
            ranks[i] += r
            if r <= k:
                hits[i] += 1
    return [h / runs for h in hits], [r / runs for r in ranks]


# --------------------------------------------------------------------------- model
def build(research: dict, undying: dict | None, top: int, runs: int, seed: int) -> dict:
    rng = random.Random(seed)
    pains = research.get("pain_points", [])
    trends = research.get("trends", [])
    pf, tf = pain_features(pains), trend_features(trends)
    ps, ts = score(pf, PAIN_WEIGHTS), score(tf, TREND_WEIGHTS)
    n = len(pains) + len(trends)
    k = max(1, min(top, n // 2))  # "top-k" must be a real cut, never the whole list
    probs, mean_ranks = robustness(pf, tf, k, runs, rng)
    pr, tr = probs[:len(pains)], probs[len(pains):]
    mr_p, mr_t = mean_ranks[:len(pains)], mean_ranks[len(pains):]

    items = []
    for p, f, s, r, mr in zip(pains, pf, ps, pr, mr_p):
        items.append({"kind": "pain_point", "id": p["id"], "label": p.get("statement"), "status": p.get("status"),
                      "mean_rank": round(mr, 2),
                      "pillar": p.get("pillar") or ("education" if p.get("status") in ("solved", "partially_solved") else "problem-solution"),
                      "score": round(s, 1), "p_top_k": round(r, 3), "features": {k2: round(v, 3) for k2, v in f.items()},
                      "magnify": p.get("status") in ("ignored", "unsolved") and f["int"] >= 0.6})
    for t, f, s, r, mr in zip(trends, tf, ts, tr, mr_t):
        items.append({"kind": "trend", "id": t["id"], "label": t.get("name"), "type": t.get("type"),
                      "mean_rank": round(mr, 2),
                      "pillar": t.get("pillar") or "trend", "score": round(s, 1), "p_top_k": round(r, 3),
                      "features": {k2: round(v, 3) for k2, v in f.items()}, "hashtags": t.get("hashtags", [])})
    items.sort(key=lambda x: x["score"], reverse=True)
    for rank, it in enumerate(items, 1):
        it["rank"] = rank
        it["robust"] = it["p_top_k"] >= 0.7

    # pillar weights
    pillar_sum: dict[str, float] = defaultdict(float)
    for it in items[: max(top * 2, 10)]:
        pillar_sum[it["pillar"]] += it["score"]
    tot = sum(pillar_sum.values()) or 1
    pillars = {k2: round(v / tot, 3) for k2, v in sorted(pillar_sum.items(), key=lambda kv: -kv[1])}

    # platform allocation
    channels = research.get("audience_channels", {}) or {}
    allocation = {}
    for pl in PLATFORMS:
        tgt = ((undying or {}).get("platforms", {}).get(pl) or {}).get("target_posts_per_week")
        if tgt is None:
            continue
        per_pillar = {k2: round(tgt * w) for k2, w in pillars.items()}
        diff = tgt - sum(per_pillar.values())
        if per_pillar and diff:
            first = next(iter(per_pillar))
            per_pillar[first] += diff
        allocation[pl] = {"posts_per_week": tgt,
                          "share_of_attention": (channels.get(pl) or {}).get("share_of_attention"),
                          "per_pillar": per_pillar}

    # attention-weighted platform priority
    priority = sorted(
        [(pl, (channels.get(pl) or {}).get("share_of_attention") or 0) for pl in PLATFORMS],
        key=lambda kv: -kv[1])

    return {
        "contract": "prometheus.suggester.v1",
        "generated_at": dt.date.today().isoformat(),
        "model": {"pain_weights": PAIN_WEIGHTS, "trend_weights": TREND_WEIGHTS,
                  "robustness_runs": runs, "perturbation": "±25% per weight", "top_k": k, "seed": seed},
        "ranked": items,
        "top": items[:top],
        "magnify": [it for it in items if it.get("magnify")][:5],
        "pillars": pillars,
        "platform_priority": [{"platform": pl, "share_of_attention": s} for pl, s in priority],
        "allocation": allocation,
        "undying_totals": (undying or {}).get("totals"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Suggester Prometheus scoring model")
    ap.add_argument("--research", type=Path)
    ap.add_argument("--undying", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--runs", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--validate", type=Path, metavar="RESEARCH_JSON")
    a = ap.parse_args(argv)

    if a.validate:
        errs = validate(json.loads(a.validate.read_text(encoding="utf-8")))
        for e in errs:
            print("✗", e)
        print("✓ research.json is valid" if not errs else f"{len(errs)} problem(s)")
        return 1 if errs else 0

    if not a.research:
        ap.error("--research is required (or use --validate)")
    research = json.loads(a.research.read_text(encoding="utf-8"))
    errs = validate(research)
    if errs:
        print("research.json has problems (continuing with defaults):", *errs, sep="\n  ", file=sys.stderr)
    undying = json.loads(a.undying.read_text(encoding="utf-8")) if a.undying and a.undying.exists() else None
    result = build(research, undying, a.top, a.runs, a.seed)

    print(f"{'rank':>4} {'kind':<10} {'id':<5} {'score':>5} {'p_topk':>6} {'mrank':>5}  label  (k={result['model']['top_k']})")
    for it in result["top"]:
        print(f"{it['rank']:>4} {it['kind']:<10} {it['id']:<5} {it['score']:>5} {it['p_top_k']:>6.2f} {it['mean_rank']:>5}  {str(it['label'])[:66]}")
    print("pillars:", result["pillars"])
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
