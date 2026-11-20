#!/usr/bin/env python3
"""Builds the SnapClip website (v2.1, 18 languages) from the store listing.

Reads  ../snapclip_store/fastlane/metadata/android/<locale>/{title,short_description,full_description}.txt
       snapclip/_build/ui_{a,b,c}.py        (UI strings + 8 v2.1 feature cards per language)
Writes snapclip/index.html                  (English, fully rendered: no-JS and crawler default)
       snapclip/assets/i18n/<slug>.json     (one per language: meta, header strings, <main>, footer)
       snapclip/assets/site.js              (from site.js.tpl)
       snapclip/sitemap.xml and the snapclip entry in ../sitemap.xml (hreflang alternates)
Run:   python3 snapclip/_build/build_site.py     (images: convert_images.py)
"""
import html as H
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from ui_a import UI as UA  # noqa: E402
from ui_b import UI as UB  # noqa: E402
from ui_c import UI as UC  # noqa: E402

ROOT = HERE.parents[1]
SITE = ROOT / "snapclip"
STORE = ROOT.parent / "snapclip_store/fastlane/metadata/android"
ORIGIN = "https://mehmetth.github.io"
PATH = "/snapclip/"
PKG = "com.durusoft.snapclip.video.downloader.nowatermark.saver.videodownloader.withoutwatermark"
PLAY = f"https://play.google.com/store/apps/details?id={PKG}"
EMAIL = "duru.sofft@gmail.com"
VERSION = "20261120"
LASTMOD = "2026-11-20"
UI = {**UA, **UB, **UC}

# slug = value of ?lang=; code = store locale folder; img = folder with its own Variant A visuals (else en-US fallback)
L = lambda slug, code, html, hreflang, og, name, img, hl, d="ltr": dict(  # noqa: E731
    slug=slug, code=code, html=html, hreflang=hreflang, og=og, name=name, img=img, hl=hl, dir=d)
LANGS = [
    L("en", "en-US", "en", "en", "en_US", "English", "en-US", "en-US"),
    L("tr", "tr-TR", "tr", "tr", "tr_TR", "Türkçe", "tr-TR", "tr"),
    L("es-419", "es-419", "es-419", "es", "es_LA", "Español (Latinoamérica)", "es-419", "es-419"),
    L("es-es", "es-ES", "es-ES", "es-ES", "es_ES", "Español (España)", "es-ES", "es"),
    L("pt-br", "pt-BR", "pt-BR", "pt-BR", "pt_BR", "Português (Brasil)", "pt-BR", "pt-BR"),
    L("de", "de-DE", "de", "de", "de_DE", "Deutsch", "de-DE", "de"),
    L("fr", "fr-FR", "fr", "fr", "fr_FR", "Français", "fr-FR", "fr"),
    L("ar", "ar", "ar", "ar", "ar_AR", "العربية", "ar", "ar", "rtl"),
    L("id", "id", "id", "id", "id_ID", "Bahasa Indonesia", "id", "id"),
    L("vi", "vi", "vi", "vi", "vi_VN", "Tiếng Việt", "vi", "vi"),
    L("ja", "ja-JP", "ja", "ja", "ja_JP", "日本語", "ja-JP", "ja"),
    L("ko", "ko-KR", "ko", "ko", "ko_KR", "한국어", "ko-KR", "ko"),
    L("it", "it-IT", "it", "it", "it_IT", "Italiano", "en-US", "it"),
    L("nl", "nl-NL", "nl", "nl", "nl_NL", "Nederlands", "en-US", "nl"),
    L("pl", "pl-PL", "pl", "pl", "pl_PL", "Polski", "en-US", "pl"),
    L("sv", "sv-SE", "sv", "sv", "sv_SE", "Svenska", "en-US", "sv"),
    L("th", "th", "th", "th", "th_TH", "ไทย", "en-US", "th"),
    L("hi", "hi-IN", "hi", "hi", "hi_IN", "हिन्दी", "en-US", "hi"),
]
assert len(LANGS) == 18

