"""Render the policy connection network as one page.

The chain pages answer "how does THIS policy reach statute". This answers a
different question: what does the corpus look like as a whole, and where is
it dense or thin.

Drawn as inline SVG with no script and no external dependency, so it works
from a file:// URL, survives being emailed as a single file, and prints. A
force-directed graph would look livelier and say less - the one thing a
reader needs from this picture is WHICH TIER a document sits in, so tier is
the vertical axis and nothing is left to a physics simulation.

Accessibility is not an afterthought here. An SVG network is invisible to a
screen reader no matter how well it is labelled, so the same data is emitted
below it as a table, and the SVG carries role="img" with a description that
states what the picture shows rather than describing its geometry.
"""

import argparse
import json
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_authority_chain import (CSS, TIER_NAME, TIER_ORDER,   # noqa: E402
                                    tier_of, esc, load, TIER_RX, HOLDS_RX,
                                    PROGRAMME_P)
from render_policy import EXTRA_CSS, page_name                    # noqa: E402

CONN_CSS = """
.viz{border:1px solid var(--border);border-radius:12px;background:var(--sunken);
padding:10px;overflow-x:auto}
.viz svg{display:block;min-width:900px;height:auto}
.key{display:flex;flex-wrap:wrap;gap:16px;margin:12px 0 0;font-size:13px;
color:var(--mutedfg)}
.key span.sw{display:inline-block;width:22px;height:0;border-top-width:2px;
border-top-style:solid;vertical-align:middle;margin-right:6px}
.statgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(11rem,1fr));
gap:10px;margin:14px 0}
.stat{border:1px solid var(--border);border-radius:12px;background:var(--card);
padding:12px 14px}
.stat .n{font:700 24px/1.1 inherit;color:var(--brass3)}
.stat .l{font-size:12px;color:var(--mutedfg)}
"""

EDGE_STYLE = {
    "high": ("#2F8F5C", "resolves in store"),
    "revision-drift": ("#C97D1F", "names an edition the store does not hold"),
    "named-not-held": ("#B83232", "named, not held"),
}
W, ROW_H, PAD_X, PAD_TOP = 1180, 118, 44, 46
R = 5.5


def layout(records):
    """Tier on the vertical axis, alphabetical within it.

    Deterministic by construction - the same store produces the same picture
    every time, which matters when the page is regenerated on every build.
    """
    tiers = {}
    for did, rec in records.items():
        tiers.setdefault(tier_of(did, rec), []).append(did)
    rows = [t for t in TIER_ORDER + ["TX"] if tiers.get(t)]
    pos = {}
    for r, tier in enumerate(rows):
        ids = sorted(tiers[tier])
        n = len(ids)
        y = PAD_TOP + r * ROW_H + 34
        span = W - 2 * PAD_X
        for i, did in enumerate(ids):
            x = PAD_X + (span * (i + 0.5) / n if n else span / 2)
            pos[did] = (x, y, tier)
    height = PAD_TOP + len(rows) * ROW_H + 30
    return pos, rows, tiers, height


def edges_of(records, pos):
    out = []
    for src, rec in records.items():
        for m in rec.get("relationships", {}).get("edge_meta", []) or []:
            if m.get("rel") != "references":
                continue
            tgt = m["target"]
            if src not in pos:
                continue
            conf = m.get("confidence", "named-not-held")
            t = TIER_RX.search(m.get("resolution", ""))
            tier = t.group(1) if t else tier_of(tgt, records.get(tgt))
            out.append({"src": src, "tgt": tgt, "conf": conf, "tier": tier,
                        "held": tgt in pos})
    return out


