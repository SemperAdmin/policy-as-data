"""Static checks on data/*.logic.json. Writes nothing.

A clause file that fails here does not ship: build.sh stops. These are the
engine's termination and citation guarantees, enforced before anything runs.

  1. Every clause has id (unique), item, cite, requires, citation, basis, value.
  2. cite is requires[0]; every rule named exists in the rules file.
  3. Every rule a clause reads directly is in its requires list. Rules reached
     only through a fact are dynamic dependencies, reported by the engine.
  4. A guard reads no rule, directly or through a fact.
  5. Every input read is declared; every fact read is defined.
  6. The fact graph is acyclic. This is the termination guarantee.
  7. Every operator is one tools/engine.py implements.
  8. basis is 'cited' or 'inferred' (CLAUDE.md section 2.4).
  9. Every clause and refusal citation obeys NAMESPACES.md N3/N4 and names a
     paragraph that exists in a USLM file under data/ or data/exports/.

Usage:
  python tools/check_logic.py
  python tools/check_logic.py --data <dir> --identifiers <dir> --identifiers <dir>
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import OPS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IDENTIFIER = re.compile(r"^/us(/[a-z0-9_-]+)+$")
IDENT_ATTR = re.compile(r'identifier="([^"]+)"')
REQUIRED_KEYS = ("id", "item", "cite", "requires", "citation", "basis", "value")


def known_identifiers(dirs) -> set:
    found = set()
    for d in dirs:
        for path in sorted(Path(d).glob("*.xml")):
            found.update(IDENT_ATTR.findall(path.read_text(encoding="utf-8")))
    return found


def children(node):
    if node["op"] == "format":
        return list(node["args"].values())
    if node["op"] == "if":
        return [node["cond"], node["then"], node["else"]]
    return list(node.get("args", []))


def walk(node, where, errors):
    if not isinstance(node, dict) or node.get("op") not in OPS:
        errors.append(f"{where}: not a known expression: {json.dumps(node)[:80]}")
        return
    yield node
    for child in children(node):
        yield from walk(child, where, errors)


def check_refs(node, where, rule_ids, inputs, facts, errors):
    op = node["op"]
    if op == "rule" and node.get("id") not in rule_ids:
        errors.append(f"{where}: unknown rule {node.get('id')!r}")
    if op in ("input", "present") and node.get("name") not in inputs:
        errors.append(f"{where}: undeclared input {node.get('name')!r}")
    if op == "fact" and node.get("name") not in facts:
        errors.append(f"{where}: undefined fact {node.get('name')!r}")


def cyclic_facts(graph: dict) -> list:
    """Kahn's algorithm. Returns the facts left on a cycle; empty means acyclic."""
    remaining = {n: set(deps) & set(graph) for n, deps in graph.items()}
    while True:
        free = [n for n, deps in remaining.items() if not deps]
        if not free:
            return sorted(remaining)
        for n in free:
            del remaining[n]
        for deps in remaining.values():
            deps.difference_update(free)


def rules_reached(node, facts, where, errors) -> set:
    """Every rule read by an expression, through facts. Call only when acyclic."""
    out = set()
    for n in walk(node, where, errors):
        if n["op"] == "rule":
            out.add(n.get("id"))
        elif n["op"] == "fact" and n.get("name") in facts:
            out |= rules_reached(facts[n["name"]], facts, where, errors)
    return out


def check_citation(citation, where, idents, errors):
    ident = (citation or {}).get("identifier", "")
    if not IDENTIFIER.match(ident):
        errors.append(f"{where}: citation {ident!r} violates NAMESPACES.md N3/N4")
    elif ident not in idents:
        errors.append(f"{where}: citation {ident!r} is not a paragraph in any USLM file")
    if not (citation or {}).get("label"):
        errors.append(f"{where}: citation has no label")


def check_file(path: Path, idents: set) -> list:
    errors = []
    doc = json.loads(path.read_text(encoding="utf-8"))
    rules_path = path.parent / doc.get("rules_file", "")
    if not rules_path.is_file():
        return [f"{path.name}: rules_file {doc.get('rules_file')!r} not found"]
    rule_ids = {r["id"] for r in json.loads(rules_path.read_text(encoding="utf-8"))["rules"]}
    inputs = {i["name"] for i in doc.get("inputs", [])}
    facts = {f["name"]: f["expr"] for f in doc.get("facts", [])}

    graph = {}
    for name, expr in facts.items():
        where = f"{path.name} fact {name}"
        graph[name] = set()
        for n in walk(expr, where, errors):
            check_refs(n, where, rule_ids, inputs, facts, errors)
            if n["op"] == "fact":
                graph[name].add(n.get("name"))
    cycle = cyclic_facts(graph)
    if cycle:
        errors.append(f"{path.name}: fact cycle among {cycle} - "
                      "the engine could not be proven to terminate")
        return errors

    seen = set()
    for c in doc.get("clauses", []):
        where = f"{path.name} clause {c.get('id', '?')}"
        missing = [k for k in REQUIRED_KEYS if k not in c]
        if missing:
            errors.append(f"{where}: missing {missing}")
            continue
        if c["id"] in seen:
            errors.append(f"{where}: duplicate id")
        seen.add(c["id"])
        if c["basis"] not in ("cited", "inferred"):
            errors.append(f"{where}: basis must be 'cited' or 'inferred'")
        if not c["requires"] or c["requires"][0] != c["cite"]:
            errors.append(f"{where}: cite must be requires[0]")
        for r in c["requires"]:
            if r not in rule_ids:
                errors.append(f"{where}: unknown rule {r!r} in requires")
        direct = set()
        for key in ("when", "value", "note"):
            if key in c:
                for n in walk(c[key], where, errors):
                    check_refs(n, where, rule_ids, inputs, facts, errors)
                    if n["op"] == "rule":
                        direct.add(n.get("id"))
        undeclared = sorted(direct - set(c["requires"]))
        if undeclared:
            errors.append(f"{where}: reads rule(s) {undeclared} not in requires")
        if "guard" in c:
            for n in walk(c["guard"], where, errors):
                check_refs(n, where, rule_ids, inputs, facts, errors)
            if rules_reached(c["guard"], facts, where, errors):
                errors.append(f"{where}: guard reads a rule; "
                              "a guard decides applicability from inputs only")
        check_citation(c["citation"], where, idents, errors)

    for r in doc.get("refusals", []):
        where = f"{path.name} refusal {r.get('id', '?')}"
        if not r.get("text"):
            errors.append(f"{where}: no text")
        check_citation(r.get("citation"), where, idents, errors)
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(ROOT / "data"))
    ap.add_argument("--identifiers", action="append",
                    help="directory of USLM files; repeatable; default data/ and data/exports/")
    args = ap.parse_args()
    idents = known_identifiers(args.identifiers or [ROOT / "data", ROOT / "data" / "exports"])
    files = sorted(Path(args.data).glob("*.logic.json"))
    errors = []
    for path in files:
        errors += check_file(path, idents)
    errors = list(dict.fromkeys(errors))
    for e in errors:
        print(f"  FAIL {e}", file=sys.stderr)
    count = sum(len(json.loads(p.read_text(encoding="utf-8")).get("clauses", [])) for p in files)
    print(f"    {count} clause(s) in {len(files)} logic file(s): {'FAIL' if errors else 'OK'}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