esc = lambda s: H.escape(s, quote=True)  # noqa: E731
abs_url = lambda slug: ORIGIN + PATH + ("" if slug == "en" else f"?lang={slug}")  # noqa: E731


def ic(name, cls=""):
    return f'<svg class="ic{(" " + cls) if cls else ""}" aria-hidden="true"><use href="#i-{name}"/></svg>'


SPRITE = (
    '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
    '<symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12.5 4.2 4.2L19 7"/></symbol>'
    '<symbol id="i-chev-l" viewBox="0 0 24 24"><path d="m14.5 6-6 6 6 6"/></symbol>'
    '<symbol id="i-chev-r" viewBox="0 0 24 24"><path d="m9.5 6 6 6-6 6"/></symbol>'
    '<symbol id="i-chev-d" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></symbol>'
    '<symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.6 2.7 3.9 5.7 3.9 9s-1.3 6.3-3.9 9c-2.6-2.7-3.9-5.7-3.9-9S9.4 5.7 12 3z"/></symbol>'
    '<symbol id="i-dl" viewBox="0 0 24 24"><path d="M12 4v11m-4.5-4.5L12 15l4.5-4.5"/><path d="M5 15v3a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-3"/></symbol>'
    '<symbol id="i-noad" viewBox="0 0 24 24"><rect x="6" y="3" width="12" height="18" rx="2.5"/><path d="M9.5 7.5h5M3.5 3.5l17 17"/></symbol>'
    '<symbol id="i-retry" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4v4.5h-4.5"/></symbol>'
    '<symbol id="i-photos" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="10" r="1.6"/><path d="m4 17 5-4.5 4 3.5 3-2.5 4 3.5"/></symbol>'
    '<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></symbol>'
    '<symbol id="i-vault" viewBox="0 0 24 24"><rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/></symbol>'
    '<symbol id="i-infinity" viewBox="0 0 24 24"><path d="M12 12c-1.7-2.3-3.2-3.5-5-3.5a3.5 3.5 0 0 0 0 7c1.8 0 3.3-1.2 5-3.5zm0 0c1.7 2.3 3.2 3.5 5 3.5a3.5 3.5 0 0 0 0-7c-1.8 0-3.3 1.2-5 3.5z"/></symbol>'
    '<symbol id="i-bolt" viewBox="0 0 24 24"><path d="M13 3 5.5 13.5H11L10 21l7.5-10.5H12z"/></symbol>'
    '<symbol id="i-crown" viewBox="0 0 24 24"><path d="M4 8l4 4 4-6 4 6 4-4-1.5 10h-13z"/></symbol>'
    '<symbol id="i-shield" viewBox="0 0 24 24"><path d="M12 3 5 6v5.5c0 4.4 3 8.3 7 9.5 4-1.2 7-5.1 7-9.5V6z"/><path d="m9 12 2.2 2.2L15.5 10"/></symbol>'
    '<symbol id="i-play" viewBox="0 0 24 24"><path fill="#00D7FE" d="M1.337.924a1.486 1.486 0 0 0-.112.568v21.017c0 .217.045.419.124.6l11.155-11.087z"/><path fill="#FFCE00" d="m22.018 13.298-3.919 2.218-3.515-3.493 3.543-3.521 3.891 2.202a1.49 1.49 0 0 1 0 2.594z"/><path fill="#00F076" d="m13.544 10.989 3.258-3.238L3.45.195a1.466 1.466 0 0 0-.946-.179z"/><path fill="#FF3A44" d="m13.544 13.056-11 10.933c.298.036.612-.016.906-.183l13.324-7.54z"/></symbol>'
    "</defs></svg>"
)

# ---------------------------------------------------------------- store text
BULLET = re.compile(r"^[•·\-\*]\s*")
NUMBER = re.compile(r"^\d+[.)]\s*")


