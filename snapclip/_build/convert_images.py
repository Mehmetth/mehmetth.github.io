#!/usr/bin/env python3
"""Variant A (Sunburst Sticker) store visuals -> web WebP.

Source: ../snapclip_store/fastlane/metadata/android/<locale>/images/
  phoneScreenshots/1..8.png (1080x1920) -> assets/screens/<locale>/1..8.webp (540 px wide)
  featureGraphic.png (1024x500)         -> assets/screens/<locale>/feature.webp (1024x500)
Only the 12 markets that have their own visuals; the other 6 languages fall back to en-US in the page.
Usage: python3 snapclip/_build/convert_images.py   (needs Pillow)
"""
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
STORE = ROOT.parent / "snapclip_store/fastlane/metadata/android"
OUT = ROOT / "snapclip/assets/screens"
LOCALES = "en-US tr-TR es-419 es-ES pt-BR de-DE fr-FR ar id vi ja-JP ko-KR".split()
QUALITY = 82


def save(img, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(dest, "WEBP", quality=QUALITY, method=6)


total = 0
for loc in LOCALES:
    src = STORE / loc / "images"
    for n in range(1, 9):
        im = Image.open(src / "phoneScreenshots" / f"{n}.png")
        assert im.size == (1080, 1920), (loc, n, im.size)
        save(im.resize((540, 960), Image.LANCZOS), OUT / loc / f"{n}.webp")
    fg = Image.open(src / "featureGraphic.png")
    assert fg.size == (1024, 500), (loc, fg.size)
    save(fg, OUT / loc / "feature.webp")
    size = sum(p.stat().st_size for p in (OUT / loc).glob("*.webp"))
    total += size
    print(f"{loc:8s} {size/1024:7.1f} KB")
print(f"TOTAL {total/1024/1024:.2f} MB")
sys.exit(0 if total < 8 * 1024 * 1024 else 1)
