# `research.json` schema (contract v1)

Downstream skills parse this file, so keep the key names exactly as shown. Extra keys are allowed.
Platform keys are always these lowercase ids:
`linkedin, facebook, instagram, tiktok, x, bluesky, youtube, telegram` (add others, e.g. `reddit`, `blog`, if useful).

```json
{
  "contract": "prometheus.research.v1",
  "generated_at": "2026-11-03",
  "business": {
    "name": "Acme Dental",
    "service": "teeth whitening",
    "home_market": "Nairobi, Kenya",
    "target_markets": ["Kenya", "East Africa"],
    "website": "https://example.com",
    "assumptions": ["..."]
  },
  "competitors": [
    {
      "id": "c1",
      "name": "SmileCo",
      "class": "direct | partial | platform | software | institution | creator",
      "region": "local | regional | international",
      "offering": "what they sell that overlaps",
      "positioning": "their one-line promise",
      "url": "https://...",
      "strengths": ["..."],
      "weaknesses": ["..."],
      "gap_left_open": "...",
      "platforms": {
        "instagram": {
          "handle": "@smileco",
          "followers": 12000,
          "posts_per_week": 5,
          "engagement_rate": 0.018,
          "format_mix": {"reels": 0.6, "carousel": 0.3, "static": 0.1},
          "top_posts": [{"url": "...", "hook": "...", "why_it_worked": "..."}],
          "posting_times": "Tue-Thu 18:00-20:00",
          "window": "2026-10-04..2026-11-02",
          "data_quality": "measured | reported | estimated"
        }
      }
    }
  ],
  "category_activity": {
    "instagram": {"user_posts_per_week_estimate": 400, "notes": "...", "data_quality": "estimated"}
  },
  "pain_points": [
    {
      "id": "p1",
      "statement": "Whitening results fade in weeks and nobody tells you why",
      "status": "solved | partially_solved | unsolved | ignored",
      "mentions": 37,
      "intensity": 4,
      "competitor_coverage": 0.2,
      "relevance": 0.9,
      "evidence": [{"source": "reddit", "quote": "verbatim", "url": "https://..."}],
      "pillar": "education"
    }
  ],
  "aspirations": [{"id": "a1", "statement": "...", "evidence": [], "mentions": 10}],
  "future_talk": [{"statement": "...", "evidence": []}],
  "objections": [{"statement": "...", "evidence": []}],
  "vocabulary": ["real phrases people use"],
  "trends": [
    {
      "id": "t1",
      "name": "At-home LED kits",
      "type": "social | hashtag | search | regulatory | ai | technology | economic | cultural",
      "velocity": "rising | peak | declining",
      "relevance": 0.8,
      "audience_overlap": 0.7,
      "competitor_saturation": 0.4,
      "evidence": [{"source": "...", "url": "...", "note": "..."}],
      "hashtags": ["#..."],
      "pillar": "trend"
    }
  ],
  "hashtags": {
    "instagram": {"broad": ["#..."], "niche": ["#..."], "branded": ["#..."]}
  },
  "persona": {
    "name": "Wanjiru",
    "age": 29,
    "location": "Nairobi",
    "job": "...",
    "income_band": "...",
    "day_in_life": "...",
    "goals": ["..."],
    "fears": ["..."],
    "top_pain_points": ["p1", "p4"],
    "objections": ["..."],
    "triggers": ["wedding invite", "..."],
    "trusts": ["..."],
    "saves_and_shares": ["..."],
    "words_they_use": ["..."]
  },
  "audience_channels": {
    "instagram": {"share_of_attention": 0.35, "behaviour": "discovers & saves", "active_hours": "19:00-23:00", "formats": ["reels", "carousel"], "communities": ["..."]},
    "tiktok": {"share_of_attention": 0.30, "behaviour": "...", "active_hours": "...", "formats": ["..."]}
  },
  "gaps_in_research": ["Could not access ..."]
}
```

Scales: `intensity` runs 1 to 5. `mentions` is an integer (approximate is fine). `competitor_coverage`,
`relevance`, `audience_overlap`, `competitor_saturation` and `share_of_attention` each run 0 to 1.
