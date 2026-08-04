"""Assemble a policy's version history from everything the store knows.

There is no single field that answers "what came before this". The corpus
holds one edition of most policies, because a superseded edition is usually
gone from the publisher's site by the time a scraper reaches it. So the
version story has to be assembled from four independent signals, and being
explicit about which one produced each row is the difference between a
timeline and a guess.

1. CURATED FAMILY. A manifest declaring that documents under different
   identifiers are one policy. Required whenever a policy is renumbered -
   the MOS Manual changed identifier scheme three times in 25 years, so no
   derivation could ever link its 32 editions.
2. CHANGE PACKAGES. Separate records for the same edition, distinguished by
   a -CHn suffix. MCO P1400.32D carries CH-1 and CH-2.
3. SUPERSESSION EDGES. supersedes and superseded_by, each carrying the basis
   that put it there. DoDI 1327.6 to 1327.06 is the clean case.
4. REVERSE DRIFT. Documents that cite an edition of this policy the store no
   longer holds. Nobody records this anywhere; it falls out of the authority
   extraction, and it is often the only surviving evidence that an earlier
   edition existed.

The record's own corrections array is carried alongside as a fifth track. It
is not policy history - it is the history of the DATA, and conflating the two
would be its own kind of dishonesty.
"""

import json
import os
import re

CH_RX = re.compile(r"-(?:CH|V)(\d{1,2})$", re.I)


def base_id(doc_id):
    """Strip revision letter and change suffix. MCO-1900.16F-CH2 -> MCO-1900.16"""
    core = CH_RX.sub("", doc_id)
    parts = core.split("-", 1)
    if len(parts) != 2:
        return core
    num = parts[1]
    while num and num[-1].isalpha():
        num = num[:-1]
    return f"{parts[0]}-{num}" if num else core


def revision_letter(doc_id):
    core = CH_RX.sub("", doc_id)
    parts = core.split("-", 1)
    if len(parts) != 2:
        return ""
    m = re.search(r"([A-Z]+)$", parts[1])
    return m.group(1) if m else ""


def change_number(doc_id):
    m = CH_RX.search(doc_id)
    return int(m.group(1)) if m else 0


def load_families(path):
    """Curated family manifests. Missing file is fine - most policies have none."""
    families = {}
    if not path or not os.path.exists(path):
        return families
    with open(path, encoding="utf-8") as fh:
        man = json.load(fh)
    key = man.get("policy_family")
    if key:
        families[key] = man
    return families


def _scheme_ids(scheme):
    """Reconstruct the exact record ids a scheme covers.

    Prefix matching is not good enough here. "MCO 1200.17" and "MCO 1200.18"
    share eight leading characters, so a prefix test folds an unrelated order
    into the MOS Manual family. The manifest states the revisions; build the
    ids from them and match exactly.
    """
    name = (scheme.get("scheme") or "").strip()
    m = re.match(r"^([A-Za-z]+)\s*P?\s*([0-9][0-9.]*)$", name)
    if not m:
        return set()
    doctype, number = m.group(1).upper(), m.group(2)
    doctype = {"MCBUL": "MCBUL", "MCO": "MCO", "NAVMC": "NAVMC"}.get(
        doctype, doctype)
    out = {f"{doctype}-{number}"}
    for rev in scheme.get("revisions") or []:
        rev = rev.strip()
        if not rev or rev == "(base)":
            continue
        out.add(f"{doctype}-{number}{rev.upper()}")
    return out


def curated_family_for(rec, families):
    """A record belongs to a curated family only if the manifest names it.

    Exact id match against the reconstructed scheme membership. A curated
    family is a declaration, and a declaration that matches by accident is
    worse than no declaration.
    """
    for key, man in families.items():
        members = set()
        for scheme in man.get("identifier_lineage", []):
            members |= _scheme_ids(scheme)
        if base_id(rec["id"]) in {base_id(m) for m in members} \
                and any(rec["id"].startswith(m.rsplit("-", 1)[0] + "-")
                        for m in members) \
                and rec["id"] in members | {base_id(x) for x in members}:
            return man
        if rec["id"] in members:
            return man
    return None


def build(rec, records, store_ids, inbound, families=None):
    """Return the version tracks for one record.

    records  - id -> record, for whatever is loaded
    store_ids - every id in the full store, for edition detection
    inbound  - id -> list of edges pointing at this record
    """
    did = rec["id"]
    base = base_id(did)
    tracks = {"editions": [], "changes": [], "supersession": [],
              "reverse_drift": [], "curated": None, "corrections": []}

    # 1 curated family
    fam = curated_family_for(rec, families or {})
    if fam:
        tracks["curated"] = {
            "title": fam.get("title"),
            "note": fam.get("note"),
            "count": fam.get("edition_count"),
            "span": fam.get("span"),
            "schemes": [
                {"scheme": s.get("scheme"), "era": s.get("era"),
                 "revisions": s.get("revisions") or [], "note": s.get("note")}
                for s in fam.get("identifier_lineage", [])],
        }

    # 2 editions and change packages held in the store
    siblings = sorted(i for i in store_ids if base_id(i) == base)
    for sid in siblings:
        entry = {"id": sid, "revision": revision_letter(sid),
                 "change": change_number(sid), "self": sid == did,
                 "held": True,
                 "title": (records.get(sid) or {}).get("title"),
                 "status": (records.get(sid) or {}).get("status")}
        if change_number(sid) and revision_letter(sid) == revision_letter(did):
            tracks["changes"].append(entry)
        else:
            tracks["editions"].append(entry)
    if len(tracks["editions"]) <= 1 and not tracks["changes"]:
        tracks["editions"] = []      # one edition is not a lineage

    # 3 supersession, in both directions, with basis preserved
    for m in rec.get("relationships", {}).get("edge_meta", []) or []:
        if m.get("rel") in ("supersedes", "superseded_by", "cancels",
                            "cancelled_by"):
            tracks["supersession"].append({
                "rel": m["rel"], "target": m["target"],
                "basis": m.get("basis", "cited"),
                "resolution": m.get("resolution", ""),
                "held": m["target"] in store_ids,
                "title": (records.get(m["target"]) or {}).get("title"),
            })

    # 4 reverse drift - who cites an edition we no longer hold
    for edge in inbound.get(base, []):
        if edge["target"] == did:
            continue
        tracks["reverse_drift"].append(edge)

    tracks["corrections"] = rec.get("corrections") or []
    return tracks


def build_inbound(records):
    """id and base-id indexes of every edge pointing at a document."""
    by_target, by_base = {}, {}
    for src, rec in records.items():
        for m in rec.get("relationships", {}).get("edge_meta", []) or []:
            tgt = m.get("target")
            if not tgt:
                continue
            entry = {"src": src, "target": tgt, "rel": m.get("rel"),
                     "basis": m.get("basis", "cited"),
                     "confidence": m.get("confidence", ""),
                     "resolution": m.get("resolution", ""),
                     "src_title": rec.get("title"),
                     "src_status": rec.get("status")}
            by_target.setdefault(tgt, []).append(entry)
            by_base.setdefault(base_id(tgt), []).append(entry)
    return by_target, by_base
