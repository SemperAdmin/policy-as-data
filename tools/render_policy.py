"""One policy, three dimensions, one page.

Until now the library answered each question on a different page. What does
this order say? A document page. What governs it? A chain page. What came
before it? A lineage page. A Marine holding a question does not experience
those as three questions, and splitting them made the connection between
them the reader's job.

This renders one page per policy carrying all three, in the order a reader
actually needs them - the text first, because the text is what the page was
opened for; the authority and the lineage read as context after it:

    WHAT IT SAYS       the provision tree, with every reference resolving
    WHERE IT SITS      the authority above it and the traffic below it
    WHAT CAME BEFORE   editions, change packages, supersession, reverse drift

The third section is where the concepts join. A reference-list item is not
printed as text - it is printed as a link to the policy it names, carrying
its tier and whether the corpus holds it. Clicking (h) in MCO 1050.3J's
reference list lands on the DoD instruction that governs leave. That is the
whole thesis on one screen: the document, its place in the hierarchy, and its
history, addressable down to the paragraph.
"""

import argparse
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lineage import (build, build_inbound, load_families,      # noqa: E402
                     base_id, revision_letter, change_number)
from render_authority_chain import (BRAND, CSS, TIER_NAME, TIER_OF_TYPE,  # noqa: E402
                                    TIER_ORDER, tier_of, esc, load,
                                    SRC_RX, HOLDS_RX, TIER_RX, FAVICON)

EXTRA_CSS = """
.crumb{font-size:13px;color:var(--mutedfg);margin:24px 0 0}
.ident{font:500 12px/1.6 "JetBrains Mono",Menlo,monospace;color:var(--brass3);
word-break:break-all}
.factrow{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 0}
.lede2{color:var(--mutedfg);max-width:54rem;margin:6px 0 18px}
.ladder{border-left:2px solid var(--brass);margin:0 0 4px 10px;padding:0 0 0 18px}
.rung{position:relative;padding:9px 0}
.rung:before{content:"";position:absolute;left:-24px;top:16px;width:12px;
height:2px;background:var(--brass)}
.rung .t{font:700 11px/1 inherit;letter-spacing:.09em;color:var(--brass3);
text-transform:uppercase}
.rung.gaprung{opacity:.72}
.rung.gaprung .t{color:var(--aging)}
.small{font-size:13px;color:var(--mutedfg)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:820px){.two{grid-template-columns:1fr}}
.panel{border:1px solid var(--border);border-radius:12px;background:var(--card);
padding:16px 20px}
.panel h3{font:700 12px/1.3 inherit;text-transform:uppercase;letter-spacing:.09em;
color:var(--mutedfg);margin:0 0 10px}
.prov{border-left:1px solid var(--muted);margin:0 0 0 4px;padding:2px 0 2px 14px}
.plabel{font:600 12px/1.6 "JetBrains Mono",Menlo,monospace;color:var(--brass3)}
.ptext{white-space:pre-wrap;overflow-wrap:break-word}
.reflist{list-style:none;padding:0;margin:0}
.reflist li{padding:7px 0;border-bottom:1px solid var(--muted)}
.reflist li:last-child{border-bottom:0}
.reflink{font-weight:600}
.timeline{list-style:none;padding:0;margin:0}
.timeline li{padding:8px 0 8px 16px;border-left:2px solid var(--border);
position:relative}
.timeline li:before{content:"";position:absolute;left:-5px;top:15px;width:8px;
height:8px;border-radius:50%;background:var(--brass)}
.timeline li.now:before{background:var(--fresh);box-shadow:0 0 0 3px rgba(47,143,92,.25)}
.timeline li.gone:before{background:var(--stale)}
details.body{margin-top:10px}
details.body summary{cursor:pointer;color:var(--blue1);font-weight:600}
.src{font:500 11px/1.6 "JetBrains Mono",Menlo,monospace;color:var(--mutedfg)}
.doc-raw{white-space:pre-wrap;overflow-wrap:break-word;
font:500 12px/1.65 "JetBrains Mono",Menlo,monospace;color:var(--fg);
background:var(--sunken);border:1px solid var(--border);border-radius:8px;
padding:14px;max-height:34rem;overflow:auto}
.typegrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));
gap:10px;margin:12px 0}
.typecard{border:1px solid var(--border);border-radius:12px;background:var(--card);
padding:14px 16px}
.typecard .n{font:700 26px/1.1 inherit;color:var(--brass3)}
"""