def store(code):
    d = STORE / code
    read = lambda n: (d / n).read_text(encoding="utf-8").strip()  # noqa: E731
    blocks = re.split(r"\n\s*\n", read("full_description.txt"))
    assert len(blocks) == 10, (code, len(blocks))

    def parts(b):
        lines = [x.strip() for x in b.split("\n") if x.strip()]
        return lines[0], lines[1:]

    def bullets(lines):
        return [BULLET.sub("", x) for x in lines if BULLET.match(x)]

    s = dict(title=read("title.txt"), short=read("short_description.txt"), intro=blocks[0].strip())
    s["how"] = [NUMBER.sub("", x) for x in parts(blocks[1])[1]]
    s["why_h"], w = parts(blocks[2]); s["why"] = bullets(w)
    s["fair_h"], w = parts(blocks[3]); s["fair"] = bullets(w)
    s["off_h"], w = parts(blocks[4]); s["off"] = bullets(w)
    s["prem_h"], w = parts(blocks[5]); s["prem"] = bullets(w); s["prem_fine"] = " ".join(x for x in w if not BULLET.match(x))
    s["ext_h"], w = parts(blocks[6]); s["ext"] = bullets(w)
    _, w = parts(blocks[7])
    faq = []
    for line in w:
        m = re.match(r"^(.+?[?？؟])\s*(.+)$", line)
        assert m, (code, line)
        faq.append((m.group(1).replace("\xa0", " ").strip(), m.group(2).strip()))
    s["faq"] = faq
    s["priv_h"], w = parts(blocks[8]); s["priv"] = " ".join(w)
    _, w = parts(blocks[9]); s["note"] = " ".join(w)
    assert len(s["how"]) == 3 and len(s["why"]) >= 7 and len(s["prem"]) == 6 and len(faq) >= 2, code
    return s


# ---------------------------------------------------------------- rendering
CARD_ICONS = ["dl", "noad", "retry", "photos", "search", "vault", "infinity", "bolt"]


def img_dir(l):
    return f"{PATH}assets/screens/{l['img']}"


def store_btn(l, geton, data_i=False):
    gi = ' data-i="geton"' if data_i else ""
    return (f'<a class="store" href="{esc(play_url(l))}" data-play><svg class="logo" aria-hidden="true"><use href="#i-play"/></svg>'
            f'<span><small{gi}>{esc(geton)}</small><b>Google Play</b></span></a>')


def play_url(l):
    return f"{PLAY}&hl={l['hl']}"


def ticks(items):
    return '<ul class="ticks" role="list">' + "".join(f"<li>{ic('check')}<span>{esc(t)}</span></li>" for t in items) + "</ul>"


def captions(u):
    c = [x[0] for x in u["cards"]]
    return [c[0], u["n3"], c[1], c[3], c[5], c[4], u["mp3"], c[6]]


