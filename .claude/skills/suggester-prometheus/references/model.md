# Suggester scoring model

## Why these factors

| Factor | Meaning | Why it matters |
|---|---|---|
| Frequency (F) | How often the pain is mentioned (log-normalised) | Reach: many people feel it |
| Intensity (I) | Emotional strength, 1 to 5 | Stopping power: strong pain stops the scroll |
| Gap (G) | 1 − competitor coverage | White space: room to own the topic |
| Status (S) | ignored > unsolved > partially solved > solved | Novelty of the message |
| Relevance (R) | How well the service solves it | Conversion potential |
| Confidence (C) | Number of evidence sources, capped at 5 | Penalises thin evidence |

Pain-point weights: F .25 · I .20 · G .20 · S .15 · R .15 · C .05

Trend weights: velocity .30 · relevance .25 · audience overlap .20 · (1 − saturation) .15 · confidence .10

## Robustness

Each weight is perturbed by a uniform ±25 % over N runs (default 500, seed 42). `p_top_k` is the share of runs
in which the item stays in the top-k. An item with p ≥ 0.7 is **robust**: it wins under any reasonable
weighting. A fragile item depends on the weighting choice, so test it before scaling it.

## Allocation

`posts(platform, pillar) = undying_target(platform) × pillar_weight`, where the pillar weight is the
item scores summed per pillar over the top 2k items, normalised to 1. Rounding error is added to the largest pillar.

## Minimum fields needed (standalone)

```json
{
  "business": {"name": "...", "service": "..."},
  "competitors": [],
  "persona": {},
  "pain_points": [{"id": "p1", "statement": "...", "status": "unsolved", "mentions": 10,
                   "intensity": 4, "competitor_coverage": 0.2, "relevance": 0.8, "evidence": []}],
  "trends": [{"id": "t1", "name": "...", "velocity": "rising", "relevance": 0.7,
              "audience_overlap": 0.6, "competitor_saturation": 0.3, "evidence": []}],
  "audience_channels": {"instagram": {"share_of_attention": 0.4}}
}
```

## Tuning

Edit `PAIN_WEIGHTS` or `TREND_WEIGHTS` in `scripts/score.py` if the business has a different goal,
for example raising `rel` for direct-response sales or raising `freq` for pure awareness. Record
the change in `03-suggester.md`.