MESSAGE_TYPES = {"MARADMIN", "ALMAR", "ALNAV"}
HELD_PILL = {"high": ("held", "in store"), "revision-drift": ("drift", "drift"),
             "named-not-held": ("gap", "not held")}


def page_name(doc_id):
    return f"policy-{doc_id}.html"


def link_or_text(doc_id, records, pages, label=None):
    label = label or doc_id
    if doc_id in pages:
        return f'<a href="{esc(page_name(doc_id))}">{esc(label)}</a>'
    return f"<code>{esc(label)}</code>"


def pill(cls, text):
    return f'<span class="pill {cls}">{esc(text)}</span>'


# ---------------------------------------------------------------------------
# Section 1 - where it sits


def authority_section(rec, records, pages, inbound, gaps):
    did = rec["id"]
    out = ['<h2>Where this sits</h2>',
           '<p class="lede2">The ladder above is what governs this policy, one '
           'tier at a time. Every rung exists because this document, or one '
           'above it, printed the reference. A tier the corpus does not hold '
           'is shown rather than skipped.</p>']

    # upward - group this record's outbound reference edges by tier
    by_tier = {}
    for m in rec.get("relationships", {}).get("edge_meta", []) or []:
        if m.get("rel") != "references":
            continue
        t = TIER_RX.search(m.get("resolution", ""))
        tier = t.group(1) if t else tier_of(m["target"], records.get(m["target"]))
        by_tier.setdefault(tier, []).append(m)

    self_tier = tier_of(did, rec)
    self_idx = TIER_ORDER.index(self_tier) if self_tier in TIER_ORDER else 99

    out.append('<div class="ladder">')
    shown = 0
    for tier in TIER_ORDER:
        if TIER_ORDER.index(tier) >= self_idx:
            break
        edges = by_tier.get(tier, [])
        if not edges:
            if tier in gaps:
                out.append(
                    f'<div class="rung gaprung"><div class="t">{tier} '
                    f'{esc(TIER_NAME[tier])} {pill("gap", "tier not held")}</div>'
                    f'<div class="small">{esc(gaps[tier])}</div></div>')
            continue
        shown += 1
        out.append(f'<div class="rung"><div class="t">{tier} '
                   f'{esc(TIER_NAME[tier])}</div>')
        for m in sorted(edges, key=lambda e: e["target"]):
            cls, txt = HELD_PILL.get(m.get("confidence"), ("", ""))
            holds = HOLDS_RX.search(m.get("resolution", ""))
            src = SRC_RX.search(m.get("resolution", ""))
            tgt = records.get(m["target"]) or {}
            out.append(
                f'<div style="padding:3px 0">'
                f'{link_or_text(m["target"], records, pages)} '
                + (pill(cls, txt) if txt else "")
                + (f' <span class="small">holds '
                   f'<code>{esc(holds.group(1))}</code></span>' if holds else "")
                + (f'<div class="small">{esc(tgt.get("title", "")[:110])}</div>'
                   if tgt.get("title") else "")
                + (f'<div class="src">named at {esc(src.group(1).strip())} '
                   f'&middot; cited</div>' if src else "")
                + "</div>")
        out.append("</div>")

    # this document
    out.append(f'<div class="rung"><div class="t">{self_tier} '
               f'{esc(TIER_NAME.get(self_tier, self_tier))} &middot; this document'
               f'</div><div><strong>{esc(rec.get("title") or did)}</strong></div>'
               f'</div>')

    # downward - who cites this
    citers = [e for e in inbound.get(did, []) if e["rel"] == "references"]
    if citers:
        msgs = [e for e in citers if (records.get(e["src"]) or {}).get("doc_type")
                in MESSAGE_TYPES]
        others = [e for e in citers if e not in msgs]
        out.append('<div class="rung"><div class="t">Below &middot; '
                   f'{len(citers)} document(s) name this one</div>')
        for e in sorted(citers, key=lambda e: e["src"], reverse=True)[:8]:
            src = SRC_RX.search(e.get("resolution", ""))
            out.append(
                f'<div style="padding:3px 0">'
                f'{link_or_text(e["src"], records, pages)}'
                + (f'<div class="small">{esc((e.get("src_title") or "")[:110])}'
                   f'</div>' if e.get("src_title") else "")
                + (f'<div class="src">names it at {esc(src.group(1).strip())}'
                   f'</div>' if src else "")
                + "</div>")
        if len(citers) > 8:
            out.append(f'<div class="small">and {len(citers) - 8} more, '
                       f'{len(msgs)} of them messages</div>')
        out.append("</div>")
    out.append("</div>")
    return out


