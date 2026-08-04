"""Write the vertical authority edges the corpus was missing.

Reads canonical records, finds the reference-list provisions the fixed
parser now produces (paths ref/a, ref2/c, encl/1), classifies each item
with tools/authority.py, and writes:

  provisions[].citations   one entry per parsed reference item
  relationships.references  target doc ids, deduplicated, source order
  relationships.edge_meta   rel/target/basis/confidence/resolution per edge

Nothing here infers. basis is always "cited" because every edge comes from
a reference list the issuing authority printed on the document. An item the
grammar does not recognize keeps its raw text and produces no edge.

Targets absent from the store are still written, with in-store=false in the
resolution string. A named authority the corpus lacks is a stated gap. It
is not dropped, and it is never resolved onto a document with a similar
number.

Usage:
  python tools/extract_authority.py --src canonical --out canonical_staging
  python tools/extract_authority.py --src canonical --out canonical_staging \
         --only MCO-1050.3J MARADMIN-2023-051
"""

import argparse
import json
import re
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atomicio import write_json  # noqa: E402
from authority import classify, TIERS  # noqa: E402

REF_ROOTS = ("ref", "encl")
TOOL = "extract_authority.py"


def _root(path):
    return path.split("/")[0].rstrip("0123456789") or path.split("/")[0]


def _base(doc_id):
    """Strip the revision letter and change suffix: MCO-1900.16F -> MCO-1900.16."""
    core = doc_id.split("-CH")[0].split("-V")[0]
    parts = core.split("-", 1)
    if len(parts) != 2:
        return core
    num = parts[1]
    while num and num[-1].isalpha():
        num = num[:-1]
    return f"{parts[0]}-{num}" if num else core


def _no_change(doc_id):
    """Strip only the change or volume suffix, keeping the revision letter.
    MCO-6100.13A-CH5 -> MCO-6100.13A. MCO-6100.13 stays MCO-6100.13."""
    return doc_id.split("-CH")[0].split("-V")[0]


def build_base_index(store_ids, known_revisions=None):
    """Two indexes, over two different populations.

    HELD is judged against store_ids - what THIS project actually has.

    DRIFT is judged against known_revisions when one is supplied - the set of
    revisions known to exist anywhere. Those are different questions. Whether
    a cited edition has been superseded is a fact about the world, not about
    the size of one corpus, and a project holding 54 documents would otherwise
    report almost every drift finding as "never held" and lose it.

    Without a revision index, drift falls back to store_ids and the tool says
    less rather than guessing.

    same_doc keys on the id WITH its revision letter, so a citation to
    "MCO 6100.13A" finds the store's "MCO-6100.13A-CH5". Those are the same
    order with its change package applied, not two editions - a message
    naming the base number is citing correctly, and calling that revision
    drift would report an id convention as a currency problem.

    base keys on the id WITHOUT its revision letter, which is what genuine
    revision drift looks like: 1421.3M cited, 1421.3N held.
    """
    same_doc, base = {}, {}
    for i in store_ids:
        same_doc.setdefault(_no_change(i), []).append(i)
    for i in (known_revisions or store_ids):
        base.setdefault(_base(i), []).append(i)
    return {"same_doc": same_doc, "base": base}


def resolve_target(cited, store_ids, base_index, known=None):
    """cited id -> (target, in_store, drift_siblings, change_applied).

    Three outcomes, kept distinct on purpose:

    - the store holds exactly what the text names            -> resolved
    - the store holds the same revision with a change package
      applied (cited MCO 6100.13A, held MCO-6100.13A-CH5)    -> resolved,
      target rewritten to the held record, cited form kept in resolution
    - the store holds a DIFFERENT revision of the same base
      (cited SECNAVINST 1421.3M, held 1421.3N)               -> drift, and
      the edge keeps pointing at the edition the text names
    """
    if cited in store_ids:
        return cited, True, [], None
    # Strict: the held id must be the cited id plus a numbered change or
    # volume suffix and nothing else. A loose stem match here would fold
    # free-form ids together - "DODFMR" would swallow
    # "DODFMR-Vol16_Ch_Definitions", which is a different document.
    suffix = re.compile(r"^" + re.escape(cited) + r"-(?:CH|V)\d{1,2}$")
    same = [s for s in base_index.get("same_doc", {}).get(_no_change(cited), [])
            if s != cited and suffix.match(s)]
    if same:
        return sorted(same)[-1], True, [], cited
    # Drift means the cited EDITION no longer exists while another revision
    # of the same base does. If the cited id is itself known to exist, the
    # citation is current and this project simply does not hold it - calling
    # that drift would report a collection gap as a currency problem, which
    # is the same error in the opposite direction from the one the strict
    # change-package match already guards against.
    if known is not None and cited in known:
        return cited, False, [], None
    sibs = [s for s in base_index.get("base", {}).get(_base(cited), [])
            if s != cited]
    return cited, False, sibs, None


