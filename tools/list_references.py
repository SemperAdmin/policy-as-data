#!/usr/bin/env python3
"""
List every external authority the corpus references, and whether it is encoded.

Scans data/*.authority.jsonld for authority nodes (statutes, DoD/Navy/USMC
issuances) and checks each against the marked-up documents (data/*.uslm.xml).
A node is ENCODED if some markup document's root @identifier equals it; otherwise
it is a source we still NEED to ingest.

This is the acquisition backlog for the corpus: run it to see what to pull next.

Usage:  python3 tools/list_references.py
"""

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")

# @types that denote an external authority/issuance (not a provision or decision).
AUTHORITY_TYPES = {
    "pol:Statute",
    "pol:CodeOfFederalRegulations",
    "pol:ExecutiveOrder",
    "pol:DoDDirective",
    "pol:DoDInstruction",
    "pol:OpmIssuance",
    "pol:NavyIssuance",
    "pol:MarineCorpsOrder",
    "pol:ServiceMessage",
}


def encoded_identifiers():
    """Root @identifier of every marked-up document."""
    ids = set()
    for f in glob.glob(os.path.join(DATA, "*.uslm.xml")):
        m = re.search(r'<issuance\b[^>]*\bidentifier="([^"]+)"', open(f).read())
        if m:
            ids.add(m.group(1))
    return ids


def authority_nodes():
    """De-duplicated authority nodes across all graphs: id -> (type, label)."""
    nodes = {}
    for f in glob.glob(os.path.join(DATA, "*.authority.jsonld")):
        doc = json.load(open(f))
        for n in doc.get("@graph", []):
            t = n.get("@type")
            if t in AUTHORITY_TYPES:
                nodes.setdefault(n["@id"], (t, n.get("label", "")))
    return nodes


def main():
    encoded = encoded_identifiers()
    nodes = authority_nodes()

    have, need = [], []
    for ident, (t, label) in sorted(nodes.items()):
        (have if ident in encoded else need).append((ident, t, label))

    def show(rows):
        for ident, t, label in rows:
            short = label.split(".")[0] if label else ident
            print(f"   {t.replace('pol:',''):20} {ident}")
            print(f"   {'':20} {short}")

    print(f"ENCODED ({len(have)}):")
    show(have)
    print(f"\nNEED SOURCE TEXT ({len(need)}):")
    show(need)


if __name__ == "__main__":
    main()