# ---------------------------------------------------------------------------
# Section 2 - what came before


def lineage_section(rec, tracks, records, pages):
    did = rec["id"]
    out = ['<h2>What came before</h2>']
    any_track = any([tracks["curated"], tracks["editions"], tracks["changes"],
                     tracks["supersession"], tracks["reverse_drift"]])
    if not any_track:
        out.append('<p class="lede2">The corpus holds one edition of this '
                   'policy and no document cites an earlier one. That is the '
                   'honest answer, not a missing feature: a superseded edition '
                   'is usually gone from the publisher\'s site before a scraper '
                   'reaches it.</p>')
    else:
        out.append('<p class="lede2">Assembled from four independent signals. '
                   'Each row says which one produced it, because a curated '
                   'family, a change package, a supersession edge, and an '
                   'inbound citation to a vanished edition are different kinds '
                   'of evidence.</p>')

    if tracks["curated"]:
        c = tracks["curated"]
        out.append('<div class="panel"><h3>Curated family &middot; '
                   'declared, not derived</h3>')
        out.append(f'<div><strong>{esc(c["title"])}</strong> '
                   f'{pill("held", str(c["count"]) + " editions")} '
                   f'{pill("", c["span"] or "")}</div>')
        out.append(f'<p class="small">{esc(c["note"])}</p>')
        out.append('<ul class="timeline">')
        for s in c["schemes"]:
            revs = ", ".join(s["revisions"]) if s["revisions"] else ""
            out.append(
                f'<li><strong>{esc(s["scheme"])}</strong> '
                f'<span class="small">{esc(s["era"] or "")}</span>'
                + (f'<div class="small">revisions {esc(revs)}</div>' if revs else "")
                + (f'<div class="small">{esc(s["note"])}</div>'
                   if s.get("note") else "")
                + "</li>")
        out.append('</ul></div>')

    if tracks["editions"] or tracks["changes"]:
        out.append('<div class="panel"><h3>Held in the store</h3>'
                   '<ul class="timeline">')
        for e in tracks["editions"] + tracks["changes"]:
            cls = "now" if e["self"] else ""
            tag = (f'change {e["change"]}' if e["change"]
                   else f'revision {e["revision"]}' if e["revision"] else "base")
            out.append(
                f'<li class="{cls}">{link_or_text(e["id"], records, pages)} '
                f'{pill("", tag)}'
                + (' ' + pill("held", "this document") if e["self"] else "")
                + (f'<div class="small">{esc((e.get("title") or "")[:110])}</div>'
                   if e.get("title") else "")
                + "</li>")
        out.append("</ul></div>")

    if tracks["supersession"]:
        out.append('<div class="panel"><h3>Supersession</h3>'
                   '<ul class="timeline">')
        for s in tracks["supersession"]:
            gone = "gone" if s["rel"] in ("superseded_by", "cancelled_by") else ""
            verb = {"supersedes": "supersedes",
                    "superseded_by": "superseded by",
                    "cancels": "cancels",
                    "cancelled_by": "cancelled by"}[s["rel"]]
            out.append(
                f'<li class="{gone}"><strong>{esc(verb)}</strong> '
                f'{link_or_text(s["target"], records, pages)} '
                f'{pill("cited", s["basis"])}'
                + ("" if s["held"] else " " + pill("gap", "not held"))
                + (f'<div class="small">{esc((s.get("title") or "")[:110])}</div>'
                   if s.get("title") else "")
                + (f'<div class="src">{esc(s["resolution"][:160])}</div>'
                   if s.get("resolution") else "")
                + "</li>")
        out.append("</ul></div>")

    if tracks["reverse_drift"]:
        out.append('<div class="panel"><h3>Cited as an earlier edition</h3>'
                   '<p class="small">These documents name a revision of this '
                   'policy the store does not hold. Nothing records that an '
                   'edition existed once it is off the publisher\'s site; an '
                   'inbound citation is often the only surviving evidence.</p>'
                   '<ul class="timeline">')
        seen = set()
        for e in tracks["reverse_drift"]:
            key = (e["src"], e["target"])
            if key in seen:
                continue
            seen.add(key)
            out.append(
                f'<li class="gone">{link_or_text(e["src"], records, pages)} '
                f'cites <code>{esc(e["target"])}</code> '
                f'{pill("drift", "not held")}</li>')
        out.append("</ul></div>")

    if tracks["corrections"]:
        out.append('<details class="body"><summary>Record history &middot; '
                   f'{len(tracks["corrections"])} correction(s) to the DATA, '
                   'not to the policy</summary><ul class="timeline">')
        for c in tracks["corrections"]:
            out.append(f'<li><strong>{esc(c.get("date"))}</strong> '
                       f'<span class="small">checked against '
                       f'{esc(c.get("against"))}</span><ul class="small">'
                       + "".join(f"<li>{esc(ch)}</li>"
                                 for ch in c.get("changes") or [])
                       + "</ul></li>")
        out.append("</ul></details>")
    return out


