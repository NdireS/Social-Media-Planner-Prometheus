#!/usr/bin/env python3
"""Planner Prometheus poster renderer: turns poster specs + brand tokens into PNG images.

posters.json:
{
  "posters": [
    {"id": "d1-ig-01", "platform": "instagram", "size": [1080, 1350],
     "layout": "headline" | "stat" | "quote" | "list" | "cover",
     "eyebrow": "SMALL LABEL", "headline": "Big words", "subhead": "...",
     "body": "..." , "items": ["for list layout"], "stat": "73%",
     "cta": "Book now", "footer": "@handle · site.com",
     "background_image": "optional/path/or/url.jpg", "theme": "light" | "dark" | "brand",
     "slide": "2/7"}
  ]
}

brand.json (brand/brand.json): see brand/brand.example.json
  colors: primary, secondary, accent, background, text
  fonts: heading, body (Google Fonts family names, fallbacks applied)
  logo: path relative to the brand.json file, or a URL
  handle, website

Renders with Python Playwright if installed, else with a Chrome/Chromium binary
(--headless --screenshot). Set CHROME_PATH to point at one. If neither is found,
the HTML files are kept so they can be opened and exported manually.

Usage:
  python3 render_posters.py --spec posters.json --brand brand/brand.json --out output/.../assets/posters
"""
from __future__ import annotations

import argparse
import html
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

DEFAULT_BRAND = {
    "name": "Brand",
    "colors": {"primary": "#111827", "secondary": "#374151", "accent": "#F59E0B",
               "background": "#F9FAFB", "text": "#111827"},
    "fonts": {"heading": "Poppins", "body": "Inter"},
    "logo": None, "handle": "", "website": "",
}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(w)dpx;height:%(h)dpx;overflow:hidden}
body{font-family:'%(body_font)s',system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;
  background:var(--bg);color:var(--fg);position:relative}
:root{--primary:%(primary)s;--secondary:%(secondary)s;--accent:%(accent)s;--bg:%(bg)s;--fg:%(fg)s;
  --pad:%(pad)dpx;--h1:%(h1)dpx;--h2:%(h2)dpx;--p:%(p)dpx}
.bgimg{position:absolute;inset:0;background-size:cover;background-position:center}
.bgimg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.7))}
.frame{position:absolute;inset:0;padding:var(--pad);display:flex;flex-direction:column;justify-content:space-between}
.top{display:flex;justify-content:space-between;align-items:center;gap:24px}
.logo{height:calc(var(--p)*2.4);max-width:40%%;object-fit:contain}
.brandname{font-family:'%(head_font)s',sans-serif;font-weight:800;font-size:calc(var(--p)*1.1);letter-spacing:.02em}
.slide{font-size:calc(var(--p)*.9);opacity:.7;font-weight:600}
.eyebrow{display:inline-block;background:var(--accent);color:var(--primary);font-weight:800;
  font-size:calc(var(--p)*.85);letter-spacing:.12em;text-transform:uppercase;padding:.45em .9em;border-radius:999px;margin-bottom:.9em}
