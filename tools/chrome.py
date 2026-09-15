"""The site chrome, in one place.

Every generated page gets its <head>, header, brand block, and navigation from
here, and nothing else emits a wordmark, a nav link, or a copy of the chrome
CSS. Before 2026-09-11 the header was a literal in five renderers and four hand
pages, and a measurement found ten distinct header link sets across 78 pages.
Same defect shape as the four-copy CSS trap in SESSION_HANDOFF.md section 10:
decide it once. ACTION-REGISTER 5.1.

The navigation is data: config/site_nav.json. A page is listed there only once
it exists in docs/, because check_site.py fails the build on a dead link.

Usage from a renderer:

    from chrome import head, header
    P = [head("Authority chains", extra_css=INDEX_CSS_EXTRA),
         header("Authority chains", current="authority-index.html"),
         '<main id="main">', ...]
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAV_PATH = ROOT / "config" / "site_nav.json"
SITE_TITLE = "Semper Admin Policy Library"

NAV = json.loads(NAV_PATH.read_text(encoding="utf-8"))

# Tab icon, one definition for every page head. The SVG is the icon;
# the PNG is the fallback for browsers that do not take SVG favicons.
FAVICON = ('<link rel="icon" href="favicon.svg" type="image/svg+xml">\n'
           '<link rel="alternate icon" href="favicon.png">')

# The brand block. Wordmark and eyebrow come from the nav file.
BRAND = ('<div class="brand">'
         f'<a class="wordmark" href="{html.escape(NAV["home"]["href"])}">'
         f'{html.escape(NAV["home"]["label"])}</a>'
         f'<span class="eyebrow">{html.escape(NAV["home"]["eyebrow"])}</span></div>')

# The portal emblem, left of the brand, opening in a new tab.
EMBLEM = (f'<a class="emblem" href="{html.escape(NAV["emblem"]["href"])}" target="_blank" '
          f'rel="noopener noreferrer" title="{html.escape(NAV["emblem"]["alt"])}">'
          f'<img src="{html.escape(NAV["emblem"]["src"])}" '
          f'alt="{html.escape(NAV["emblem"]["alt"])}" height="40"></a>')

# Kept for callers that import it by name. The rules are inside CSS below.
BRAND_CSS = ('.brand{display:flex;flex-direction:column;align-items:flex-start}'
             '.brand .eyebrow{margin-top:2px}')

CSS = """
:root{--scarlet:#B82230;--scarlet3:#D14150;--blue:#0F1F3D;--blue3:#2A3D60;
--blue1:#6B9BD2;--parch:#F2E5BE;--parch3:#FAF1D8;--brass:#B89042;
--brass3:#D4AF67;--fresh:#2F8F5C;--aging:#C97D1F;--stale:#B83232;
--bg:#0A1424;--elev:#11203F;--sunken:#060E1A;--fg:#F2E5BE;--card:#11203F;
--muted:#182A4D;--mutedfg:#B5A988;--border:#233A5C;--borders:#34507A;
--n950:#0F0C09;--rad:8px;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:400 15px/1.6 "Inter Variable",Inter,system-ui,sans-serif}
a{color:var(--blue1)}a:hover{color:var(--brass3)}
:focus-visible{outline:3px solid var(--brass3);outline-offset:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{position:static;display:inline-block;padding:8px;
background:var(--brass3);color:var(--n950)}
header.chrome,main,footer{max-width:64rem;margin:0 auto;padding:16px 24px}
header.chrome{margin-top:16px;border-radius:12px;border:1px solid var(--border);
background:var(--elev);display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.brand{display:flex;flex-direction:column;align-items:flex-start}
.brand .eyebrow{margin-top:2px}
.eyebrow{font:700 11px/1 inherit;text-transform:uppercase;letter-spacing:.08em;
color:var(--mutedfg)}
header.chrome a[aria-current="page"]{color:var(--parch3);text-decoration-thickness:2px}
.emblem{align-self:center;display:flex}
.wordmark{font:400 28px/1.2 "Bebas Neue",Oswald,system-ui,sans-serif;
letter-spacing:.04em;color:var(--parch3);text-decoration:none;text-transform:uppercase}
h1{font:700 28px/1.2 inherit;margin:32px 0 8px}
h2{font:700 20px/1.2 inherit;border-bottom:1px solid var(--borders);
padding-bottom:8px;margin-top:40px}
.lede{color:var(--mutedfg);max-width:52rem}
.tier{border:1px solid var(--border);border-radius:12px;background:var(--card);
margin:0 0 4px;padding:16px 20px}
.tier.gap{background:repeating-linear-gradient(135deg,var(--sunken),
var(--sunken) 10px,#0b1830 10px,#0b1830 20px);border-style:dashed;
border-color:var(--aging)}
.tierhead{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;
font:700 11px/1 inherit;text-transform:uppercase;letter-spacing:.09em;
color:var(--mutedfg);margin-bottom:10px}
.tiercode{color:var(--brass3);font-weight:700}
.doc{margin:10px 0 0;padding:10px 0 0;border-top:1px solid var(--muted)}
.doc:first-of-type{border-top:0;padding-top:0}
.docid{font:600 14px/1.4 "JetBrains Mono",Menlo,monospace;color:var(--parch3)}
.doctitle{color:var(--fg)}
.uslm{font:500 12px/1.5 "JetBrains Mono",Menlo,monospace;color:var(--brass3);
word-break:break-all}
.why{font-size:13px;color:var(--mutedfg);margin-top:4px}
.pill{display:inline-block;padding:2px 9px;border-radius:9999px;
font:700 11px/1.6 inherit;border:1px solid var(--borders);
background:var(--muted);color:var(--parch3);white-space:nowrap}
.pill.cited{border-color:var(--fresh);color:#9fe0bd}
.pill.drift{border-color:var(--aging);color:#f0c489}
.pill.gap{border-color:var(--stale);color:#f3a3a3}
.pill.held{border-color:var(--blue1);color:#bcd7f2}
.pill.cancelled,.pill.superseded{background:var(--stale);border-color:var(--stale);
color:#fff}
.arrow{text-align:center;color:var(--brass);font:700 13px/1 inherit;
padding:6px 0;letter-spacing:.08em}
.arrow span{background:var(--bg);padding:0 10px}
.arrow{position:relative}
.arrow:before{content:"";position:absolute;left:50%;top:0;bottom:0;width:1px;
background:var(--brass);z-index:-1}
table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px}
th,td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--muted);
vertical-align:top}
th{color:var(--mutedfg);font-size:11px;text-transform:uppercase;
letter-spacing:.08em}
code{font:500 12px/1.5 "JetBrains Mono",Menlo,monospace;color:var(--brass3)}
footer{border-top:1px solid var(--border);margin-top:48px;font-size:13px;
color:var(--mutedfg)}
/* Small screens: the chrome stacks - wordmark row, page label, then nav links
   as wrapping pill targets (the inline margin-left:auto that right-aligns the
   first link on desktop needs the !important to release). Wide tables scroll
   in place instead of stretching the page, and long identifiers break. */
@media (max-width:640px){
header.chrome{align-items:center;column-gap:12px;row-gap:8px;padding:12px 16px}
.wordmark{font-size:22px}
header.chrome span{flex-basis:100%;order:2;font:700 11px/1 inherit;
text-transform:uppercase;letter-spacing:.08em;color:var(--mutedfg)}
header.chrome a:not(.wordmark):not(.emblem){order:3;margin-left:0!important;
font:600 13px/1.1 inherit;padding:8px 12px;border:1px solid var(--borders);
border-radius:9999px;background:var(--muted);color:var(--parch3);
text-decoration:none}
table{display:block;overflow-x:auto}
code,h3{overflow-wrap:anywhere}
}
"""


def esc_title(s) -> str:
    return html.escape(str(s or ""), quote=True)


def head(title: str, extra_css: str = "") -> str:
    """Doctype through the skip link. The caller opens <main>."""
    return ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'{FAVICON}'
            f'<title>{esc_title(title)} - {SITE_TITLE}</title>'
            f'<style>{CSS}{extra_css}</style></head><body>'
            '<a class="skip" href="#main">Skip to main content</a>')


def header(label: str, current: str | None = None) -> str:
    """The chrome header: emblem, brand, page label, then every nav item.
    `current` is the href of the page being rendered; that link is marked
    aria-current so a reader and a screen reader both know where they are."""
    links = []
    for i, item in enumerate(NAV["items"]):
        attrs = ' style="margin-left:auto"' if i == 0 else ""
        if item.get("external"):
            attrs += ' rel="noopener"'
        if current and item["href"] == current:
            attrs += ' aria-current="page"'
        links.append(f'<a href="{html.escape(item["href"])}"{attrs}>'
                     f'{html.escape(item["label"])}</a>')
    return (f'<header class="chrome">{EMBLEM}{BRAND}'
            f'<span class="eyebrow">{html.escape(label)}</span>'
            + "".join(links) + '</header>')