def render_main(l, s, u):
    d = img_dir(l)
    caps = captions(u)
    out = []
    # hero
    out.append(
        f'<section class="hero" id="download" aria-labelledby="hero-t"><div class="wrap hero-in">'
        f'<div class="hero-copy"><p class="eyebrow">{ic("check")}{esc(u["eyebrow"])}</p>'
        f'<h1 id="hero-t">{esc(s["title"])}</h1><p class="lead">{esc(s["intro"])}</p>'
        f'<div class="stores">{store_btn(l, u["geton"])}</div>'
        f'<ul class="trust">' + "".join(f'<li>{ic("check")}{esc(u[k])}</li>' for k in ("t1", "t2", "t3")) + "</ul></div>"
        f'<div class="hero-art"><svg class="ring" viewBox="0 0 100 100" aria-hidden="true"><defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B7A2FF"/><stop offset="1" stop-color="#FF8FC2"/></linearGradient></defs>'
        f'<circle cx="50" cy="50" r="46" fill="none" stroke="url(#rg)" stroke-width="2.2" stroke-linecap="round" pathLength="7" stroke-dasharray=".84 .16"/></svg>'
        f'<img class="banner" src="{d}/feature.webp" width="1024" height="500" alt="{esc(s["title"])}" fetchpriority="high" decoding="async"></div>'
        f"</div></section>")
    # features (v2.1)
    cards = []
    for k, (t, p) in enumerate(u["cards"]):
        pro = k == 5
        badge = f' <span class="badge">{esc(u["p_prem"])}</span>' if pro else ""
        cls = "card card-pro" if k in (5, 6) else "card"
        cards.append(f'<li class="{cls}"><span class="card-ic">{ic(CARD_ICONS[k])}</span><h3>{esc(t)}{badge}</h3><p>{esc(p)}</p></li>')
    out.append(
        f'<section class="sec" id="features" aria-labelledby="feat-t"><div class="wrap"><div class="sh"><p class="kicker">{esc(u["n1"])}</p>'
        f'<h2 id="feat-t">{esc(u["f_h"])}</h2></div><ul class="grid" role="list">{"".join(cards)}</ul></div></section>')
    # showcase
    thumbs = "".join(
        f'<li><button class="thumb" type="button" data-src="{d}/{n}.webp" data-cap="{esc(c)}" aria-label="{esc(c)}" aria-current="{"true" if n == 1 else "false"}">'
        f'<img src="{d}/{n}.webp" width="540" height="960" alt="" loading="lazy" decoding="async"></button></li>'
        for n, c in enumerate(caps, 1))
    out.append(
        f'<section class="sec sec-alt" id="preview" aria-labelledby="prev-t"><div class="wrap"><div class="sh"><p class="kicker">{esc(u["n2"])}</p>'
        f'<h2 id="prev-t">{esc(u["s_h"])}</h2></div><div class="show" data-show>'
        f'<div class="stage" role="group" aria-roledescription="carousel" aria-label="{esc(u["s_h"])}">'
        f'<div class="phone"><img src="{d}/1.webp" width="540" height="960" alt="{esc(caps[0])}" decoding="async"></div>'
        f'<div class="ctl"><button class="nb prev" type="button" aria-label="{esc(u["s_prev"])}">{ic("chev-l")}</button>'
        f'<p class="cap" aria-live="polite">{esc(caps[0])}</p>'
        f'<button class="nb next" type="button" aria-label="{esc(u["s_next"])}">{ic("chev-r")}</button></div></div>'
        f'<ul class="thumbs" role="list" aria-label="{esc(u["s_pick"])}">{thumbs}</ul></div></div></section>')
    # how to
    steps = "".join(f'<li><span class="num">{n}</span><p>{esc(t)}</p></li>' for n, t in enumerate(s["how"], 1))
    out.append(f'<section class="sec" id="how" aria-labelledby="how-t"><div class="wrap"><div class="sh"><h2 id="how-t">{esc(u["n3"])}</h2></div><ol class="steps">{steps}</ol></div></section>')
    # why / offline / extras (store copy)
    def lst(h, items):
        return f'<div class="card"><h3 class="k">{esc(h)}</h3>{ticks(items)}</div>'
    out.append(
        f'<section class="sec sec-alt" id="why" aria-labelledby="why-t"><div class="wrap"><div class="sh"><h2 id="why-t">{esc(u["m_h"])}</h2></div>'
        f'<div class="grid g3">{lst(s["why_h"], s["why"])}<div class="stack">{lst(s["off_h"], s["off"])}{lst(s["ext_h"], s["ext"])}</div>{lst(s["fair_h"], s["fair"])}</div></div></section>')
    # pricing
    out.append(
        f'<section class="sec" id="pricing" aria-labelledby="price-t"><div class="wrap"><div class="sh center"><p class="kicker">{esc(u["n4"])}</p><h2 id="price-t">{esc(u["p_h"])}</h2></div>'
        f'<div class="plans"><article class="plan"><h3>{esc(u["p_free"])}</h3>{ticks(s["fair"])}</article>'
        f'<article class="plan plan-pro"><h3>{ic("crown")}{esc(u["p_prem"])}</h3>{ticks(s["prem"])}</article></div>'
        f'<p class="fine center">{esc(s["prem_fine"])}</p></div></section>')
    # privacy
    out.append(
        f'<section class="sec sec-alt" id="privacy" aria-labelledby="priv-t"><div class="wrap"><div class="priv"><div class="priv-ic">{ic("shield")}</div>'
        f'<div><p class="kicker">{esc(s["priv_h"])}</p><h2 id="priv-t">{esc(u["v_h"])}</h2></div>'
        f'<div><p>{esc(s["priv"])}</p><p><a href="{PATH}snapclip-privacy-policy.html" hreflang="en">{esc(u["v_link"])}</a></p></div></div></div></section>')
    # faq
    faq = "".join(f'<details{" open" if i == 0 else ""}><summary>{esc(q)}{ic("chev-d", "chev")}</summary><p>{esc(a)}</p></details>' for i, (q, a) in enumerate(s["faq"]))
    out.append(f'<section class="sec" id="faq" aria-labelledby="faq-t"><div class="wrap narrow"><div class="sh"><h2 id="faq-t">{esc(u["q_h"])}</h2></div><div class="faq">{faq}</div></div></section>')
    # cta
    out.append(
        f'<section class="cta" aria-labelledby="cta-t"><div class="wrap cta-in"><img class="cta-icon" src="{PATH}assets/icon.svg" width="88" height="88" alt="" loading="lazy">'
        f'<h2 id="cta-t">{esc(u["c_h"])}</h2><p>{esc(u["c_p"])}</p><div class="stores">{store_btn(l, u["geton"])}</div></div></section>')
    return "".join(out)


