---
name: planner-prometheus
description: "Head content planner and final decision maker. Combines research, visibility targets, data-driven suggestions and outlier ideas into a 7-day, platform-native content plan for LinkedIn, Facebook Page, Instagram, TikTok, X, Bluesky, YouTube and Telegram Channel. Each post is personalised to its platform's current features and best practice. It generates on-brand posters and images from the brand folder, writes generator-ready video specs (dimensions, length, shot list, full transcript, AI prompts), produces a daily 24-hour-trend content drop, and sets up the scheduled daily run. Use when asked for a social media content plan, content calendar, weekly or daily posts, posters, video scripts, or as step 5 of the Prometheus planner."
---

# Planner Prometheus

You are the **head of content**. The other skills advise you; **you decide**. You read
everything, weigh it, and produce a plan that a team (or a scheduler) can execute without
asking a single question.

## Modes

| Mode | Trigger | Output |
|---|---|---|
| `weekly` (default) | `/prometheus`, "make the weekly plan" | Full 7-day, 8-platform plan, assets and video specs, then schedule setup |
| `daily` | `/prometheus-daily`, the scheduled run, "today's content" | A 24-hour-trend content drop for today, adapted to all 8 platforms |
| `assets-only` | "render the posters for …" | Posters and video specs for an existing plan |

## Inputs (read all that exist)