# ---------------------------------------------------------------------------
# Section 3 - what it says


def provision_tree(provisions, records, pages, path_prefix=None):
    by_parent = {}
    for p in provisions:
        by_parent.setdefault(p.get("parent"), []).append(p)

    def walk(parent, depth):
        out = []
        for p in by_parent.get(parent, []):
            anchor = p["path"].replace("/", "-")
            cits = p.get("citations") or []
            out.append(f'<div class="prov" id="{esc(anchor)}">')
            out.append(f'<span class="plabel">{esc(p.get("label") or "")}</span> ')
            text = p.get("text") or ""
            if cits:
                c = cits[0]
                out.append(
                    f'<span class="reflink">'
                    f'{link_or_text(c["target_doc"], records, pages, text[:150])}'
                    f'</span> ' + pill("cited", "cited"))
            elif text:
                out.append(f'<span class="ptext">{esc(text)}</span>')
            out.append("</div>")
            out.extend(walk(p["path"], depth + 1))
        return out

    return walk(None, 0)


def content_section(rec, records, pages):
    out = ['<h2>What it says</h2>']
    ref_secs, body_secs = [], []
    for sec in rec.get("sections", []):
        provs = sec.get("provisions") or []
        refs = [p for p in provs
                if p["path"].split("/")[0].rstrip("0123456789") in ("ref", "encl")
                and "/" in p["path"]]
        body = [p for p in provs if p not in refs]
        if refs:
            ref_secs.append((sec, refs))
        if body:
            body_secs.append((sec, body))

    # Every section, in document order. A section the parser refused - a
    # table, a flattened extraction - has no provisions, and dropping it
    # would silently remove content from the document. Those render as
    # source text, labelled, so the page is the whole policy rather than
    # the parseable part of it.
    ordered = [(sec, [p for p in (sec.get("provisions") or [])
                      if p["path"].split("/")[0].rstrip("0123456789")
                      not in ("ref", "encl")])
               for sec in rec.get("sections", [])]
    total = sum(len(b) for _, b in ordered)
    raw_only = sum(1 for sec, b in ordered if not b and (sec.get("text") or "").strip())
    if total or raw_only:
        label = (f'The full text &middot; {total} addressable paragraph(s) '
                 f'across {len(ordered)} section(s)')
        if raw_only:
            label += (f', {raw_only} of them held as source text because the '
                      f'parser refused to invent a hierarchy for them')
        # Open by default: the text is the point of the page, not an appendix.
        out.append(f'<details class="body" open><summary>{label}</summary>')
        for sec, body in ordered:
            anchor = esc(sec.get("anchor") or "")
            out.append(f'<div class="panel" style="margin-top:10px" '
                       f'id="sec-{anchor}">'
                       f'<h3>{anchor}'
                       + (f' &middot; {esc(sec.get("heading"))}'
                          if sec.get("heading") else "")
                       + "</h3>")
            if body:
                out.extend(provision_tree(body, records, pages))
            elif (sec.get("text") or "").strip():
                out.append('<p class="small">No provision hierarchy was parsed '
                           'for this section. Its source text is shown as '
                           'extracted, unaltered.</p>')
                out.append(f'<div class="doc-raw">{esc(sec["text"])}</div>')
            out.append("</div>")
        out.append("</details>")

    # The reference join follows the text: it is the page's connective
    # tissue, not its subject.
    if ref_secs:
        out.append('<div class="panel"><h3>References this document names</h3>'
                   '<p class="small">Each entry is a link, not a string. This is '
                   'the join between one policy and the next.</p>')
        for sec, refs in ref_secs:
            out.append('<ul class="reflist">')
            for p in refs:
                cits = p.get("citations") or []
                label = p.get("label") or ""
                text = p.get("text") or ""
                if cits:
                    c = cits[0]
                    tgt = records.get(c["target_doc"]) or {}
                    tier = TIER_OF_TYPE.get(tgt.get("doc_type"), "")
                    out.append(
                        f'<li><span class="plabel">{esc(label)}</span> '
                        f'<span class="reflink">'
                        f'{link_or_text(c["target_doc"], records, pages, text[:120])}'
                        f'</span>'
                        + (" " + pill("", f"{tier} {TIER_NAME.get(tier, '')}")
                           if tier else "")
                        + (" " + pill("held", "in store")
                           if c["target_doc"] in records else
                           " " + pill("gap", "named, not held"))
                        + f'<div class="src">{esc(c.get("target_uslm") or "")}</div>'
                        + "</li>")
                else:
                    out.append(f'<li><span class="plabel">{esc(label)}</span> '
                               f'{esc(text[:160])} '
                               f'{pill("", "no issuance named")}</li>')
            out.append("</ul>")
        out.append("</div>")
    return out