def render_foot(l, s, u):
    return (
        f'<div class="wrap"><div class="foot-grid"><div><a class="brand" href="{PATH}"><img src="{PATH}assets/icon.svg" width="32" height="32" alt="" loading="lazy"><span>SnapClip</span></a><p>{esc(u["f_tag"])}</p></div>'
        f'<nav aria-label="{esc(u["fh_app"])}"><h2>{esc(u["fh_app"])}</h2><ul><li><a href="#features">{esc(u["n1"])}</a></li><li><a href="#pricing">{esc(u["n4"])}</a></li><li><a href="#faq">{esc(u["n5"])}</a></li>'
        f'<li><a href="{esc(play_url(l))}" data-play>Google Play</a></li></ul></nav>'
        f'<nav aria-label="{esc(u["fh_legal"])}"><h2>{esc(u["fh_legal"])}</h2><ul>'
        f'<li><a href="{PATH}snapclip-privacy-policy.html" hreflang="en">{esc(u["f_priv"])}</a></li>'
        f'<li><a href="{PATH}snapclip-terms-and-conditions.html" hreflang="en">{esc(u["f_terms"])}</a></li>'
        f'<li><a href="{PATH}snapclip-data-deletion.html" hreflang="en">{esc(u["f_del"])}</a></li></ul></nav>'
        f'<nav aria-label="{esc(u["fh_help"])}"><h2>{esc(u["fh_help"])}</h2><ul><li><a href="mailto:{EMAIL}">{esc(u["f_mail"])}</a></li><li><span dir="ltr">{EMAIL}</span></li></ul></nav></div>'
        f'<div class="foot-bottom"><span>© 2026 DuruSoft</span><p class="indep" id="independence">{esc(s["note"])}</p></div></div>')


def last_sentence(text):
    parts = [p for p in re.split(r"(?<=[.!?。！？])\s*", text.strip()) if p]
    return parts[-1] if parts else ""