def svg(records, pos, rows, tiers, height, edges):
    # No height attribute. With a viewBox and width:100%, a fixed height
    # forces a letterbox on any container narrower than W.
    P = [f'<svg viewBox="0 0 {W} {height}" width="100%" '
         f'role="img" aria-labelledby="viztitle vizdesc" '
         f'xmlns="http://www.w3.org/2000/svg">',
         '<title id="viztitle">Policy connection network</title>',
         f'<desc id="vizdesc">A network of {len(pos)} documents in '
         f'{len(rows)} tiers, statute at the top and messages at the bottom, '
         f'joined by {len(edges)} cited references. Line colour states whether '
         f'the reference resolves to a document the corpus holds, names an '
         f'edition it no longer holds, or names one it never held. The same '
         f'data is listed as a table below this figure.</desc>']

    # tier bands and labels
    for r, tier in enumerate(rows):
        y = PAD_TOP + r * ROW_H
        P.append(f'<rect x="0" y="{y - 16}" width="{W}" height="{ROW_H - 6}" '
                 f'fill="#11203F" opacity="0.34" rx="8"/>')
        P.append(f'<text x="{PAD_X - 30}" y="{y + 4}" fill="#D4AF67" '
                 f'font-family="monospace" font-size="12" font-weight="700">'
                 f'{tier}</text>')
        P.append(f'<text x="{PAD_X}" y="{y + 4}" fill="#B5A988" '
                 f'font-family="sans-serif" font-size="11" '
                 f'letter-spacing="1.4">{esc(TIER_NAME.get(tier, tier).upper())} '
                 f'&#183; {len(tiers[tier])}</text>')

    # edges first so nodes sit on top
    for e in edges:
        if not e["held"] or e["tgt"] not in pos:
            continue
        x1, y1, _ = pos[e["src"]]
        x2, y2, _ = pos[e["tgt"]]
        colour = EDGE_STYLE.get(e["conf"], EDGE_STYLE["named-not-held"])[0]
        # a gentle arc so parallel edges between the same two tiers separate
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * 0.10
        P.append(f'<path d="M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} '
                 f'{x2:.1f},{y2:.1f}" fill="none" stroke="{colour}" '
                 f'stroke-width="1.1" opacity="0.5"/>')

    # unresolved edges as short stubs pointing off the top of their tier
    for e in edges:
        if e["held"]:
            continue
        x1, y1, _ = pos[e["src"]]
        colour = EDGE_STYLE.get(e["conf"], EDGE_STYLE["named-not-held"])[0]
        P.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x1:.1f}" '
                 f'y2="{y1 - 15:.1f}" stroke="{colour}" stroke-width="1" '
                 f'opacity="0.42" stroke-dasharray="2 2"/>')

    degree = Counter()
    for e in edges:
        degree[e["src"]] += 1
        if e["held"]:
            degree[e["tgt"]] += 1

    for did, (x, y, tier) in pos.items():
        rec = records[did]
        st = rec.get("status")
        fill = ("#B83232" if st == "cancelled" else
                "#C97D1F" if st == "superseded" else "#6B9BD2")
        rad = R + min(4.5, math.sqrt(degree.get(did, 0)) * 1.1)
        P.append(f'<a href="{esc(page_name(did))}">'
                 f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rad:.1f}" '
                 f'fill="{fill}" stroke="#0A1424" stroke-width="1.4">'
                 f'<title>{esc(rec.get("title") or did)} &#8212; {esc(st or "")}'
                 f', {degree.get(did, 0)} connection(s)</title></circle></a>')

    # label the highest-degree node in each tier, so the picture has anchors
    for tier in rows:
        ids = [d for d in tiers[tier] if d in pos]
        if not ids:
            continue
        top = max(ids, key=lambda d: degree.get(d, 0))
        if degree.get(top, 0) < 3:
            continue
        x, y, _ = pos[top]
        P.append(f'<text x="{x:.1f}" y="{y - 12:.1f}" fill="#F2E5BE" '
                 f'font-family="monospace" font-size="10" '
                 f'text-anchor="middle">{esc(top)}</text>')

    P.append("</svg>")
    return "\n".join(P), degree


