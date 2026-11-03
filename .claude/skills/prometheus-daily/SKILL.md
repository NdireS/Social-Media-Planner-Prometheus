---
name: prometheus-daily
description: "Daily 24-hour-trend content drop. Scans the last 24 hours, picks ONE idea, and adapts it natively to all 8 platforms with posters and a video spec. The scheduled daily run calls it. Use when the user types /prometheus-daily or asks for today's content."
argument-hint: "[optional business name / override]"
---


# /prometheus-daily: today's 24-hour drop

Brief override (may be empty): **$ARGUMENTS**

1. Load `prometheus.config.yaml` (with `$ARGUMENTS` overriding it). Work out `slug` and today's date in the
   business timezone (`business.timezone`).
2. Find the most recent weekly run: `output/<slug>/<latest-date>/`. Load its `research.json`, `suggester.json`,
   `outlier.json` and `weekly-plan.json` if they exist. If no weekly run exists yet, tell the user that the first
   `/prometheus` run gives better results, then continue with a light research pass.
3. Use the **planner-prometheus** skill in **daily** mode. It runs the 24-hour pulse, picks one idea, writes native
   versions for LinkedIn, Facebook, Instagram, TikTok, X, Bluesky, YouTube and Telegram, renders the posters and writes the video spec.
4. Output to `output/<slug>/daily/<YYYY-MM-DD>/`.
5. If today is `schedule.weekly_day` and the latest weekly run is older than 6 days, say that a weekly refresh is
   due (or run `/prometheus` if the config sets `schedule.auto_weekly: true`).
6. Reply with today's idea, the 8 post times, and the file paths.