def meta_for(l, s, u):
    desc = f'{s["short"]} {last_sentence(s["intro"])}'
    if len(desc) > 165:
        desc = s["short"]
    d = img_dir(l)
    image = ORIGIN + f"{d}/feature.webp"
    shots = [ORIGIN + f"{d}/{n}.webp" for n in range(1, 9)]
    app = {
        "@context": "https://schema.org", "@type": "MobileApplication", "name": f'SnapClip: {s["title"]}', "alternateName": ["SnapClip"],
        "description": s["short"], "url": abs_url(l["slug"]), "inLanguage": l["html"], "operatingSystem": "Android",
        "applicationCategory": "MultimediaApplication", "image": image, "screenshot": shots, "downloadUrl": PLAY,
        "author": {"@type": "Organization", "name": "DuruSoft"}, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
    }
    faq = {
        "@context": "https://schema.org", "@type": "FAQPage", "inLanguage": l["html"],
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in s["faq"]],
    }
    return dict(title=f'SnapClip: {s["title"]}', desc=desc, og_title=s["title"], og_desc=s["short"], image=image, image_alt=s["title"]), \
        [json.dumps(app, ensure_ascii=False, separators=(",", ":")), json.dumps(faq, ensure_ascii=False, separators=(",", ":"))]


HEADER_KEYS = ["skip", "n1", "n2", "n3", "n4", "n5", "dl", "lang", "geton", "eyebrow"]


def build_lang(l):
    s, u = store(l["code"]), UI[l["code"]]
    assert len(u["cards"]) == 8, l["code"]
    meta, ld = meta_for(l, s, u)
    return dict(
        slug=l["slug"], meta=meta, ld=ld, play=play_url(l),
        ui={k: u[k] for k in HEADER_KEYS}, main=render_main(l, s, u), foot=render_foot(l, s, u)), s, u


def render_index(en, s, u):
    l = LANGS[0]
    m = en["meta"]
    hreflang = "".join(f'<link rel="alternate" hreflang="{x["hreflang"]}" href="{abs_url(x["slug"])}">' for x in LANGS)
    hreflang += f'<link rel="alternate" hreflang="x-default" href="{abs_url("en")}">'
    switcher = "".join(
        f'<li><a href="{PATH}?lang={x["slug"]}" data-slug="{x["slug"]}" hreflang="{x["html"]}" lang="{x["html"]}" translate="no"'
        f'{" aria-current=\"true\"" if x["slug"] == "en" else ""}><span>{esc(x["name"])}</span>{ic("check")}</a></li>' for x in LANGS)
    nav = "".join(f'<a href="#{h}" data-i="{k}">{esc(u[k])}</a>' for h, k in (("features", "n1"), ("preview", "n2"), ("how", "n3"), ("pricing", "n4"), ("faq", "n5")))
    return f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(m["title"])}</title>
<meta name="description" content="{esc(m["desc"])}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#F6F4FB" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0D0C14" media="(prefers-color-scheme: dark)">
<link rel="canonical" href="{abs_url("en")}">
{hreflang}
<meta property="og:type" content="website">
<meta property="og:site_name" content="SnapClip">
<meta property="og:url" content="{abs_url("en")}">
<meta property="og:title" content="{esc(m["og_title"])}">
<meta property="og:description" content="{esc(m["og_desc"])}">
<meta property="og:image" content="{m["image"]}">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="500">
<meta property="og:image:alt" content="{esc(m["image_alt"])}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(m["og_title"])}">
<meta name="twitter:description" content="{esc(m["og_desc"])}">
<meta name="twitter:image" content="{m["image"]}">
<meta name="twitter:image:alt" content="{esc(m["image_alt"])}">
<link rel="icon" href="{PATH}assets/icon.svg" type="image/svg+xml">
<link rel="icon" href="{PATH}assets/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="{PATH}assets/apple-touch-icon.png">
<link rel="manifest" href="{PATH}assets/site.webmanifest">
<script type="application/ld+json">{en["ld"][0]}</script>
<script type="application/ld+json">{en["ld"][1]}</script>
<link rel="stylesheet" href="{PATH}assets/site.css?v={VERSION}">
</head>
<body>
{SPRITE}
<a class="skip" href="#main" data-i="skip">{esc(u["skip"])}</a>
<header class="top"><div class="wrap top-in">
  <a class="brand" href="{PATH}" aria-label="SnapClip"><img src="{PATH}assets/icon.svg" width="34" height="34" alt=""><span>SnapClip</span></a>
  <nav class="nav" aria-label="SnapClip">{nav}</nav>
  <span class="spacer"></span>
  <details class="menu lang">
    <summary class="btn btn-ghost" aria-label="{esc(u["lang"])}" data-ai="lang">{ic("globe")}<span class="cur">English</span>{ic("chev-d", "chev")}</summary>
    <div class="panel"><ul role="list">{switcher}</ul></div>
  </details>
  <details class="menu get">
    <summary class="btn btn-sm" data-i="dl">{esc(u["dl"])}</summary>
    <div class="panel"><p class="get-title">SnapClip</p><p class="get-sub" data-i="eyebrow">{esc(u["eyebrow"])}</p><div class="stores">{store_btn(l, u["geton"], True)}</div></div>
  </details>
