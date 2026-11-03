# Video production spec (generator-ready)

Every video in a plan gets a full spec written to `videos/<id>.md`, plus a machine-readable copy in
`videos/<id>.json`. The spec must be detailed enough that **another tool** (an AI video generator such as
Veo, Sora, Runway, Kling, Pika or HeyGen, an editor such as CapCut or Premiere, or a human crew) can
produce it accurately **without asking a single question**.

## Required fields

```yaml
id: d3-tiktok-01
platform: tiktok
title: "..."
objective: awareness | engagement | conversion | education
pillar: problem-solution
source_ids: [p1, t3]          # research / suggester / outlier IDs that justify it
format:
  aspect_ratio: "9:16"
  resolution: "1080x1920"
  frame_rate: 30
  duration_seconds: 34
  safe_zones: "keep text inside x 60–920, y 220–1420 (TikTok UI)"
  codec: "H.264, MP4, ≤ 287 MB"
audio:
  voiceover: true
  voice: "female, late 20s, warm Nairobi English accent, conversational, 160 wpm"
  music: "lo-fi afrobeat instrumental, 96 BPM, ducked to −18 LUFS under VO"
  sfx: ["whoosh at 00:02.0", "pop at 00:11.5"]
  loudness: "−14 LUFS integrated"
look:
  style: "handheld, natural light, warm grade, slight grain"
  brand_colors: ["#0F4C81", "#F2C14E"]
  fonts: {headline: "Poppins Bold", captions: "Inter SemiBold"}
  on_screen_text_style: "white, 6 px brand-primary stroke, max 6 words per card"
  captions: "burned-in, word-by-word highlight in accent colour, centred at y=1250"
talent: "one presenter: woman, 28, braids, casual blazer, speaking to camera"
locations: ["small bright clinic room", "matatu window (B-roll)"]
props: ["shade guide", "phone showing price list"]
scenes:
  - n: 1
    time: "00:00.0–00:01.5"
    shot: "extreme close-up of a smile, quick push-in"
    camera: "50 mm equivalent, handheld, push-in 10 %"
    action: "smile drops into a frown"
    on_screen_text: "Your whitening faded in 3 weeks?"
    vo: "If your whitening faded in three weeks…"
    transition: "hard cut on the beat"
    generator_prompt: "Extreme close-up of a young Black woman's smile in warm natural light, the smile slowly turns into a frown, shallow depth of field, handheld, 9:16"
  - n: 2
    # …
cta: {on_screen: "Book a free shade check: link in bio", vo: "...", end_card_seconds: 2}
caption: "..."                 # platform caption
hashtags: ["#..."]
thumbnail_or_cover: {frame: "00:00.8", text: "FADED IN 3 WEEKS?", size: "1080x1920"}
accessibility: {captions: true, alt_text: "...", no_flashing: true}
deliverables: ["master 9:16 MP4", "SRT captions file", "cover image PNG"]
```

## Writing the transcript
- Include a full **word-for-word script** with timestamps (`[00:03.2] VO: …`), on-screen text and speaker labels.
- Long-form YouTube videos also need: chapters with timestamps, B-roll list per chapter, lower-thirds, end screen at the last 20 s, and a title, description and tags pack.
- Each scene needs its own `generator_prompt`: a self-contained visual description covering subject, action, setting, lighting, lens, movement, mood and aspect ratio. Don't refer to "the previous shot".
- Keep the same character described identically in every prompt (appearance, clothing) so the AI generator stays consistent.

## Platform defaults
| Platform | Ratio | Resolution | Ideal length | Hook window |
|---|---|---|---|---|
| TikTok | 9:16 | 1080×1920 | 15–60 s (1–3 min for search) | 1 s |
| Instagram Reels | 9:16 | 1080×1920 | 7–45 s | 1.5 s |
| Facebook Reels | 9:16 | 1080×1920 | 15–60 s | 2 s |
| YouTube Shorts | 9:16 | 1080×1920 | 20–60 s (≤ 3 min) | 1 s |
| YouTube long-form | 16:9 | 1920×1080 / 3840×2160 | 8–20 min | 15 s |
| LinkedIn video | 9:16 or 1:1 | 1080×1920 / 1080×1080 | 30–90 s | 3 s |
| X video | 16:9 or 1:1 | 1920×1080 / 1080×1080 | 15–45 s | 2 s |
| Bluesky video | 9:16 or 16:9 | 1080×1920 / 1920×1080 | 15–60 s | 2 s |
| Telegram video | any; 16:9 or round "circle" 1:1 | 1280 wide / 640×640 circle | 15–90 s | 3 s |
