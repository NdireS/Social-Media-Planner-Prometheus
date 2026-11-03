# Volume science: floors, ceilings and surfaces

These defaults are baselines as of late 2026. Platforms change their algorithms, so check
current guidance with a quick web search when a number matters, and update
`DEFAULT_SURFACES` in `scripts/cadence.py` if needed.

## Platform floors (used when no competitor is active)

| Platform | Floor posts/week | Why |
|---|---|---|
| LinkedIn | 5 | Weekday presence is the minimum to stay in network feeds |
| Facebook | 7 | Daily Reels and posts keep the page in recommendations |
| Instagram | 10 | Daily Reels plus carousels; stories are counted separately |
| TikTok | 14 | 2 a day is the classic growth cadence |
| X | 21 | The feed is fast; 3 a day is the minimum to be seen |
| Bluesky | 14 | A conversation-first feed rewards frequency |
| YouTube | 7 | Daily Shorts, plus a long-form video when possible |
| Telegram | 7 | Channel readers expect a daily drop |

## Surface ceilings (safe per day before quality or reach per post drops)

The engine fills surfaces in the listed order until it reaches their per-day ceiling, then overflows to the next.

| Platform | Surfaces (in fill order) → safe max per day |
|---|---|
| LinkedIn | feed post 2 · document carousel 1 · short video 1 · newsletter/article 0.3 · comment-posts (unlimited, counted in quota) |
| Facebook | reel 3 · feed post 3 · story 6 · group post 2 |
| Instagram | reel 3 · carousel 2 · story 10 · broadcast channel 3 |
| TikTok | video 5 · photo carousel 3 · story 5 |
| X | post 15 · thread 2 · quote/reply-post (unlimited, counted in quota) |
| Bluesky | post 15 · thread 2 · reply-post (unlimited) |
| YouTube | short 4 · long-form 0.5 · community post 2 · live 0.3 |
| Telegram | channel post 6 · poll 1 · story 3 |

## Engagement presence quota (per day)

The default is `max(10, 2 × daily posts)` meaningful interactions on high-reach accounts in the niche, spread
over the platforms with the highest `share_of_attention`. "Meaningful" means at least a full sentence
that adds value. Emoji-only replies don't count.

## Minimal standalone input

If you have no `research.json`, `cadence.py` also accepts a bare list:

```json
{
  "competitors": [
    {"name": "Rival A", "platforms": {"instagram": {"posts_per_week": 6}, "tiktok": {"posts_per_week": 10}}},
    {"name": "Rival B", "platforms": {"x": {"posts_per_week": 21}}}
  ]
}
```

## Atomization ladder (1 pillar → 25+ pieces)

1 long video (10 to 20 min) → 1 YouTube long-form · 5 to 8 Shorts/Reels/TikToks · 3 carousels ·
1 LinkedIn document · 1 blog and newsletter · 1 Telegram long post · 10 to 15 X/Bluesky posts (quotes, stats,
hot takes) · 1 thread · 3 polls · 5 stories.