def reference_items(record):
    """Yield (section_anchor, provision) for every reference-list item.

    Enclosure lists are included: MCO 1610.7B and MCO 1400.31D both hold
    their references inside Enclosure (1), which is exactly why they read
    as reference-free before the parser fix.
    """
    for sec in record.get("sections", []):
        for p in sec.get("provisions", []):
            path = p.get("path", "")
            if "/" not in path:
                continue                      # the container node itself
            if _root(path) in REF_ROOTS:
                yield sec.get("anchor"), p


MESSAGE_TYPES = {"MARADMIN", "ALMAR", "ALNAV"}
# A naval message states its references twice: REF/A/MSGID:.../ in the
# header, which carries only an originator and a date, and the AMPN block,
# which names the document in plain language ("REF D IS MCO 1050.3J
# REGULATIONS FOR LEAVE..."). The header form is unresolvable and was what
# the old extractor stored. The AMPN form is the citation.
# Naval messages state their references in up to three places, and the
# store was reading none of them usefully:
#
#   REF/A/MSGID: MEMO/OSD WASHINGTON DC/4JAN2023//   originator + date only
#   REF/A/DOC/MCO 8000.8/14 MARCH 2014//             the document, named
#   NARR/REF A IS MCO 1050.3J REGULATIONS FOR...     the document, named
#   AMPN/REF (A) IS MCO 1040.42B, WARRANT OFFICER... the document, named
#
# The first form is unresolvable and is what the old extractor stored. The
# other three are citations. NARR and AMPN carry the same content; which tag
# a drafter uses is a matter of habit, and reading only AMPN was dropping
# most of the message tier.
NARR_RX = re.compile(r"^\s*(?:AMPN|NARR)/(.*)$", re.I | re.M | re.S)
REF_IS_RX = re.compile(
    r"\bREF\s*\(?([A-Z])\)?\s+(?:IS\s+)?(.*?)"
    r"(?=\bREF\s*\(?[A-Z]\)?\s+(?:IS\s+)?[A-Z0-9]|$)",
    re.I | re.S)
# REF/A/DOC/MCO 8000.8/14 MARCH 2014// - the middle field names the type,
# the next field names the document. MSGID lines carry no document and are
# skipped rather than guessed at.
REF_LINE_RX = re.compile(r"^\s*REF/([A-Z])/([A-Z]+)/([^/]+)/", re.I | re.M)


def message_citations(record):
    """Yield (source-label, plain-language description) for a message."""
    if record.get("doc_type") not in MESSAGE_TYPES:
        return
    for sec in record.get("sections", []):
        text = sec.get("text", "")
        m = NARR_RX.search(text)
        if m:
            block = re.split(r"^\s*POC/", m.group(1), flags=re.M)[0]
            for hit in REF_IS_RX.finditer(block):
                letter = hit.group(1).upper()
                yield (f"narr:REF {letter}",
                       " ".join(hit.group(2).split()).strip(" /."))
        for hit in REF_LINE_RX.finditer(text):
            letter, kind, body = (hit.group(1).upper(), hit.group(2).upper(),
                                  hit.group(3).strip())
            if kind == "MSGID":
                continue
            # Both forms are yielded. A NARR entry often gives only the
            # document's TITLE ("REF A IS CLASS V(W) TOTAL LIFE CYCLE
            # MANAGEMENT") while the REF line carries the number. Duplicate
            # targets are dropped downstream, so reading both loses nothing.
            yield f"ref-line:REF {letter}", body
        return