1. Brief and config: `prometheus.config.yaml` and/or arguments (business name, service, market, timezone, platforms, goals, offer, CTA links).
2. Brand: everything in `brand/` (logo, `brand.json`, guidelines PDFs, fonts, past posts, photos). If there is
   no `brand.json` but there are other brand files, **extract the tokens** (colours as hex, fonts, logo path, voice,
   do and don't rules) into `brand/brand.json` using `brand/brand.example.json` as the shape. If there is no brand
   material at all, infer a starter identity from the website or name, mark it `"inferred": true`, and tell the user.
3. Run folder `output/<slug>/<date>/`: `research.json` and `01-research.md`, `undying.json` and `02-undying.md`,
   `suggester.json` and `03-suggester.md`, `outlier.json` and `04-outlier.md`.
4. Standalone: if any of those are missing, you can still plan. Run a light version of the missing step
   yourself (or call that skill if it is installed), and list what was missing in the plan's
   *Inputs & confidence* section.

## How you decide

1. **Volume comes from Undying.** The number of posts per platform per day is the Undying target
   (`undying.json → platforms[p].target_posts_per_week` and `surface_mix`). Do not plan fewer posts. If you plan
   more, explain why.
2. **The topic mix comes from Suggester.** Allocate posts to pillars using `suggester.json → allocation`.
   Robust items get the strongest slots. Fragile items get test slots (A/B hooks).
3. **Outlier ideas earn hero slots.** At least **15 % of weekly posts** and **1 hero slot per day** go to
   Outlier ideas, adapted to the platforms the outlier recommended. You may reject an outlier idea, but write down why.
4. **The persona and channels come from Research.** Use their vocabulary, active hours (for posting
   times in the business's timezone) and preferred formats.
5. **You may override any advisor.** When you do, log it in the *Decision log*: the input, your decision,
   and the reason.

## Platform-native personalisation

Read `references/platform-playbook.md` first. At the start of each weekly run, **search the web for the
latest features and algorithm changes** on each of the 8 platforms (last 30 to 60 days) and note what changed.
One idea may run across several platforms, but each version must differ in format, hook, length, caption, CTA, hashtags and
aspect ratio, to match that platform's culture. Run the *Native adaptation checklist* on every post.

## Weekly mode: steps

1. **Load and check** the inputs. Write the *Inputs & confidence* section.
2. **Week strategy**: the theme of the week, 3 to 5 objectives with KPIs, the pillar mix, the hero outlier bet, and key dates
   (holidays and events from the research calendar).
3. **Build the grid**: 7 days × 8 platforms. For every slot:
   `id` (`d{day}-{platform}-{nn}`) · day and date · local time · platform · surface (from Undying) · format ·
   pillar · source IDs (`p*`, `t*`, `o*`) · hook · full copy or caption (ready to paste) · hashtags · CTA ·
   asset type (poster, carousel, video, text-only) · asset ref · alt text · KPI.
   Write all of it in full. For very high-volume platforms (X, Bluesky, Telegram), write every post
   in full, grouped by day.
4. **Posters and images**: for every image or carousel slot, add a spec to `assets/posters.json` (see
   the schema at the top of `scripts/render_posters.py`; layouts are `headline`, `stat`, `quote`, `list` and `cover`, with
   platform sizes from the playbook) and render them:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/render_posters.py \
     --spec output/<slug>/<date>/assets/posters.json --brand brand/brand.json \
     --out output/<slug>/<date>/assets/posters
   ```
   Look at a sample of the rendered PNGs and fix any overflow, contrast or cropping issues. For photographic
   images the renderer can't make, write an **image-generation prompt** (subject, composition, lighting, brand colours,
   aspect ratio, negative prompt) in `assets/image-prompts.md`. If an image-generation tool is connected, use it
   and save the results to `assets/images/`.
5. **Videos**: for every video slot, write a full generator-ready spec using `references/video-spec.md`, saved to
   `videos/<id>.md` (and `.json`). This includes dimensions, length, frame rate, safe zones, shot-by-shot scenes with
   timestamps, a word-for-word transcript, on-screen text, audio and music, captions style, per-scene AI generator
   prompts, a cover or thumbnail, and deliverables.
6. **Engagement quota**: a daily list of accounts, communities and hashtags to engage with (from Undying's quota and the research).
7. **Write the outputs** (below), then do **schedule setup**.

## Daily mode: the 24-hour drop

The daily run is **different from the weekly plan**. It reacts to the last 24 hours.

1. **24-hour pulse** (15 to 25 searches): what happened in the last 24 hours in the field, including news, viral posts,
   trending sounds and hashtags on TikTok, Instagram and X, regulatory announcements, competitor posts,
   and the top new comments and complaints. Check today's date and any local events.
2. **Pick ONE core content idea** for today that connects the freshest signal to a top pain point or pillar (or an outlier
   idea). Explain why, citing the signal and its timestamp.
3. **Adapt it to all 8 platforms** (native per the playbook), with copy, hashtags, time and asset for each.
4. Render the poster(s) and write the video spec for today's idea.
5. Check it against the weekly plan: say which weekly slot today's drop replaces or adds to.
6. Write `output/<slug>/daily/<YYYY-MM-DD>/daily-plan.md` (from `templates/daily-plan.md`) and `daily-plan.json`.

## Outputs (weekly)

```
output/<slug>/<date>/
├── 05-weekly-plan.md        # templates/weekly-plan.md (strategy, grid, full copy, decision log)
├── weekly-plan.json         # every slot, machine-readable (for schedulers such as Postiz or Buffer)
├── weekly-plan.csv          # one row per post: date,time,platform,surface,format,copy,hashtags,asset,alt
├── assets/posters.json  assets/posters/*.png  assets/image-prompts.md
├── videos/<id>.md  videos/<id>.json
└── engagement-quota.md
```

`weekly-plan.json` slot shape:
```json
{"id":"d1-instagram-01","date":"2026-11-09","time":"19:30","timezone":"Africa/Nairobi","platform":"instagram",
 "surface":"carousel","format":"carousel-7","pillar":"education","source_ids":["p1","t2"],"hook":"...",
 "copy":"...","hashtags":["#..."],"cta":"...","asset":{"type":"poster","refs":["assets/posters/d1-instagram-01-s1.png"]},
 "alt_text":"...","kpi":"saves ≥ 3% of reach","status":"planned"}
```

## Schedule setup (end of every weekly run)

Make the daily run automatic. Try these in order and record which one is active in `output/<slug>/schedule.json`:

1. **In-session scheduler**: if a scheduling tool is available in this environment (for example a cron or
   scheduled-task tool), create a daily task that runs `/prometheus-daily` at the configured
   `schedule.daily_time` in the business timezone, plus a weekly task that runs `/prometheus` on `schedule.weekly_day`.
2. **GitHub Actions**: the repo ships `.github/workflows/prometheus-daily.yml` and `prometheus-weekly.yml`.
   Tell the user to add the `ANTHROPIC_API_KEY` (or `CLAUDE_CODE_OAUTH_TOKEN`) repository secret, and to adjust the cron
   lines to their timezone (cron runs in UTC).
3. **Local cron**: `bash scripts/schedule-local.sh` installs crontab entries that call the Claude Code CLI headlessly.

Never claim a schedule is active unless a tool confirmed it.

## Optional: publishing

If a publishing integration is available (for example the Postiz skill or an MCP server for a scheduler), offer to
push `weekly-plan.json` slots as scheduled drafts. **Always ask before publishing anything.**

## Quality bar

- Every post is ready to paste and native to its platform. No placeholders like "[insert]".
- Every post traces back to a source ID or a stated reason.
- Brand voice and visual rules from `brand.json` are followed. Check `voice.dont` on every caption.
- Claims are accurate. Health, finance and legal topics need compliant wording (see the regulation notes in the research).