</div></header>
<main id="main">{en["main"]}</main>
<footer class="foot" id="foot">{en["foot"]}</footer>
<script src="{PATH}assets/site.js?v={VERSION}" defer></script>
</body>
</html>
'''


def sitemap_entries():
    alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x["hreflang"]}" href="{abs_url(x["slug"])}"/>' for x in LANGS)
    alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("en")}"/>'
    return "\n".join(f"<url><loc>{abs_url(x['slug'])}</loc><lastmod>{LASTMOD}</lastmod>{alts}</url>" for x in LANGS)


def main():
    (SITE / "assets/i18n").mkdir(parents=True, exist_ok=True)
    built = {}
    for l in LANGS:
        data, s, u = build_lang(l)
        built[l["slug"]] = (data, s, u)
        (SITE / "assets/i18n" / f"{l['slug']}.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    en, s, u = built["en"]
    (SITE / "index.html").write_text(render_index(en, s, u), encoding="utf-8")
    table = [dict(slug=x["slug"], html=x["html"], hreflang=x["hreflang"], dir=x["dir"], og=x["og"], name=x["name"]) for x in LANGS]
    js = (HERE / "site.js.tpl").read_text(encoding="utf-8").replace("__LANGS__", json.dumps(table, ensure_ascii=False)).replace("__V__", VERSION)
    (SITE / "assets/site.js").write_text(js, encoding="utf-8")
    entries = sitemap_entries()
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + entries + "\n"
        + "\n".join(f"<url><loc>{ORIGIN}{PATH}{p}</loc><lastmod>{LASTMOD}</lastmod></url>" for p in ("snapclip-privacy-policy.html", "snapclip-terms-and-conditions.html", "snapclip-data-deletion.html"))
        + "\n</urlset>\n", encoding="utf-8")
    root_map = ROOT / "sitemap.xml"
    txt = root_map.read_text(encoding="utf-8")
    pat = re.compile(r"<url><loc>https://mehmetth\.github\.io/snapclip/</loc>.*?</url>(?:\n<url><loc>https://mehmetth\.github\.io/snapclip/\?lang=[^<]*</loc>.*?</url>)*")
    assert pat.search(txt), "snapclip entry not found in root sitemap"
    root_map.write_text(pat.sub(lambda _m: entries, txt, count=1), encoding="utf-8")
    manifest = SITE / "assets/site.webmanifest"
    mj = json.loads(manifest.read_text(encoding="utf-8"))
    mj["name"] = "SnapClip: Video Downloader No Watermark"
    manifest.write_text(json.dumps(mj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("built", len(LANGS), "languages;", "index.html", (SITE / "index.html").stat().st_size, "bytes")


if __name__ == "__main__":
    main()
