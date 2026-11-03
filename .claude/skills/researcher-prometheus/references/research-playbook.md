# Research playbook

Use this as a checklist. Replace `{service}`, `{city}`, `{country}`, `{competitor}`,
`{handle}` and `{year}` with real values.

## Query banks

### Competitor discovery (Phase 1)
- `{service} {city}` / `{service} near {city}` / `best {service} {country} {year}`
- `{service} company` / `{service} agency` / `{service} startup` / `{service} app`
- `{service} software` / `{service} SaaS` / `{service} AI tool` / `alternative to {competitor}`
- `{competitor} vs` (autocomplete shows the rivals people compare)
- `{service} site:crunchbase.com` / `site:producthunt.com {service}` / `site:g2.com {service}`
- `{service} government programme {country}` / `{service} NGO {country}` / `{service} course university`
- `{service} tiktok` / `{service} youtube channel` / `{service} influencer {country}`
- App stores: search the service keyword and record the top 10 apps with ratings and review counts.
- Google Maps: search `{service}` in `{city}` and record rating, review count and categories.
- Marketplaces: Fiverr, Upwork, Jiji, Amazon, Etsy and local equivalents (if the service is sold there).

### Social activity (Phase 2)
- Platform search for brand name and handle; check the profile, the last 30 days of posts and pinned posts.
- `site:instagram.com {competitor}` / `site:tiktok.com @{handle}` / `site:linkedin.com/company {competitor}`
- `site:t.me {service}` / `site:bsky.app {service}` / `site:youtube.com {service} {country}`
- Third-party analytics (public pages): Social Blade, HypeAuditor and similar free profile pages, used as `reported` data.
- Facebook Ad Library and LinkedIn ad transparency for competitors' **active ads**, which reveal the angles they pay for.
- Blogs: `{competitor} blog`, RSS feeds, sitemap.xml with lastmod dates (gives the publishing cadence).

### Voice of customer (Phase 3)
- `site:reddit.com {service}` / `site:reddit.com {service} {country}` / `"{service}" "I hate"` / `"{service}" "wish there was"`
- `"{service}" "anyone else"` / `"{service}" "is it just me"` / `"{service}" scam` / `"{service}" too expensive`
- `site:quora.com {service}` / `{competitor} reviews` / `{competitor} complaints` / `site:trustpilot.com {competitor}`
- App store reviews, sorted by "most critical"
- YouTube and TikTok comments under the top 5 videos on the topic (sort by top and by newest)
- Facebook groups and Telegram groups for the category in `{country}`
- Future talk: `future of {service}`, `{service} in 5 years`, `{service} AI will replace`, `{service} {year+1} predictions`

### Trends and forces (Phase 4)
- Google Trends: the service term over 12 months, plus related rising queries, for both `{country}` and worldwide
- `{service} trends {year}` / `{service} statistics {year}` / `{service} market report {year}`
- `{service} regulation {country} {year}` / `{service} law change` / `{service} advertising rules {country}`
- `{service} AI` / `AI {service} tool` / `how AI is changing {service}`
- Hashtags: search the platform's hashtag or topic pages and note post counts or "views" where shown
- TikTok Creative Center (trending hashtags and sounds by country and industry), if accessible
- `{country} public holidays {year}` and industry events and conferences in the next 90 days

## Measurement rules

- **Posts/week** = posts in the observed window ÷ (window days ÷ 7). Use 14 to 30 days and record the window.
- **Engagement rate (ER)** = mean (likes + comments + shares/reposts + saves where visible) ÷ followers, taken over the last 10 posts.
- For YouTube, use views ÷ subscribers for the last 10 uploads, and record Shorts and long-form separately.
- For Telegram, use average views per post ÷ subscribers and posts/day.
- **Intensity** scale: 1 = mild preference, 2 = annoyance, 3 = clear frustration, 4 = anger or high cost, 5 = desperation, harm or legal or financial damage.
- **Competitor coverage** (0 to 1) = the share of deep-profiled competitors that address the pain point in content or product.
- **Relevance** (0 to 1) = how directly the business's service can address the pain point.
- **Share of attention** (0 to 1 across platforms, summing to about 1) = where the persona spends category-relevant time, estimated from evidence.

## Depth checklist (tick before finishing)

- [ ] ≥ 25 competitors listed across all six classes, both local and international
- [ ] 8 to 12 deep profiles with per-platform cadence and ER
- [ ] User-generated content volume estimated per platform
- [ ] ≥ 15 pain points, each with verbatim quotes and links
- [ ] Each pain point classified as solved, partially solved, unsolved or ignored
- [ ] ≥ 10 trends with velocity, including regulatory and AI forces
- [ ] Hashtag sets per platform (broad, niche and branded)
- [ ] Vocabulary bank of ≥ 30 real phrases
- [ ] One sharp primary persona, with channels and active hours
- [ ] `research.json` is valid against the schema
- [ ] Gaps and blocked sources are listed
