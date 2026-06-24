#!/usr/bin/env python3
"""
Validate the policy-as-data corpus.

Runs the same checks for every document in data/, so the corpus stays correct
as it grows. No policy logic lives here; this is QA on the encoding only.

Checks:
  1. Schema     - every *.uslm.xml validates against schema/usmc-issuance-1.0.xsd
  2. JSON       - every *.json / *.jsonld is well-formed
  3. Ontology   - schema/authority-ontology.ttl parses        (skipped if no rdflib)
  4. Conformance- every pol: type/predicate used in a *.jsonld is declared in the
                  ontology                                     (skipped if no rdflib)
  5. References - every rules.json citation and every authority Provision node
                  resolves to a provision @identifier in the markup

Exit status is non-zero if any check fails.

Usage:  python3 tools/validate.py
"""

import glob
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = os.path.join(ROOT, "schema", "usmc-issuance-1.0.xsd")
ONTOLOGY = os.path.join(ROOT, "schema", "authority-ontology.ttl")
DATA = os.path.join(ROOT, "data")

failures = []
notes = []


def rel(path):
    return os.path.relpath(path, ROOT)


def check_schema(uslm_files):
    print("1. Schema validation (xmllint)")
    for f in uslm_files:
        result = subprocess.run(
            ["xmllint", "--noout", "--schema", SCHEMA, f],
            capture_output=True, text=True,
        )
        ok = result.returncode == 0
        print(f"   {'OK  ' if ok else 'FAIL'} {rel(f)}")
        if not ok:
            failures.append(f"schema: {rel(f)}\n{result.stderr.strip()}")


def check_json(json_files):
    print("2. JSON well-formedness")
    for f in json_files:
        try:
            json.load(open(f))
            print(f"   OK   {rel(f)}")
        except Exception as exc:  # noqa: BLE001
            print(f"   FAIL {rel(f)}")
            failures.append(f"json: {rel(f)}: {exc}")


def load_rdflib():
    try:
        import rdflib  # noqa: F401
        return rdflib
    except ImportError:
        return None


def check_ontology(rdflib):
    print("3. Ontology (Turtle)")
    if rdflib is None:
        print("   SKIP (rdflib not installed)")
        notes.append("ontology parse + conformance skipped: pip install rdflib")
        return None
    g = rdflib.Graph()
    try:
        g.parse(ONTOLOGY, format="turtle")
        print(f"   OK   {rel(ONTOLOGY)} ({len(g)} triples)")
        return g
    except Exception as exc:  # noqa: BLE001
        print(f"   FAIL {rel(ONTOLOGY)}")
        failures.append(f"ontology: {exc}")
        return None


def declared_terms(graph, rdflib):
    """Local names of every pol: term defined in the ontology."""
    pol = "https://policy.usmc.mil/ns#"
    terms = set()
    for s in set(graph.subjects()):
        if isinstance(s, rdflib.URIRef) and str(s).startswith(pol):
            terms.add(str(s)[len(pol):])
    return terms


def pol_terms_used(obj):
    """Every pol:* term referenced anywhere in a parsed JSON-LD value."""
    used = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "@type" and isinstance(v, str) and v.startswith("pol:"):
                used.add(v[4:])
            used |= pol_terms_used(v)
    elif isinstance(obj, list):
        for v in obj:
            used |= pol_terms_used(v)
    elif isinstance(obj, str) and obj.startswith("pol:"):
        used.add(obj[4:])
    return used


def check_conformance(graph, rdflib, jsonld_files):
    print("4. JSON-LD conforms to ontology")
    if graph is None:
        print("   SKIP")
        return
    declared = declared_terms(graph, rdflib)
    for f in jsonld_files:
        doc = json.load(open(f))
        # @context maps shorthand keys -> pol: terms; gather both context terms
        # and inline pol: usages, then ignore the JSON-LD keywords.
        used = pol_terms_used(doc)
        ctx = doc.get("@context", {})
        for v in ctx.values():
            term = v.get("@id") if isinstance(v, dict) else v
            if isinstance(term, str) and term.startswith("pol:"):
                used.add(term[4:])
        unknown = sorted(t for t in used if t and t not in declared)
        ok = not unknown
        print(f"   {'OK  ' if ok else 'FAIL'} {rel(f)}")
        if not ok:
            failures.append(f"conformance: {rel(f)} uses undeclared pol: terms: {unknown}")


def collect_identifiers(uslm_files):
    ids = set()
    for f in uslm_files:
        ids |= set(re.findall(r'identifier="(/[^"]+)"', open(f).read()))
    return ids


def check_references(ids, rules_files, jsonld_files):
    print("5. Referential integrity (citations -> markup)")
    for f in rules_files:
        doc = json.load(open(f))
        for r in doc.get("rules", []):
            cid = r.get("citation", {}).get("identifier", "")
            ok = cid in ids
            print(f"   {'OK  ' if ok else 'FAIL'} {r['id']:28} -> {cid}  [{rel(f)}]")
            if not ok:
                failures.append(f"reference: {rel(f)} {r['id']} -> {cid} not in markup")
    for f in jsonld_files:
        doc = json.load(open(f))
        for n in doc.get("@graph", []):
            if n.get("@type") == "pol:Provision":
                cid = n.get("@id", "")
                ok = cid in ids
                print(f"   {'OK  ' if ok else 'FAIL'} provision {cid}  [{rel(f)}]")
                if not ok:
                    failures.append(f"reference: {rel(f)} provision {cid} not in markup")


def main():
    uslm = sorted(glob.glob(os.path.join(DATA, "*.uslm.xml")))
    jsonld = sorted(glob.glob(os.path.join(DATA, "*.jsonld")))
    rules = sorted(glob.glob(os.path.join(DATA, "*.rules.json")))
    other_json = sorted(set(glob.glob(os.path.join(DATA, "*.json"))) - set(rules))

    rdflib = load_rdflib()
    check_schema(uslm)
    check_json(rules + other_json + jsonld)
    graph = check_ontology(rdflib)
    check_conformance(graph, rdflib, jsonld)
    ids = collect_identifiers(uslm)
    check_references(ids, rules, jsonld)

    print()
    for n in notes:
        print(f"note: {n}")
    if failures:
        print(f"\nFAILED: {len(failures)} problem(s)")
        for x in failures:
            print(f"  - {x}")
        sys.exit(1)
    print(f"\nPASS: {len(uslm)} document(s) validated, all references resolve.")


if __name__ == "__main__":
    main()