# ---------------------------------------------------------------------------


def render_one(rec, records, pages, inbound_t, inbound_b, families, gaps, out_dir):
    did = rec["id"]
    tracks = build(rec, records, set(records), inbound_b, families)
    tier = tier_of(did, rec)
    dates = rec.get("dates") or {}

    P = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         FAVICON,
         f'<title>{esc(rec.get("title") or did)} - Semper Admin Policy Library</title>',
         f"<style>{CSS}{EXTRA_CSS}</style></head><body>",
         '<a class="skip" href="#main">Skip to main content</a>',
         f'<header class="chrome">{BRAND}<span>Policy</span>'
         '<a href="policy-index.html" style="margin-left:auto">All policies</a>'
         '<a href="authority-index.html">Authority chains</a>'
         '<a href="sources.html">Sources</a></header>',
         '<main id="main">',
         f'<p class="crumb"><a href="policy-index.html">All policies</a> '
         f'&rsaquo; {esc(tier)} {esc(TIER_NAME.get(tier, tier))}</p>',
         f'<h1>{esc(rec.get("title") or did)}</h1>',
         f'<div class="ident">{esc(rec.get("uslm_identifier") or "")}</div>',
         '<div class="factrow">'
         + pill("", f"{tier} {TIER_NAME.get(tier, tier)}")
         + pill(rec.get("status") if rec.get("status") in ("cancelled",
                                                           "superseded") else "",
                rec.get("status") or "unknown")
         + pill("", rec.get("verification") or "UNVERIFIED")
         + (pill("", f"signed {dates.get('signed')}") if dates.get("signed") else "")
         + (pill("cancelled", f"cancelled {dates.get('cancelled')}")
            if dates.get("cancelled") else "")
         + "</div>"]

    # The document's own text leads - it is what a reader opened the page
    # for. The authority ladder and the lineage are context and follow it.
    P += content_section(rec, records, pages)
    P += authority_section(rec, records, pages, inbound_t, gaps)
    P += lineage_section(rec, tracks, records, pages)

    prov = rec.get("provenance") or {}
    P.append('<h2>Provenance</h2><div class="panel"><p class="small">'
             f'Source <code>{esc(prov.get("source_path") or "")}</code><br>'
             f'Extracted by {esc(prov.get("extraction_engine") or "")} '
             f'on {esc((prov.get("extracted_at") or "")[:10])}, converted '
             f'{esc((prov.get("converted_at") or "")[:10])} against store schema '
             f'{esc(rec.get("schema_version") or "")}<br>'
             f'Checksum <code>{esc((prov.get("source_hash") or "")[:32])}</code>'
             '</p></div>')
    P.append('<footer><p>This record is an UNVERIFIED machine extraction unless '
             'marked otherwise. Every link on this page is cited: it exists '
             'because the issuing authority printed the reference on the '
             'document. This library is an unofficial reference - the issuing '
             'authority\'s copy governs.</p></footer></main></body></html>')

    with open(os.path.join(out_dir, page_name(did)), "w", encoding="utf-8") as fh:
        fh.write("\n".join(P))
    return tracks


