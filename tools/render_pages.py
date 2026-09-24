"""Render the site's hand-written pages from fragments in site/.

Before 2026-09-15 six pages in docs/ were edited by hand and written by no
tool. README.md says docs/ is regenerated, never edited; those six were the
exception, and the stale counts on the home page were the consequence. Now a
page's body lives in site/<name>.html as an HTML fragment, this stage wraps
it in the chrome and writes docs/<name>.html, and every number in a fragment
is a placeholder filled from what the build measured. A count on the home
page is never typed. ACTION-REGISTER 5.2.

Placeholders are {{name}}. An unknown name fails the stage: a page is never
published with a placeholder in it.

Idempotent by construction: fragment in, page out, prior output removed
first. Runs after every other renderer so it can count the pages they made.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomicio import write_text  # noqa: E402
from chrome import head, header  # noqa: E402
from verify_status import (  # noqa: E402
    DATA, LEDGER, VERIFIED, derive, live_rule_assertions, load_ledger, load_policy,
)

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DOCS = ROOT / "docs"
REPORT = ROOT / "config" / "authority_report.json"
RECON = ROOT / "config" / "reconciliation.json"
EXPORTS = ROOT / "data" / "exports"

# name, page label in the chrome, nav href to mark current
PAGES = [
    ("index.html", "Home", "index.html"),
    ("how-it-works.html", "How it works", "how-it-works.html"),
    ("about.html", "About", "about.html"),
    ("search.html", "Search", "search.html"),
    ("accessibility.html", "Accessibility", "about.html"),
    ("ontology.html", "Ontology", "ontology.html"),
    # The MOS strand, folded into the build as fragments (ACTION-REGISTER 5.10,
    # first half). Generating the lineage page from the family manifest is the
    # second half and is still open.
    ("mos-manual-intro.html", "MOS Manual", "policy-index.html"),
    ("mos-manual-lineage.html", "Version history", "policy-index.html"),
]

FOOTER = ('<footer><p>Generated from the canonical policy store. This site is an '
          'unofficial reference - the issuing authority\'s copy governs.</p>'
          '<p><a href="accessibility.html">Accessibility statement</a> &middot; '
          '<a href="about.html">About</a></p></footer>')

TYPE_LABEL = {"MCO": "Marine Corps Orders", "MARADMIN": "MARADMIN messages",
              "NAVMC": "NAVMC publications", "SECNAVINST": "SECNAV instructions",
              "DODI": "DoD instructions", "USC": "U.S. Code sections"}


from render_currency import display as display_id  # noqa: E402


def policy_link(doc_id: str) -> str:
    page = f"policy-{doc_id}.html"
    if (DOCS / page).exists():
        return f'<a href="{page}">{display_id(doc_id)}</a>'
    return display_id(doc_id)


def measure() -> dict:
    """Everything a fragment may cite, from build outputs only. Never from
    canonical/, which carries contact details and is not this stage's to read."""
    report = json.loads(REPORT.read_text(encoding="utf-8"))
    recon = json.loads(RECON.read_text(encoding="utf-8"))
    t = report["totals"]
    v = {"docs": t["docs"], "edges": t["edges"], "drift": t["drift"],
         "gaps": t["gaps"], "held": t["held"]}


    # Provisions, as the store counts them, measured by extract_authority.
    # Not counted in the exports: 14 exports repeat provision elements and
    # some identifiers collide (ACTION-REGISTER 5.13), so a tag count there
    # states neither the store nor the truth.
    v["provisions"] = t.get("provisions", 0)
    v["path_collisions"] = t.get("path_collisions", 0)
    v["docs_with_path_collisions"] = t.get("docs_with_path_collisions", 0)

    # Pages by type, from what the renderers wrote.
    by_type = {}
    for f in DOCS.glob("policy-*.html"):
        if f.name == "policy-index.html":
            continue
        prefix = f.name[len("policy-"):-len(".html")].split("-")[0]
        by_type[prefix] = by_type.get(prefix, 0) + 1
    v["policy_pages"] = sum(by_type.values())
    v["type_counts"] = " &middot; ".join(
        f'<a href="type-{k if k != "SECNAVINST" else "SECNAV"}.html">{TYPE_LABEL.get(k, k)}</a> {n}'
        for k, n in sorted(by_type.items(), key=lambda kv: -kv[1]))

    # Current documents citing an instruction no longer in force.
    cs = report.get("cites_superseded", {})
    citing = sorted({d for docs in cs.values() for d in docs})
    v["n_cites_superseded"] = len(citing)
    v["cites_superseded"] = "; ".join(
        f"{', '.join(policy_link(d) for d in docs)} cite{'s' if len(docs) == 1 else ''} "
        f"{policy_link(tgt)}, {report['superseded_status'].get(tgt, 'no longer in force')}"
        for tgt, docs in cs.items()) or "none found in this set"

    # At scale: the same measurement across the full corpus, if the report-only
    # run has been made. Honest either way: the block says "not yet run" rather
    # than being omitted, because its absence is itself a fact about the proof.
    scale_path = ROOT / "config" / "scale_report.json"
    if scale_path.exists():
        sr = json.loads(scale_path.read_text(encoding="utf-8"))
        st, gone = sr["totals"], sr.get("cites_superseded_detail", [])
        n_gone_docs = len({d["citing"] for d in gone})
        v["scale_block"] = (
            '<div class="findings scale"><div class="finding">'
            f'<div class="big">{n_gone_docs:,}</div><p>documents in force across the full '
            f'corpus of {st["docs"]:,} cite an instruction that is not. '
            f'<a href="scale.html">The same measurement, at scale</a></p></div>'
            '<div class="finding">'
            f'<div class="big">{st["drift"]:,} of {st["edges"]:,}</div><p>references across the '
            f'full corpus name an edition since superseded</p></div>'
            '<div class="finding">'
            f'<div class="big">{st["quarantined"]:,}</div><p>records carrying a limited '
            f'distribution statement, excluded from the count as from everything else</p></div>'
            '</div>')
    else:
        v["scale_block"] = ('<p class="note">The same measurement has not yet been run across '
                            'the full corpus. When it has, its counts appear here, produced by '
                            'the same tool and never typed.</p>')

    # The most depended-upon document, for the impact pointer.
    nb = report.get("named_by", {})
    if nb:
        top = next(iter(nb))
        v["most_named"] = policy_link(top)
        v["most_named_n"] = len(nb[top])
    else:
        v["most_named"], v["most_named_n"] = "nothing", 0

    # Verification, derived the same way the verification page derives it.
    quorum, _dev = load_policy()
    rows = derive(live_rule_assertions(DATA), load_ledger(LEDGER), quorum)
    v["assertions"] = len(rows)
    v["verified"] = sum(r["status"] == VERIFIED for r in rows)

    # The thread's comparison, from the reconciliation report.
    findings = recon["findings"]
    lead = next((f for f in findings if f["concept"] == "PARENTAL_LEAVE_MAX_DURATION"), None)
    n_nc = sum(f["verdict"] != "AGREE" for f in findings)
    tier_word = {"T0": "the statute", "T1": "the DoD instruction", "T2": "the Navy instruction",
                 "T3": "the Marine Corps order", "T4": "the manual", "T5": "the message"}
    if lead and lead["verdict"] == "AGREE":
        stated = "; ".join(f"{tier_word.get(t['tier'], t['tier_label'])} states {t['stated']}"
                           for t in lead["tiers"])
        v["thread_verdict"] = (f"Yes. {stated[0].upper() + stated[1:]}. Both come to "
                               f"{lead['tiers'][0]['canonical']} {lead['canonical_unit']}.")
    elif lead:
        v["thread_verdict"] = f"Not yet. {lead['detail']}."
    else:
        v["thread_verdict"] = "Not yet. The concept is not in the reconciliation report."
    # The ontology page: what the project's own ontology holds, counted from
    # the schema and the concept register rather than typed.
    ttl = (ROOT / "schema" / "authority-ontology.ttl").read_text(encoding="utf-8")
    v["n_ontology_classes"] = len(re.findall(r"\ba owl:Class\b", ttl))
    concepts = json.loads((ROOT / "config" / "rule_concepts.json").read_text(encoding="utf-8"))
    v["n_concepts"] = len(concepts["concepts"])

    v["n_findings"] = len(findings)
    v["n_not_compared"] = n_nc
    for k, val in v.items():
        if isinstance(val, int) and k not in ("n_findings", "n_not_compared", "verified",
                                              "assertions", "n_cites_superseded", "most_named_n"):
            v[k] = f"{val:,}"
    return v


def render_one(name: str, label: str, current: str, values: dict) -> str:
    frag = (SITE / name).read_text(encoding="utf-8")
    css = (SITE / "pages.css").read_text(encoding="utf-8") if (SITE / "pages.css").exists() else ""
    unknown = sorted(set(re.findall(r"\{\{(\w+)\}\}", frag)) - set(values))
    if unknown:
        raise SystemExit(f"site/{name}: unknown placeholder(s) {unknown}; nothing written")
    body = re.sub(r"\{\{(\w+)\}\}", lambda m: str(values[m.group(1)]), frag)
    title_m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
    title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else label
    if name == "index.html":
        title = "Home"
    return (head(title, extra_css=css) + header(label, current=current)
            + '<main id="main">' + body + "</main>" + FOOTER + "</body></html>")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(DOCS))
    args = ap.parse_args()
    out = Path(args.out)
    values = measure()
    for name, label, current in PAGES:
        target = out / name
        if target.exists():
            target.unlink()
        write_text(target, render_one(name, label, current, values))
        print(f"    {name}")
    print(f"    {len(PAGES)} page(s) from site/, counts: docs {values['docs']}, "
          f"edges {values['edges']}, drift {values['drift']}, verified "
          f"{values['verified']}/{values['assertions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