def extract(record, store_ids, base_index=None, known=None):
    """Annotate one record in place. Returns a stats dict."""
    base_index = base_index if base_index is not None else {"same_doc": {},
                                                            "base": {}}
    self_id = record.get("id")
    edges, seen, parsed, unparsed, drift = [], set(), 0, 0, 0

    for anchor, prov in reference_items(record):
        cit = classify(prov.get("text", ""))
        if not cit:
            unparsed += 1
            prov.pop("citations", None)
            continue
        parsed += 1
        target, in_store, siblings, applied = resolve_target(
            cit["doc_id"], store_ids, base_index, known)
        if siblings:
            drift += 1
        prov["citations"] = [{
            "text": cit["text"][:500],
            "target_doc": target,
            "target_path": None,      # document-grade: a reference list
            "target_uslm": cit["uslm"],
            "basis": "cited",
            "resolution": (f"reference-list {prov['path']}; tier={cit['tier']}; "
                           f"in-store={'true' if in_store else 'false'}"
                           + (f"; store-holds={','.join(sorted(siblings)[:3])}"
                              if siblings else "")
                           + (f"; cited-as={applied}; change-package-applied"
                              if applied else "")
                           + ("; series" if cit["series"] else "")),
        }]
        if target == self_id or target in seen:
            continue                  # a document citing itself is not an edge
        seen.add(target)
        edges.append({
            "rel": "references",
            "target": target,
            "basis": "cited",
            "confidence": ("high" if in_store
                           else "revision-drift" if siblings
                           else "named-not-held"),
            "resolution": (f"{anchor}:{prov['path']}; tier={cit['tier']} "
                           f"({cit['tier_name']}); uslm={cit['uslm']}"
                           + (f"; store-holds={','.join(sorted(siblings)[:3])}"
                              if siblings else "")
                           + (f"; cited-as={applied}; change-package-applied"
                              if applied else "")
                           + (f"; title={cit['title'][:80]}" if cit["title"] else "")
                           + ("; series-citation" if cit["series"] else "")),
        })

    for where, desc in message_citations(record):
        cit = classify(desc)
        if not cit:
            unparsed += 1
            continue
        parsed += 1
        target, in_store, siblings, applied = resolve_target(
            cit["doc_id"], store_ids, base_index, known)
        if siblings:
            drift += 1
        if target == self_id or target in seen:
            continue
        seen.add(target)
        edges.append({
            "rel": "references",
            "target": target,
            "basis": "cited",
            "confidence": ("high" if in_store
                           else "revision-drift" if siblings
                           else "named-not-held"),
            "resolution": (f"{where}; tier={cit['tier']} "
                           f"({cit['tier_name']}); uslm={cit['uslm']}"
                           + (f"; store-holds={','.join(sorted(siblings)[:3])}"
                              if siblings else "")
                           + (f"; cited-as={applied}; change-package-applied"
                              if applied else "")),
        })

    # Idempotent by construction. A pipeline gets re-run, and appending to
    # a previous run's output silently preserves edges a later grammar fix
    # would never have written. Everything this tool wrote before is
    # identified by its resolution prefix and dropped first.
    rel = record.setdefault("relationships", {})
    mine = tuple(f"{p}:" for p in ("front-matter", "ampn", "narr", "ref-line")) \
        + ("p-", "encl", "ref")
    prior = {m.get("target") for m in (rel.get("edge_meta") or [])
             if m.get("rel") == "references"
             and str(m.get("resolution", "")).split(";")[0].strip()
             .startswith(mine)}
    rel["edge_meta"] = [m for m in (rel.get("edge_meta") or [])
                        if not (m.get("rel") == "references"
                                and m.get("target") in prior)]
    rel["references"] = [r for r in (rel.get("references") or [])
                         if r not in prior]
    record["conversion_notes"] = [
        n for n in (record.get("conversion_notes") or [])
        if not str(n).startswith(TOOL)]
    existing = [r for r in (rel.get("references") or [])
                if not r.upper().startswith("MSGID")]
    rel["references"] = existing + [e["target"] for e in edges
                                    if e["target"] not in existing]
    meta = list(rel.get("edge_meta") or [])
    have = {(m.get("rel"), m.get("target")) for m in meta}
    meta.extend(e for e in edges if ("references", e["target"]) not in have)
    rel["edge_meta"] = meta

    if edges or parsed or unparsed:
        stamp = datetime.now(timezone.utc).date().isoformat()
        record.setdefault("conversion_notes", []).append(
            f"{TOOL} {stamp} - authority edges from reference lists: "
            f"{len(edges)} written, {parsed} item(s) classified, "
            f"{unparsed} item(s) left unparsed (raw text retained)")
    return {"edges": len(edges), "parsed": parsed, "unparsed": unparsed,
            "held": sum(1 for e in edges if e["confidence"] == "high"),
            "drift": sum(1 for e in edges if e["confidence"] == "revision-drift"),
            "gaps": sum(1 for e in edges if e["confidence"] == "named-not-held")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical")
    ap.add_argument("--out", default="canonical_staging")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--report", default="authority_report.json")
    ap.add_argument("--revision-index",
                    help="JSON array of every doc id KNOWN TO EXIST, which may "
                         "be far larger than this project's holdings. Used only "
                         "to decide whether a cited edition has been superseded. "
                         "Omit and drift is judged against --store-index, which "
                         "understates it.")
    ap.add_argument("--store-index",
                    help="JSON array of every doc id in the full store. "
                         "Without it, in-store is judged against --src only, "
                         "which understates coverage when --src is a subset.")
    args = ap.parse_args()

    names = sorted(f for f in os.listdir(args.src) if f.endswith(".json"))
    if args.only:
        want = set(args.only)
        names = [f for f in names if f[:-5] in want]
    os.makedirs(args.out, exist_ok=True)

    totals = {"docs": 0, "edges": 0, "parsed": 0, "unparsed": 0,
              "held": 0, "drift": 0, "gaps": 0}
    by_tier, gap_docs, per_doc = {}, {}, {}
    if args.store_index:
        with open(args.store_index, encoding="utf-8") as fh:
            store_ids = set(json.load(fh))
    else:
        store_ids = {f[:-5] for f in os.listdir(args.src) if f.endswith(".json")}
    known = None
    if getattr(args, "revision_index", None):
        with open(args.revision_index, encoding="utf-8") as fh:
            known = set(json.load(fh))
    base_index = build_base_index(store_ids, known)

    for name in names:
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        s = extract(rec, store_ids, base_index, known)
        for k in ("edges", "parsed", "unparsed", "held", "drift", "gaps"):
            totals[k] += s[k]
        totals["docs"] += 1
        per_doc[rec["id"]] = s
        for m in rec.get("relationships", {}).get("edge_meta", []):
            if m.get("rel") != "references":
                continue
            tier = m.get("resolution", "").split("tier=")[-1][:2]
            by_tier[tier] = by_tier.get(tier, 0) + 1
            if m.get("confidence") in ("named-not-held", "revision-drift"):
                gap_docs.setdefault(m["target"], []).append(rec["id"])
        write_json(os.path.join(args.out, name), rec)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": totals,
        "edges_by_tier": {k: {"count": v, "name": TIERS.get(k, k)}
                          for k, v in sorted(by_tier.items())},
        "named_not_held": {k: sorted(set(v))
                           for k, v in sorted(gap_docs.items(),
                                              key=lambda kv: -len(kv[1]))},
        "per_document": per_doc,
    }
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)

    print(f"documents        {totals['docs']}")
    if known:
        print(f"revision index   {len(known)} known id(s) "
              f"(drift judged against these, not the {len(store_ids)} held)")
    print(f"items classified {totals['parsed']}  unparsed {totals['unparsed']}")
    print(f"edges written    {totals['edges']}  held {totals['held']}  "
          f"revision-drift {totals['drift']}  named-not-held {totals['gaps']}")
    for k, v in sorted(by_tier.items()):
        print(f"  {k} {TIERS.get(k, k):24} {v}")
    print(f"report -> {args.report}")


if __name__ == "__main__":
    main()
