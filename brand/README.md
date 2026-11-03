# Brand folder

Drop your brand material here. The Planner uses it to make on-brand posters, images and video looks.

| File | Purpose |
|---|---|
| `brand.json` | Brand tokens: colours, fonts, logo, voice, visual rules. Copy `brand.example.json` to start |
| `logo.png` / `logo.svg` | Logo (a transparent PNG or SVG works best) |
| `guidelines.pdf` | Any brand book; the Planner extracts tokens from it |
| `fonts/` | Custom font files (optional; Google Fonts names in `brand.json` are loaded automatically) |
| `photos/` | Real photos of the team, place and product, used as poster backgrounds |
| `past-posts/` | Screenshots of posts that worked, so the Planner can match the style |

If there is no `brand.json`, the Planner extracts one from whatever is here. If the folder is empty, it infers a
starter identity from the business name and website, and marks it `"inferred": true`.
