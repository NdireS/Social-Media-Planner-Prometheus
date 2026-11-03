# Social Media Planner: Prometheus

This repository is a Claude Code project made of **five building-block skills** and **two pipeline skills**.
All of them live in `.claude/skills/` as real folders (no symlinks, so they work on Windows).

- `/prometheus [brief]` runs the full weekly pipeline (`.claude/skills/prometheus/SKILL.md`).
- `/prometheus-daily [brief]` runs the 24-hour daily drop (`.claude/skills/prometheus-daily/SKILL.md`). The schedule calls it.

| Order | Skill | Reads | Writes |
|---|---|---|---|
| 1 | `researcher-prometheus` | brief, config | `01-research.md`, `research.json`, `sources.md` |
| 2 | `undying-prometheus` | `research.json` | `undying.json`, `02-undying.md` |
| 3 | `suggester-prometheus` | `research.json`, `undying.json` | `suggester.json`, `03-suggester.md` |
| 4 | `outlier-prometheus` | brief only (research = graveyard) | `outlier.json`, `04-outlier.md` |
| 5 | `planner-prometheus` | all of the above, plus `brand/` | weekly plan, posters, video specs, schedule |

## Conventions
- Run folder: `output/<business-slug>/<YYYY-MM-DD>/`. Daily runs go in `output/<slug>/daily/<YYYY-MM-DD>/`.
- JSON contracts: `prometheus.research.v1`, `prometheus.undying.v1`, `prometheus.suggester.v1`, `prometheus.outlier.v1`.
  Don't rename keys; downstream scripts parse them.
- Platform ids: `linkedin, facebook, instagram, tiktok, x, bluesky, youtube, telegram`.
- Inside SKILL.md files, scripts are referenced as `${CLAUDE_SKILL_DIR}/scripts/...` so a skill works wherever it is
  installed (project, `~/.claude/skills`, or plugin). Sibling skills are `${CLAUDE_SKILL_DIR}/../<name>/`.
- Scripts use the Python standard library only (PyYAML for config, Playwright or Chrome optional for posters).
- Never publish to social platforms without explicit user confirmation.
- Smoke test: `bash scripts/selftest.sh`. Install globally: `bash scripts/install-skills.sh`.