def render(records, out_path):
    pos, rows, tiers, height = layout(records)
    edges = edges_of(records, pos)
    fig, degree = svg(records, pos, rows, tiers, height, edges)

    held = sum(1 for e in edges if e["conf"] == "high")
    drift = sum(1 for e in edges if e["conf"] == "revision-drift")
    gap = sum(1 for e in edges if e["conf"] == "named-not-held")
    internal = sum(1 for e in edges if e["held"])
    isolated = [d for d in pos if degree.get(d, 0) == 0]

    P = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>Policy connections - Semper Admin Policy Library</title>',
         f"<style>{CSS}{EXTRA_CSS}{CONN_CSS}</style></head><body>",
         '<a class="skip" href="#main">Skip to main content</a>',
         '<header class="chrome"><a class="wordmark" href="index.html">'
         'Semper Admin</a><span>Connections</span>'
         '<a href="policy-index.html" style="margin-left:auto">All policies</a>'
         '<a href="authority-index.html">Authority chains</a>'
         '<a href="sources.html">Sources</a></header>',
         '<main id="main"><h1>Policy connections</h1>',
         '<p class="lede">Every document in the set and every cited reference '
         'between them. Statute at the top, messages at the bottom, and each '
         'document sitting in the tier that issued it. A line exists only '
         'where the issuing authority printed the reference - nothing here is '
         'inferred from subject matter or numbering.</p>',
         '<div class="statgrid">'
         + f'<div class="stat"><div class="n">{len(pos)}</div>'
           f'<div class="l">documents</div></div>'
         + f'<div class="stat"><div class="n">{len(edges)}</div>'
           f'<div class="l">cited references</div></div>'
         + f'<div class="stat"><div class="n">{internal}</div>'
           f'<div class="l">joining two documents in the set</div></div>'
         + f'<div class="stat"><div class="n">{drift}</div>'
           f'<div class="l">naming a superseded edition</div></div>'
         + f'<div class="stat"><div class="n">{gap}</div>'
           f'<div class="l">naming a document not held</div></div>'
         + '</div>',
         '<div class="viz">' + fig + '</div>',
         '<div class="key">'
         + "".join(f'<span><span class="sw" style="border-top-color:{c}">'
                   f'</span>{esc(lbl)}</span>'
                   for c, lbl in EDGE_STYLE.values())
         + '<span>Node size is the number of connections. '
           'Red is cancelled, amber superseded, blue active. '
           'A dashed stub is a reference to a document outside this set.</span>'
         + '</div>']

    P.append('<h2>How to read the shape</h2>')
    P.append('<p class="lede">Two things are visible here that no single '
             'document page shows. The first is where the corpus is thin: a '
             'tier with few nodes and few lines into it is a tier the corpus '
             'barely holds, and the dashed stubs are the references running '
             'off the edge of what was collected. The second is which '
             'documents carry the traffic - node size is connection count, so '
             'the hubs are visible without reading a single title.</p>')

    if isolated:
        P.append(f'<p class="lede">{len(isolated)} document(s) in this set have '
                 f'no cited connection to any other document in it: '
                 + ", ".join(f'<a href="{esc(page_name(d))}">{esc(d)}</a>'
                             for d in sorted(isolated)[:12])
                 + (', and others' if len(isolated) > 12 else '')
                 + '. That is a statement about the demonstration set, not '
                   'about the policies.</p>')

    # accessible equivalent
    P.append('<h2>The same data as a table</h2>')
    P.append('<p class="lede">An SVG network is invisible to a screen reader '
             'however well it is labelled, so every connection in the figure '
             'is listed here.</p>')
    P.append('<table><tr><th>Tier</th><th>Document</th><th>Connections</th>'
             '<th>Names</th></tr>')
    for tier in rows:
        for did in sorted(tiers[tier]):
            rec = records[did]
            outs = [m["target"] for m in
                    rec.get("relationships", {}).get("edge_meta", []) or []
                    if m.get("rel") == "references"]
            shown = ", ".join(
                f'<a href="{esc(page_name(t))}">{esc(t)}</a>' if t in pos
                else f"<code>{esc(t)}</code>" for t in sorted(outs)[:10])
            if len(outs) > 10:
                shown += f' and {len(outs) - 10} more'
            P.append(f'<tr><td><code>{esc(tier)}</code></td>'
                     f'<td><a href="{esc(page_name(did))}">'
                     f'{esc(rec.get("title") or did)}</a></td>'
                     f'<td>{degree.get(did, 0)}</td>'
                     f'<td class="small">{shown or "&mdash;"}</td></tr>')
    P.append('</table>')
    P.append('<footer><p>Generated from the canonical store. Every edge is '
             'cited and names the paragraph it was read from; open a document '
             'to see it. Records are UNVERIFIED machine extractions unless '
             f'promoted.</p>{PROGRAMME_P}</footer></main></body></html>')

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(P))
    return {"docs": len(pos), "edges": len(edges), "internal": internal,
            "drift": drift, "gap": gap, "isolated": len(isolated),
            "tiers": len(rows)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="canonical_staging")
    ap.add_argument("--out", default="demo_site")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    records = load(args.store)
    st = render(records, os.path.join(args.out, "connections.html"))
    print(f"connections.html: {st['docs']} documents across {st['tiers']} tiers, "
          f"{st['edges']} edges ({st['internal']} internal, {st['drift']} drift, "
          f"{st['gap']} not held), {st['isolated']} isolated")


if __name__ == "__main__":
    main()
