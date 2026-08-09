"""Render the top-down authority chain as a page.

Walks upward from a seed document through cited reference edges, groups
what it finds by tier, and renders one page per spine.

Three rules the rendering obeys, all inherited from the store's discipline:

1. Cited and inferred are never conflated. Every edge prints its basis and
   the paragraph it came from.
2. A tier the corpus does not hold prints as a stated gap with the reason,
   never as a closed link. The leave spine genuinely skips the Department
   of the Navy - no SECNAV leave instruction exists in the store - and the
   page says so rather than drawing a line that is not there.
3. A citation to a superseded edition prints as revision drift, showing
   both the edition named and the edition held. It is not silently
   upgraded to the current one.
"""

import argparse
import html
import json
import os
import re
from datetime import datetime, timezone

# The programme identity, one definition for every page footer. Wording is
# the corrected edition adopted in CHARTER.md section 3 - the name and the
# scope sentences only. The EU-derived mission clauses stay off the public
# site until the source page's reuse licence is confirmed (CHARTER.md
# section 2, reason 3); these two sentences are original text and carry no
# attribution obligation.
PROGRAMME_P = (
    '<p>Semper Admin is the public identity of GOATS, the Generalized Orders '
    'Administrative Tools programme. The programme is scoped to the United '
    'States Government; the Marine Corps and the Department of the Navy are '
    'the first use case and the proof of concept.</p>')

TIER_ORDER = ["T0", "T1", "T2", "T3", "T4", "T5"]
TIER_NAME = {
    "T0": "Statute",
    "T1": "Department of Defense",
    "T2": "Department of the Navy",
    "T3": "Service directive",
    "T4": "Service manual",
    "T5": "Message",
    "TX": "Other authority",
}
TIER_OF_TYPE = {
    "USC": "T0",
    "DODI": "T1", "DODD": "T1", "DODM": "T1", "DTM": "T1",
    "DODFMR": "T1", "DODREG": "T1", "CJCSI": "T1",
    "SECNAV": "T2", "SECNAVINST": "T2", "SECNAVM": "T2",
    "OPNAVINST": "T2", "BUMEDINST": "T2", "NAVSO": "T2", "SECNAVNOTE": "T2",
    "MCO": "T3", "MCBUL": "T3",
    "NAVMC": "T4", "MCRP": "T4", "MCTP": "T4", "MCWP": "T4", "MCDP": "T4",
    "MARADMIN": "T5", "ALMAR": "T5", "ALNAV": "T5",
    "EO": "TX",
}
TIER_RX = re.compile(r"tier=(T[0-9X])")
SRC_RX = re.compile(r"^([^;]+);")
HOLDS_RX = re.compile(r"store-holds=([^;]+)")


def tier_of(doc_id, record=None):
    if record and record.get("doc_type") in TIER_OF_TYPE:
        return TIER_OF_TYPE[record["doc_type"]]
    prefix = doc_id.split("-")[0].upper()
    return TIER_OF_TYPE.get(prefix, "TX")


def load(store):
    out = {}
    for f in os.listdir(store):
        if f.endswith(".json"):
            with open(os.path.join(store, f), encoding="utf-8") as fh:
                out[f[:-5]] = json.load(fh)
    return out


