#!/usr/bin/env python3
"""Static checks for the SnapClip site: internal links, image paths, hreflang set, size budget (8 MB for images)."""
import json, re, sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "snapclip"
errs = []
pages = {"index.html": (SITE / "index.html").read_text(encoding="utf-8")}
for f in sorted((SITE / "assets/i18n").glob("*.json")):
    d = json.loads(f.read_text(encoding="utf-8"))
    pages[f.name] = " ".join([d["main"], d["foot"], d["meta"]["image"], *d["ld"]])
n_links = 0
for name, html in pages.items():
    for url in set(re.findall(r'(?:href|src|data-src)="([^"]+)"', html)):
        if url.startswith(("mailto:", "#", "https://play.google.com/")):
            continue
        u = urlsplit(url)
        path = u.path if not u.netloc else (u.path if u.netloc == "mehmetth.github.io" else None)
        if path is None:
            errs.append(f"{name}: external {url}"); continue
        n_links += 1
        if not (ROOT / path.lstrip("/")).exists() and not (ROOT / path.lstrip("/") / "index.html").exists():
            errs.append(f"{name}: missing {path}")
    for img in re.findall(r"https://mehmetth\.github\.io(/snapclip/assets/screens/[^\s\"\\]+)", html):
        if not (ROOT / img.lstrip("/")).exists():
            errs.append(f"{name}: missing JSON-LD image {img}")
idx = pages["index.html"]
alts = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', idx)
if len(alts) != 19:
    errs.append(f"hreflang count {len(alts)} != 19")
for need in ("snapclip-privacy-policy.html", "snapclip-terms-and-conditions.html", "snapclip-data-deletion.html"):
    for name, html in pages.items():
        if need not in html:
            errs.append(f"{name}: footer link {need} missing")
for name, html in pages.items():
    if "data-play" not in html or "withoutwatermark" not in html:
        errs.append(f"{name}: Play link missing")
total = sum(p.stat().st_size for p in (SITE / "assets/screens").rglob("*.webp"))
print(f"pages checked: {len(pages)}, internal refs checked: {n_links}, hreflang: {len(alts)}")
print(f"WebP total: {total/1024/1024:.2f} MB in {len(list((SITE/'assets/screens').rglob('*.webp')))} files (budget 8 MB)")
if total >= 8 * 1024 * 1024:
    errs.append("image budget exceeded")
print("\n".join(errs) if errs else "OK: no errors")
sys.exit(1 if errs else 0)