def render_index(records, pages, inbound_t, out_dir, types=None):
    rows = []
    for did in sorted(pages):
        rec = records[did]
        tier = tier_of(did, rec)
        outb = len([m for m in rec.get("relationships", {}).get("edge_meta", [])
                    or [] if m.get("rel") == "references"])
        inb = len([e for e in inbound_t.get(did, []) if e["rel"] == "references"])
        provs = sum(len(s.get("provisions") or []) for s in rec.get("sections", []))
        rows.append((TIER_ORDER.index(tier) if tier in TIER_ORDER else 9,
                     did, rec, tier, outb, inb, provs))
    rows.sort()

    P = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         FAVICON,
         '<title>All policies - Semper Admin Policy Library</title>',
         f"<style>{CSS}{EXTRA_CSS}</style></head><body>",
         '<a class="skip" href="#main">Skip to main content</a>',
         f'<header class="chrome">{BRAND}<span>All policies</span>'
         '<a href="authority-index.html" style="margin-left:auto">Authority chains</a>'
         '<a href="sources.html">Sources</a></header>',
         '<main id="main"><h1>All policies</h1>',
         '<p class="lede">Every document in the demonstration set, ordered by '
         'the level that issued it. Each one opens on a single page carrying '
         'its full text, its authority, and its version history - the three '
         'questions a reader actually has, answered together.</p>',
         ('<div class="typegrid">' + "".join(
             f'<div class="typecard"><div class="n">{n}</div>'
             f'<a href="{esc(type_page_name(t))}">{esc(lbl)}</a></div>'
             for t, lbl, n in (types or [])) + '</div>') if types else "",
         '<table><tr><th>Tier</th><th>Policy</th><th>Status</th>'
         '<th>Names</th><th>Named by</th><th>Paragraphs</th></tr>']
    for _, did, rec, tier, outb, inb, provs in rows:
        P.append(
            f'<tr><td><code>{esc(tier)}</code> '
            f'<span class="small">{esc(TIER_NAME.get(tier, ""))}</span></td>'
            f'<td><a href="{esc(page_name(did))}">'
            f'{esc(rec.get("title") or did)}</a><br>'
            f'<span class="src">{esc(rec.get("uslm_identifier") or "")}</span></td>'
            f'<td>{pill(rec.get("status") if rec.get("status") in ("cancelled", "superseded") else "", rec.get("status") or "unknown")}</td>'
            f'<td>{outb}</td><td>{inb}</td><td>{provs}</td></tr>')
    P.append('</table>')
    P.append('<footer><p>Records are UNVERIFIED machine extractions unless '
             'promoted. Statute and Department of Defense records are '
             'metadata-grade: identity, dates, supersession, and reference '
             'lists only, section text not ingested.</p></footer>'
             '</main></body></html>')
    with open(os.path.join(out_dir, "policy-index.html"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(P))


TYPE_LABEL = {
    "USC": "United States Code", "DODI": "DoD Instructions",
    "DODD": "DoD Directives", "DTM": "Directive-type Memorandums",
    "SECNAV": "SECNAV Instructions", "MCO": "Marine Corps Orders",
    "MCBUL": "Marine Corps Bulletins", "NAVMC": "NAVMC Publications",
    "MARADMIN": "MARADMIN Messages", "ALMAR": "ALMAR Messages",
    "ALNAV": "ALNAV Messages", "DODFMR": "DoD Financial Management Regulation",
}


def type_page_name(doc_type):
    return f"type-{doc_type}.html"


def render_type_indexes(records, pages, inbound_t, out_dir):
    """One page per issuance type, matching the pattern the message pages set.

    A reader who wants every Marine Corps Order in the set should not have to
    filter a mixed list in their head.
    """
    groups = {}
    for did in pages:
        groups.setdefault(records[did].get("doc_type") or "OTHER", []).append(did)

    made = []
    for doc_type, ids in sorted(groups.items()):
        label = TYPE_LABEL.get(doc_type, doc_type)
        rows = sorted(ids, key=lambda d: (records[d].get("status") != "active", d))
        P = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
         FAVICON,
             f'<title>{esc(label)} - Semper Admin Policy Library</title>',
             f"<style>{CSS}{EXTRA_CSS}</style></head><body>",
             '<a class="skip" href="#main">Skip to main content</a>',
             f'<header class="chrome">{BRAND}<span>Documents by type</span>'
             '<a href="policy-index.html" style="margin-left:auto">All policies</a>'
             '<a href="authority-index.html">Authority chains</a>'
             '<a href="connections.html">Connections</a>'
             '<a href="sources.html">Sources</a></header>',
             '<main id="main">',
             f'<p class="crumb"><a href="index.html">Home</a> &rsaquo; '
             f'{esc(label)}</p>',
             f'<h1>{esc(label)} <span class="small">({len(rows)})</span></h1>',
             '<table><tr><th>Document</th><th>Status</th><th>Names</th>'
             '<th>Named by</th><th>Paragraphs</th></tr>']
        for did in rows:
            rec = records[did]
            outb = len([m for m in rec.get("relationships", {}).get("edge_meta", [])
                        or [] if m.get("rel") == "references"])
            inb = len([e for e in inbound_t.get(did, [])
                       if e["rel"] == "references"])
            provs = sum(len(sec.get("provisions") or [])
                        for sec in rec.get("sections", []))
            st = rec.get("status") or "unknown"
            P.append(
                f'<tr><td><a href="{esc(page_name(did))}">'
                f'{esc(rec.get("title") or did)}</a><br>'
                f'<span class="src">{esc(rec.get("uslm_identifier") or "")}</span>'
                f'</td>'
                f'<td>{pill(st if st in ("cancelled", "superseded") else "", st)}</td>'
                f'<td>{outb}</td><td>{inb}</td><td>{provs}</td></tr>')
        P.append('</table>')
        P.append('<footer><p>Generated from the canonical policy store. Records '
                 'are UNVERIFIED machine extractions unless promoted. This site '
                 'is an unofficial reference - the issuing authority\'s copy '
                 'governs.</p></footer></main></body></html>')
        with open(os.path.join(out_dir, type_page_name(doc_type)), "w",
                  encoding="utf-8") as fh:
            fh.write("\n".join(P))
        made.append((doc_type, label, len(rows)))
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="canonical_staging")
    ap.add_argument("--out", default="demo_site")
    ap.add_argument("--config", default="spines.json")
    ap.add_argument("--families", default="mos-family-manifest.json")
    args = ap.parse_args()

    records = load(args.store)
    pages = set(records)
    inbound_t, inbound_b = build_inbound(records)
    families = load_families(args.families)

    gaps = {}
    if os.path.exists(args.config):
        with open(args.config, encoding="utf-8") as fh:
            for spec in json.load(fh)["spines"]:
                gaps.update(spec.get("gaps") or {})

    os.makedirs(args.out, exist_ok=True)
    stats = {"curated": 0, "editions": 0, "supersession": 0, "drift": 0}
    for did in sorted(pages):
        t = render_one(records[did], records, pages, inbound_t, inbound_b,
                       families, gaps, args.out)
        stats["curated"] += 1 if t["curated"] else 0
        stats["editions"] += 1 if t["editions"] or t["changes"] else 0
        stats["supersession"] += 1 if t["supersession"] else 0
        stats["drift"] += 1 if t["reverse_drift"] else 0
    types = render_type_indexes(records, pages, inbound_t, args.out)
    render_index(records, pages, inbound_t, args.out, types)

    print(f"policy pages      {len(pages)}")
    print(f"  curated family  {stats['curated']}")
    print(f"  multi-edition   {stats['editions']}")
    print(f"  supersession    {stats['supersession']}")
    print(f"  reverse drift   {stats['drift']}")
    print(f"index -> policy-index.html")
    for t, lbl, n in types:
        print(f"  {type_page_name(t):26} {n:4}  {lbl}")


if __name__ == "__main__":
    main()