def walk(records, seed, max_hops=6):
    """Breadth-first upward walk. Returns (nodes, edges)."""
    nodes, edges, frontier, seen = {}, [], [seed], set()
    hops = 0
    while frontier and hops <= max_hops:
        nxt = []
        for did in frontier:
            if did in seen:
                continue
            seen.add(did)
            rec = records.get(did)
            nodes[did] = rec
            if not rec:
                continue
            rel = rec.get("relationships", {})
            for m in rel.get("edge_meta", []):
                if m.get("rel") not in ("references", "supersedes",
                                        "superseded_by", "cancels"):
                    continue
                tgt = m["target"]
                t_rec = records.get(tgt)
                t_tier = TIER_RX.search(m.get("resolution", ""))
                edges.append({
                    "src": did, "dst": tgt, "rel": m["rel"],
                    "basis": m.get("basis", "cited"),
                    "confidence": m.get("confidence", ""),
                    "resolution": m.get("resolution", ""),
                    "tier": (t_tier.group(1) if t_tier
                             else tier_of(tgt, t_rec)),
                })
                # Follow held targets upward, and follow supersession so a
                # citation to an old edition leads to the current one.
                if tgt in records and tgt not in seen:
                    nxt.append(tgt)
        frontier = nxt
        hops += 1
    return nodes, edges


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
header.chrome a:not(.wordmark){order:3;margin-left:0!important;
font:600 13px/1.1 inherit;padding:8px 12px;border:1px solid var(--borders);
border-radius:9999px;background:var(--muted);color:var(--parch3);
text-decoration:none}
table{display:block;overflow-x:auto}
code,h3{overflow-wrap:anywhere}
}
"""


# Contact masking, same definition the export tier uses, so the rendered site
# and the XML agree about what a contact is. Masking lives in esc() because
# every renderer emits through it, and a second emission path is how the XML
# tier ended up with an unmasked phone number in a heading attribute.
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RX = re.compile(
    r"(?:\(?\d{3}\)?[-. ]?\d{3}[-. ]\d{4}|\b\d{3}[-.]\d{4}\b|DSN[:\s]*\d{3}[-. ]?\d{4})",
    re.I)
MASK = "[contact withheld]"
MASK_ON = True


def mask(text):
    if not MASK_ON:
        return text
    return PHONE_RX.sub(MASK, EMAIL_RX.sub(MASK, text))


def esc(s):
    return html.escape(mask(str(s or "")))


TITLE_LEVEL_RX = re.compile(r"^USC-T\d+$")


def primary_chain(records, seed, prefer=None):
    """The spine: seed -> ... -> the highest held tier.

    The walk climbs ONE TIER AT A TIME. Ranking on absolute tier instead
    would let a bare "Title 10, U.S. Code" citation short-circuit the whole
    ladder, jumping a Marine Corps order straight to statute and hiding the
    DoD instruction that actually implements it. Smallest ascent wins, and a
    specific section beats a whole-title node at equal ascent.

    Supersession is followed so a citation to a retired edition leads to the
    edition in force, and one lateral step is allowed so a clarification
    reaches the message it clarifies.
    """
    # prefer breaks ties between equally-ranked targets. It selects among
    # edges the extractor already found; it cannot create one.
    pref = {d: i for i, d in enumerate(prefer or [])}
    order = {t: i for i, t in enumerate(TIER_ORDER)}
    chain, cur, guard, lateral = [seed], seed, 0, 0
    while guard < 12:
        guard += 1
        rec = records.get(cur)
        if not rec:
            break
        cur_tier = order.get(tier_of(cur, rec), 99)
        best = None
        for m in rec.get("relationships", {}).get("edge_meta", []):
            tgt = m.get("target")
            if m.get("rel") not in ("references", "supersedes", "superseded_by"):
                continue
            if tgt in chain or tgt not in records:
                continue
            t_rec = records[tgt]
            t_tier = order.get(tier_of(tgt, t_rec), 99)
            specific = (pref.get(tgt, 500),
                        0 if not TITLE_LEVEL_RX.match(tgt) else 1)
            if m["rel"] == "superseded_by":
                rank = (0, (-1, 0))           # same tier, current edition
            elif t_tier < cur_tier:
                rank = (cur_tier - t_tier, specific)   # smallest ascent wins
            elif (t_tier == cur_tier and lateral < 1
                  and tier_of(cur, rec) == "T5"):
                # A clarification pointing at the message it clarifies is a
                # real step, and a reader expects to see it. Restricted to
                # the message tier: a DoD instruction citing a sibling DoD
                # instruction is a cross-reference, not a rung on the
                # ladder, and treating it as one puts an unrelated issuance
                # above the one that governs. Capped at one either way.
                rank = (-1, (-1, 0))
            else:
                continue
            if best is None or rank < best[0]:
                best = (rank, tgt, m)
        if not best:
            break
        if best[0][0] == -1:
            lateral += 1
        chain.append(best[1])
        cur = best[1]
    return chain


def edge_between(records, src, dst):
    for m in records.get(src, {}).get("relationships", {}).get("edge_meta", []):
        if m.get("target") == dst:
            return m
    return None


def _pills(did, rec):
    held = rec is not None
    status = (rec or {}).get("status", "not held")
    cls = status if status in ("cancelled", "superseded") else ""
    return (f"<span class=\"pill {'held' if held else 'gap'}\">"
            f"{'in store' if held else 'named, not held'}</span> "
            f"<span class=\"pill {esc(cls)}\">{esc(status)}</span>")


def render(records, seed, title, gaps, out_path, subtitle="", prefer=None):
    nodes, edges = walk(records, seed)
    chain = primary_chain(records, seed, prefer)
    inbound = {}
    for e in edges:
        inbound.setdefault(e["dst"], []).append(e)

    stamp = datetime.now(timezone.utc).date().isoformat()
    P = [
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        f"<title>{esc(title)} - Semper Admin Policy Library</title>",
        f"<style>{CSS}</style></head><body>",
        "<a class=\"skip\" href=\"#main\">Skip to main content</a>",
        "<header class=\"chrome\"><a class=\"wordmark\" href=\"index.html\">"
        "Semper Admin</a><span>Authority chain</span></header>",
        "<main id=\"main\">",
        f"<h1>{esc(title)}</h1>",
        f"<p class=\"lede\">{esc(subtitle)}</p>",
        "<h2>The chain</h2>",
    ]

    # Statute at the top, message at the bottom.
    walk_up = list(reversed(chain))
    shown_gaps = set()
    for i, did in enumerate(walk_up):
        rec = records.get(did)
        tier = tier_of(did, rec)
        # State any tier the chain jumps over.
        if i > 0:
            prev_tier = tier_of(walk_up[i - 1], records.get(walk_up[i - 1]))
            a = TIER_ORDER.index(prev_tier) if prev_tier in TIER_ORDER else -1
            b = TIER_ORDER.index(tier) if tier in TIER_ORDER else -1
            for skipped in TIER_ORDER[a + 1:b]:
                if skipped in shown_gaps or skipped not in gaps:
                    continue
                shown_gaps.add(skipped)
                P.append("<div class=\"arrow\"><span>implemented by</span></div>")
                P.append(
                    f"<div class=\"tier gap\"><div class=\"tierhead\">"
                    f"<span class=\"tiercode\">{skipped}</span>"
                    f"<span>{esc(TIER_NAME[skipped])}</span>"
                    f"<span class=\"pill gap\">tier not held</span></div>"
                    f"<p class=\"why\">{esc(gaps[skipped])}</p></div>")
            m = edge_between(records, did, walk_up[i - 1])
            label = "supersedes" if m and m.get("rel") == "superseded_by" else "implemented by"
            P.append(f"<div class=\"arrow\"><span>{esc(label)}</span></div>")

        P.append(f"<div class=\"tier\"><div class=\"tierhead\">"
                 f"<span class=\"tiercode\">{tier}</span>"
                 f"<span>{esc(TIER_NAME.get(tier, tier))}</span></div>")
        P.append("<div class=\"doc\">")
        P.append(f"<div><span class=\"docid\">{esc(did)}</span> {_pills(did, rec)}</div>")
        if rec:
            P.append(f"<div class=\"doctitle\">{esc(rec.get('title'))}</div>"
                     f"<div class=\"uslm\">{esc(rec.get('uslm_identifier'))}</div>")
        # Why this link exists, from the citing document below it.
        if i + 1 < len(walk_up):
            m = edge_between(records, walk_up[i + 1], did)
            if m:
                src = SRC_RX.search(m.get("resolution", ""))
                holds = HOLDS_RX.search(m.get("resolution", ""))
                extra = ""
                if m.get("confidence") == "revision-drift":
                    extra = (" <span class=\"pill drift\">revision drift</span> "
                             f"store holds <code>{esc(holds.group(1) if holds else '')}</code>")
                P.append(
                    f"<p class=\"why\"><code>{esc(walk_up[i + 1])}</code> names it at "
                    f"<code>{esc(src.group(1) if src else '')}</code> "
                    f"<span class=\"pill cited\">{esc(m.get('basis', 'cited'))}</span>"
                    f"{extra}</p>")
        breadth = sorted(inbound.get(did, []), key=lambda e: e["src"])
        outbound = [e for e in edges if e["src"] == did]
        if outbound:
            P.append(f"<details><summary>"
                     f"{'The 1 reference' if len(outbound) == 1 else f'All {len(outbound)} references'}"
                     f" this document names</summary><table><tr><th>target</th>"
                     f"<th>tier</th><th>relation</th><th>basis</th>"
                     f"<th>from paragraph</th><th>note</th></tr>")
            for e in sorted(outbound, key=lambda e: (e["tier"], e["dst"])):
                src = SRC_RX.search(e["resolution"])
                holds = HOLDS_RX.search(e["resolution"])
                note = ""
                if e["confidence"] == "revision-drift":
                    note = (f"<span class=\"pill drift\">revision drift</span> "
                            f"holds <code>{esc(holds.group(1) if holds else '')}</code>")
                elif e["confidence"] == "named-not-held":
                    note = "<span class=\"pill gap\">not in store</span>"
                elif e["confidence"] == "high":
                    note = "<span class=\"pill held\">in store</span>"
                P.append(f"<tr><td><code>{esc(e['dst'])}</code></td>"
                         f"<td>{esc(e['tier'])}</td><td>{esc(e['rel'])}</td>"
                         f"<td><span class=\"pill cited\">{esc(e['basis'])}</span></td>"
                         f"<td><code>{esc(src.group(1) if src else '')}</code></td>"
                         f"<td>{note}</td></tr>")
            P.append("</table></details>")
        P.append("</div></div>")

    held = sum(1 for e in edges if e["confidence"] == "high")
    drift = sum(1 for e in edges if e["confidence"] == "revision-drift")
    gap_n = sum(1 for e in edges if e["confidence"] == "named-not-held")
    P.append("<h2>How to read this page</h2><p class=\"lede\">Every step states "
             "the paragraph the citation came from and whether the link is cited "
             "or inferred. Every link here is <strong>cited</strong>: it exists "
             "because the issuing authority printed the reference on the document. "
             "A tier the corpus does not hold prints as a stated gap with its "
             "reason, never as a closed link. A citation naming a superseded "
             "edition prints as revision drift, showing the edition named and the "
             "edition held, and is never silently upgraded to the current one.</p>")
    P.append(f"<footer><p>Generated {stamp} from the canonical store. Chain of "
             f"{len(chain)} documents across {len({tier_of(d, records.get(d)) for d in chain})} "
             f"tiers, drawn from {len(edges)} cited edges "
             f"({held} resolving in store, {drift} revision drift, {gap_n} named "
             f"but not held). Records are UNVERIFIED machine extractions unless "
             f"promoted. Statute and Department of Defense records are "
             f"metadata-grade: identity, dates, supersession, and reference lists "
             f"only, section text not ingested.</p>{PROGRAMME_P}</footer>")
    P.append("</main></body></html>")

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(P))
    return nodes, edges, chain


INDEX_CSS_EXTRA = """
.grid{border:1px solid var(--border);border-radius:12px;background:var(--card);
padding:8px 4px;overflow-x:auto}
.grid table{margin:0}
.grid td.t{text-align:center;font:600 12px/1.6 "JetBrains Mono",Menlo,monospace}
.have{color:#9fe0bd}.miss{color:#f0c489}.none{color:var(--muted-foreground);opacity:.4}
.spinename{font-weight:700}
"""


def render_index(results, out_path):
    """Landing page: which tiers each spine actually holds."""
    stamp = datetime.now(timezone.utc).date().isoformat()
    P = [
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">",
        "<title>Authority chains - Semper Admin Policy Library</title>",
        f"<style>{CSS}{INDEX_CSS_EXTRA}</style></head><body>",
        "<a class=\"skip\" href=\"#main\">Skip to main content</a>",
        "<header class=\"chrome\"><a class=\"wordmark\" href=\"index.html\">"
        "Semper Admin</a><span>Authority chains</span></header>",
        "<main id=\"main\"><h1>Authority chains</h1>",
        "<p class=\"lede\">Five policy spines, each traced from the message a "
        "Marine reads up to the authority it rests on. The grid states what each "
        "chain actually holds. A tier is filled only when a document names the "
        "one above it in its own printed reference list.</p>",
        "<h2>Tier coverage</h2><div class=\"grid\"><table>",
        "<tr><th>Spine</th>"
        + "".join(f"<th>{t}<br><span style=\"font-weight:400;text-transform:none\">"
                  f"{esc(TIER_NAME[t])}</span></th>" for t in TIER_ORDER)
        + "<th>Chain</th><th>Edges</th></tr>",
    ]
    for r in results:
        cells = []
        for t in TIER_ORDER:
            if t in r["tiers"]:
                cells.append("<td class=\"t have\" title=\"held\">&#9679;</td>")
            elif t in r["gaps"]:
                cells.append("<td class=\"t miss\" title=\"stated gap\">&#9675;</td>")
            else:
                cells.append("<td class=\"t none\" title=\"not part of this "
                             "spine\">&middot;</td>")
        P.append(f"<tr><td class=\"spinename\"><a href=\"{esc(r['out'])}\">"
                 f"{esc(r['title'].replace('Authority chain - ', ''))}</a></td>"
                 + "".join(cells)
                 + f"<td class=\"t\">{r['chain_len']}</td>"
                 + f"<td class=\"t\">{r['edges']}</td></tr>")
    P.append("</table></div>")
    P.append("<p class=\"why\"><span class=\"have\">&#9679;</span> held in the "
             "store &nbsp; <span class=\"miss\">&#9675;</span> named or expected "
             "and stated as a gap &nbsp; <span class=\"none\">&middot;</span> not "
             "part of this spine</p>")

    P.append("<h2>What each spine proves</h2>")
    for r in results:
        P.append(f"<div class=\"tier\"><div class=\"doc\">"
                 f"<div><a class=\"docid\" href=\"{esc(r['out'])}\">"
                 f"{esc(r['title'].replace('Authority chain - ', ''))}</a></div>"
                 f"<p class=\"why\">{esc(r['subtitle'])}</p>"
                 f"<p class=\"why\">Chain of {r['chain_len']} documents, "
                 f"{r['edges']} cited edges: {r['held']} resolving in store, "
                 f"{r['drift']} revision drift, {r['gap_edges']} named but not "
                 f"held.</p></div></div>")

    total_edges = sum(r["edges"] for r in results)
    total_drift = sum(r["drift"] for r in results)
    P.append("<h2>How to read these pages</h2><p class=\"lede\">Every link is "
             "<strong>cited</strong>: it exists because the issuing authority "
             "printed the reference on the document. Nothing is inferred from "
             "subject matter or numbering. A tier the corpus does not hold prints "
             "as a stated gap with its reason. A citation naming a superseded "
             "edition prints as revision drift, showing the edition named and the "
             "edition held, and is never silently upgraded.</p>")
    P.append(f"<footer><p>Generated {stamp} from the canonical store. "
             f"{len(results)} spines, {total_edges} cited edges, {total_drift} of "
             f"them naming an edition the store no longer holds as current. "
             f"Records are UNVERIFIED machine extractions unless promoted. "
             f"Statute and Department of Defense records are metadata-grade: "
             f"identity, dates, supersession, and reference lists only, section "
             f"text not ingested.</p>{PROGRAMME_P}</footer></main></body></html>")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(P))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="canonical_staging")
    ap.add_argument("--out", default="site_staging")
    ap.add_argument("--config", default="spines.json")
    ap.add_argument("--spine", help="render one spine by key")
    ap.add_argument("--index", default="authority-index.html")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    records = load(args.store)
    with open(args.config, encoding="utf-8") as fh:
        cfg = json.load(fh)

    results = []
    for spec in cfg["spines"]:
        if args.spine and spec["key"] != args.spine:
            continue
        seed = next((s for s in spec["seed_candidates"] if s in records), None)
        if not seed:
            print(f"{spec['key']:10} SKIPPED - no seed candidate in the store: "
                  f"{', '.join(spec['seed_candidates'])}")
            continue
        nodes, edges, chain = render(
            records, seed, spec["title"], spec["gaps"],
            os.path.join(args.out, spec["out"]), spec["subtitle"],
            spec.get("prefer"))
        tiers = sorted({tier_of(d, records.get(d)) for d in chain})
        held = sum(1 for e in edges if e["confidence"] == "high")
        drift = sum(1 for e in edges if e["confidence"] == "revision-drift")
        gap_edges = sum(1 for e in edges if e["confidence"] == "named-not-held")
        results.append({**spec, "seed": seed, "tiers": tiers,
                        "chain_len": len(chain), "edges": len(edges),
                        "held": held, "drift": drift, "gap_edges": gap_edges})
        print(f"{spec['key']:10} seed={seed:22} chain={len(chain)} "
              f"tiers={' '.join(tiers)} edges={len(edges)}")
        for d in reversed(chain):
            r = records.get(d)
            print(f"             {tier_of(d, r):3} {d:22} "
                  f"{(r or {}).get('status', '-'):11} "
                  f"{((r or {}).get('title') or '')[:52]}")

    if results and not args.spine:
        render_index(results, os.path.join(args.out, args.index))
        print(f"\nindex -> {args.index} ({len(results)} spines)")


if __name__ == "__main__":
    main()
