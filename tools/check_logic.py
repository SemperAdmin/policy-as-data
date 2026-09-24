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
  7. Every operator is one tools/engine.py implements, and every node has the
     shape its operator needs: required keys present, the right number of
     args, and a format template whose placeholders are exactly its args.
     The engine's operators are partial; this is where their shape is gated,
     so a malformed node is a FAIL line here and never a traceback there.
  8. basis is 'cited' or 'inferred' (CLAUDE.md section 2.4).
  9. Fact names are unique and input names are unique.
 10. Every clause and refusal citation obeys NAMESPACES.md N3/N4 and names a
     paragraph that exists in a USLM file under data/ or data/exports/.

Usage:
  python tools/check_logic.py
  python tools/check_logic.py --data <dir> --identifiers <dir> --identifiers <dir>
"""

from __future__ import annotations

import argparse
import json
import re
import string
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


# Operator shapes. Arity is (minimum, maximum) over a list-valued "args";
# None for maximum means unbounded. Keys are the other fields a node must carry.
ARITY = {
    **{op: (2, 2) for op in ("lt", "le", "gt", "ge", "eq", "add", "sub", "mul",
                             "add_days", "days_between")},
    **{op: (1, 1) for op in ("abs", "iso")},
    **{op: (1, None) for op in ("and", "max", "min")},
}
KEYS = {"const": ("value",), "input": ("name",), "present": ("name",), "rule": ("id",),
        "fact": ("name",), "if": ("cond", "then", "else"), "format": ("template", "args")}


def placeholders(template: str) -> set:
    """Field names a str.format template reads, as the engine will call it."""
    names = set()
    for _literal, field, _spec, _conv in string.Formatter().parse(template):
        if field is not None:
            names.add(re.split(r"[.\[]", field, maxsplit=1)[0])
    return names


def shape_errors(node) -> list:
    """What is wrong with one node's shape, ignoring its children. Never indexes
    a key it has not checked, so a malformed node yields messages, not a
    traceback."""
    op = node["op"]
    out = [f"op {op!r} needs {k!r}" for k in KEYS.get(op, ()) if k not in node]
    if op in ARITY:
        args = node.get("args")
        lo, hi = ARITY[op]
        if not isinstance(args, list):
            out.append(f"op {op!r} needs args as a list")
        elif len(args) < lo or (hi is not None and len(args) > hi):
            want = f"exactly {lo}" if lo == hi else f"at least {lo}"
            out.append(f"op {op!r} arity: needs {want} arg(s), has {len(args)}")
    if op == "format" and "template" in node and "args" in node:
        template, args = node["template"], node["args"]
        if not isinstance(template, str):
            out.append("op 'format' template must be a string")
        elif not isinstance(args, dict):
            out.append("op 'format' args must be an object")
        else:
            try:
                names = placeholders(template)
            except ValueError as exc:
                out.append(f"op 'format' template does not parse: {exc}")
            else:
                if names - set(args):
                    out.append(f"format placeholder(s) {sorted(names - set(args))} "
                               "not supplied in args")
                if set(args) - names:
                    out.append(f"format args {sorted(set(args) - names)} "
                               "name no placeholder in the template")
    return out


def children(node):
    op = node["op"]
    if op == "format":
        args = node.get("args")
        return list(args.values()) if isinstance(args, dict) else []
    if op == "if":
        return [node[k] for k in ("cond", "then", "else") if k in node]
    args = node.get("args", [])
    return list(args) if isinstance(args, list) else []


def walk(node, where, errors):
    if not isinstance(node, dict) or node.get("op") not in OPS:
        errors.append(f"{where}: not a known expression: {json.dumps(node)[:80]}")
        return
    errors.extend(f"{where}: {e}" for e in shape_errors(node))
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
    input_names = [i.get("name") for i in doc.get("inputs", [])]
    fact_names = [f.get("name") for f in doc.get("facts", [])]
    for kind, names in (("input", input_names), ("fact", fact_names)):
        for name in sorted({n for n in names if names.count(n) > 1}, key=str):
            errors.append(f"{path.name}: duplicate {kind} name {name!r}")
    inputs = set(input_names)
    facts = {f.get("name"): f.get("expr") for f in doc.get("facts", [])}

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
