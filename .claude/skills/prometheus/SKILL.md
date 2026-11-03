---
name: prometheus
description: "Run the full Prometheus social media pipeline in one call: Researcher, then Undying, then Suggester and Outlier, then Planner. Produces a 7-day content plan for LinkedIn, Facebook, Instagram, TikTok, X, Bluesky, YouTube and Telegram, with posters, video specs and a scheduled daily run. Use when the user types /prometheus or asks for a full social media plan for a business."
argument-hint: "[business name, service, market]  (optional, otherwise prometheus.config.yaml is used)"
---


# /prometheus: full weekly pipeline

Brief from the user (may be empty): **$ARGUMENTS**

You are the orchestrator. Run the five Prometheus skills in order, passing files between them
through one run folder. Don't skip a stage. If a stage fails, record the failure, run a light
version of it yourself, and continue.

## 0. Set up
1. Load `prometheus.config.yaml` (fall back to `prometheus.config.example.yaml` only for its structure). Any
   value in `$ARGUMENTS` overrides the config.
2. If the **business name**, **service** or **market** is unknown, ask the user once, then proceed.
3. `slug` = the business name in kebab-case. `RUN=output/<slug>/<YYYY-MM-DD>`. Create `RUN/`.
4. Check `brand/`. If there are brand files but no `brand/brand.json`, the Planner will extract one.

## 1. Researcher Prometheus
Use the **researcher-prometheus** skill with the brief. Outputs: `RUN/01-research.md`, `RUN/research.json`, `RUN/sources.md`.
If a subagent tool is available, fan out the research phases in parallel.

## 2. Undying Prometheus
Use the **undying-prometheus** skill on `RUN/research.json` with `multiplier` from the config (default 2.0, never lower).
Outputs: `RUN/undying.json` and `RUN/02-undying.md`.

## 3 and 4. Suggester Prometheus and Outlier Prometheus (in parallel)
- **Suggester**: use the **suggester-prometheus** skill on `RUN/research.json` and `RUN/undying.json`.
  Outputs: `RUN/suggester.json` and `RUN/03-suggester.md`.
- **Outlier**: run the **outlier-prometheus** skill **in a separate subagent** if one is available, giving it ONLY the
  one-line brief (business, service, audience) and the path to `RUN/research.json` labelled "graveyard only". This
  keeps it independent of the data. Outputs: `RUN/04-outlier.md`, `RUN/04-outlier-workings.md` and `RUN/outlier.json`.

## 5. Planner Prometheus
Use the **planner-prometheus** skill in `weekly` mode on everything in `RUN/` plus `brand/`.
Outputs: `RUN/05-weekly-plan.md`, `weekly-plan.json` and `weekly-plan.csv`, plus `assets/`, `videos/` and `engagement-quota.md`.
Then do **schedule setup** as the planner skill describes.

## 6. Wrap up
- Write `RUN/README.md`: an index of every file with a one-line description of each.
- Reply to the user with: the week theme, the volume per platform (ours versus the leader), the top 3 data-driven moves, the
  outlier bet, the number of posts, posters and videos produced, where the files are, and the schedule status (only
  what was actually confirmed).