h1{font-family:'%(head_font)s',sans-serif;font-weight:800;font-size:var(--h1);line-height:1.04;letter-spacing:-.02em}
h1 em{font-style:normal;color:var(--accent)}
h2{font-family:'%(head_font)s',sans-serif;font-weight:600;font-size:var(--h2);line-height:1.2;margin-top:.6em;opacity:.9}
p.body{font-size:var(--p);line-height:1.45;margin-top:1em;opacity:.9;max-width:92%%}
.stat{font-family:'%(head_font)s',sans-serif;font-weight:900;font-size:calc(var(--h1)*2.3);line-height:.95;color:var(--accent);letter-spacing:-.04em}
.quote{font-family:'%(head_font)s',sans-serif;font-size:calc(var(--h1)*.8);line-height:1.15;font-weight:700}
.quote::before{content:"\\201C";display:block;font-size:2.4em;line-height:.6;color:var(--accent)}
ul{list-style:none;margin-top:1.1em}
li{font-size:calc(var(--p)*1.15);line-height:1.35;padding:.55em 0 .55em 1.6em;position:relative;border-bottom:2px solid color-mix(in srgb,var(--fg) 12%%,transparent)}
li::before{content:"";position:absolute;left:0;top:1.05em;width:.7em;height:.7em;border-radius:50%%;background:var(--accent)}
.bottom{display:flex;justify-content:space-between;align-items:flex-end;gap:24px}
.cta{background:var(--accent);color:var(--primary);font-weight:800;font-size:calc(var(--p)*1.05);padding:.8em 1.3em;border-radius:14px}
.footer{font-size:calc(var(--p)*.85);opacity:.75}
.bar{position:absolute;left:0;top:0;bottom:0;width:calc(var(--pad)*.28);background:var(--accent)}
"""


def theme_colors(brand: dict, theme: str) -> tuple[str, str]:
    c = brand["colors"]
    if theme == "dark":
        return c.get("primary", "#111"), "#FFFFFF"
    if theme == "brand":
        return c.get("secondary", c.get("primary")), "#FFFFFF"
    return c.get("background", "#FFF"), c.get("text", "#111")


def as_url(ref: str | None, base: Path) -> str | None:
    if not ref:
        return None
    if ref.startswith(("http://", "https://", "data:", "file://")):
        return ref
    p = (base / ref).resolve() if not Path(ref).is_absolute() else Path(ref)
    return p.as_uri() if p.exists() else None


def build_html(spec: dict, brand: dict, brand_dir: Path, spec_dir: Path) -> str:
    w, h = spec.get("size", [1080, 1350])
    short = min(w, h)
    theme = spec.get("theme", "light")
    bg_img = as_url(spec.get("background_image"), spec_dir)
    bg, fg = theme_colors(brand, theme)
    if bg_img:
        fg = "#FFFFFF"
    c = brand["colors"]
    fonts = brand.get("fonts", {})
    vars_ = dict(w=w, h=h, primary=c.get("primary"), secondary=c.get("secondary", c.get("primary")),
                 accent=c.get("accent", "#F59E0B"), bg=bg, fg=fg, pad=int(short * 0.075),
                 h1=int(short * (0.085 if spec.get("layout") != "cover" else 0.11)),
                 h2=int(short * 0.042), p=int(short * 0.03),
                 head_font=fonts.get("heading", "Poppins"), body_font=fonts.get("body", "Inter"))
    e = lambda k: html.escape(str(spec.get(k, "") or ""))
    # allow *word* emphasis in headline
    headline = e("headline")
    parts = headline.split("*")
    headline = "".join(f"<em>{t}</em>" if i % 2 else t for i, t in enumerate(parts))

    logo = as_url(brand.get("logo"), brand_dir)
    top_left = f'<img class="logo" src="{logo}">' if logo else f'<div class="brandname">{html.escape(brand.get("name", ""))}</div>'
    slide = f'<div class="slide">{e("slide")}</div>' if spec.get("slide") else ""
    eyebrow = f'<div class="eyebrow">{e("eyebrow")}</div>' if spec.get("eyebrow") else ""

    layout = spec.get("layout", "headline")
    if layout == "stat":
        middle = f'{eyebrow}<div class="stat">{e("stat")}</div><h2>{headline}</h2>' + (f'<p class="body">{e("body")}</p>' if spec.get("body") else "")
    elif layout == "quote":
        middle = f'{eyebrow}<div class="quote">{headline}</div>' + (f'<h2>— {e("subhead")}</h2>' if spec.get("subhead") else "")
    elif layout == "list":
        items = "".join(f"<li>{html.escape(str(i))}</li>" for i in spec.get("items", []))
        middle = f'{eyebrow}<h1>{headline}</h1><ul>{items}</ul>'
    else:  # headline / cover
        middle = f'{eyebrow}<h1>{headline}</h1>' + (f'<h2>{e("subhead")}</h2>' if spec.get("subhead") else "") + \
                 (f'<p class="body">{e("body")}</p>' if spec.get("body") else "")

    footer = spec.get("footer") or " · ".join(x for x in [brand.get("handle"), brand.get("website")] if x)
    cta = f'<div class="cta">{e("cta")}</div>' if spec.get("cta") else "<div></div>"
    fam = "|".join(urllib.parse.quote_plus(f) + ":wght@400;600;700;800;900" for f in {vars_["head_font"], vars_["body_font"]})
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={fam.replace('|', '&family=')}&display=block">
<style>{CSS % vars_}</style></head><body>
{f'<div class="bgimg" style="background-image:url({bg_img})"></div>' if bg_img else '<div class="bar"></div>'}
<div class="frame"><div class="top">{top_left}{slide}</div>
<div class="mid">{middle}</div>
<div class="bottom"><div class="footer">{html.escape(footer)}</div>{cta}</div></div>
</body></html>"""


def find_chrome() -> str | None:
    cands = [os.environ.get("CHROME_PATH"), "/opt/pw-browsers/chromium", "google-chrome", "google-chrome-stable",
             "chromium", "chromium-browser", "chrome",
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
    for c in cands:
        if not c:
            continue
        p = Path(c)
        if p.is_dir():  # playwright layout
            for sub in p.glob("chrome-*/chrome"):
                return str(sub)
        if p.is_file():
            return str(p)
        found = shutil.which(c)
        if found:
            return found
    return None


def render(html_files: list[tuple[Path, Path, int, int]]) -> str:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for src, png, w, h in html_files:
                pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
                pg.goto(src.as_uri(), wait_until="networkidle")
                pg.screenshot(path=str(png))
                pg.close()
            b.close()
        return "playwright"
    except ImportError:
        pass
    chrome = find_chrome()
    if not chrome:
        return "none"
    for src, png, w, h in html_files:
        subprocess.run([chrome, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", f"--window-size={w},{h}",
                        "--virtual-time-budget=4000", f"--screenshot={png}", src.as_uri()],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)
    return "chrome-cli"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Render brand posters to PNG")
    ap.add_argument("--spec", required=True, type=Path)
    ap.add_argument("--brand", type=Path, default=Path("brand/brand.json"))
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)

    brand = json.loads(json.dumps(DEFAULT_BRAND))
    if a.brand.exists():
        user = json.loads(a.brand.read_text(encoding="utf-8"))
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(brand.get(k), dict):
                brand[k].update(v)
            else:
                brand[k] = v
    else:
        print(f"! brand file {a.brand} not found, using neutral defaults", file=sys.stderr)

    specs = json.loads(a.spec.read_text(encoding="utf-8"))["posters"]
    a.out.mkdir(parents=True, exist_ok=True)
    jobs = []
    for s in specs:
        w, h = s.get("size", [1080, 1350])
        src = a.out / f"{s['id']}.html"
        src.write_text(build_html(s, brand, a.brand.parent, a.spec.parent), encoding="utf-8")
        jobs.append((src, a.out / f"{s['id']}.png", w, h))
    engine = render(jobs)
    ok = [p for _, p, _, _ in jobs if p.exists()]
    print(f"engine={engine} rendered {len(ok)}/{len(jobs)} posters into {a.out}")
    if engine == "none":
        print("No browser found: open the .html files and export them, or install Chrome or Playwright "
              "(set CHROME_PATH).", file=sys.stderr)
    return 0 if len(ok) == len(jobs) or engine == "none" else 1


if __name__ == "__main__":
    sys.exit(main())
