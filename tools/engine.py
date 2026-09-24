"""Clause engine - decision logic as verified data, not as Python.

Evaluates data/<doc>.logic.json against the rule values in the rules file it
names. Successor to the hand-written logic in tools/evaluate.py, which it must
reproduce exactly before it replaces it (EVALUATOR-PLAN.md, M1).

Discipline, inherited from tools/evaluate.py and extended to the logic:
- Rule VALUES come from the rules file. Clause LOGIC comes from the logic file.
  Neither is written here.
- A rule the ledger has not admitted is never used, and neither is a clause.
  A line resting on either is WITHHELD and names what it waits on.
- Every emitted line cites. The proof block names the clause, the paragraph the
  clause was read from, whether that reading is cited or inferred, and every
  rule and input the line touched.

Why it always terminates: facts form an acyclic graph (tools/check_logic.py
rejects a cycle before the build ships), every expression is a finite tree,
and every operator is total. No recursion, no search, no solver. This is not
Datalog; recursion is a revisit trigger, not a feature.

Usage:
  python tools/engine.py --input event_date=2027-03-01 --input as_of=2027-06-01
  python tools/engine.py --logic data/maradmin-051-23.logic.json \\
      --input event_date=2027-03-01 --input proposed_increment=5 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import (  # noqa: E402
    clause_assertion_id, clause_dependency_hash, rule_assertion_id, rule_hash)
from verify_status import LEDGER, POLICY, VERIFIED, derive, load_ledger, load_policy  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LOGIC_DEFAULT = ROOT / "data" / "maradmin-051-23.logic.json"


class EngineError(Exception):
    """A clause could not be evaluated. Names what failed; never guesses."""


class Tainted:
    """A value that rests on at least one rule the ledger has not admitted.
    It propagates instead of computing, so nothing derived from an unadmitted
    value can reach the output."""
    __slots__ = ("rules",)

    def __init__(self, rules):
        self.rules = tuple(dict.fromkeys(rules))


def taint_of(*values):
    rules = [r for v in values if isinstance(v, Tainted) for r in v.rules]
    return Tainted(rules) if rules else None


STRICT = {
    "lt": lambda a, b: a < b,
    "le": lambda a, b: a <= b,
    "gt": lambda a, b: a > b,
    "ge": lambda a, b: a >= b,
    "eq": lambda a, b: a == b,
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "abs": lambda a: abs(a),
    "max": lambda *a: max(a),
    "min": lambda *a: min(a),
    "add_days": lambda d, n: d + timedelta(days=n),
    "days_between": lambda a, b: (b - a).days,
    "iso": lambda d: d.isoformat(),
}
OPS = set(STRICT) | {"const", "input", "present", "rule", "fact", "and", "if", "format"}


class Context:
    """One evaluation: admitted rules, fact definitions, typed inputs, and the
    record of what each clause touched, for the proof."""

    def __init__(self, rules, facts, inputs):
        self.rules = rules
        self.facts = facts
        self.inputs = inputs
        self.memo = {}
        self.rules_touched = []
        self.inputs_touched = []


def ev(node, cx):
    op = node["op"]
    if op == "const":
        return node["value"]
    if op == "input":
        cx.inputs_touched.append(node["name"])
        return cx.inputs[node["name"]]
    if op == "present":
        cx.inputs_touched.append(node["name"])
        return cx.inputs[node["name"]] is not None
    if op == "rule":
        rule = cx.rules[node["id"]]
        cx.rules_touched.append(node["id"])
        return rule["value"] if rule["verification"] == VERIFIED else Tainted([node["id"]])
    if op == "fact":
        name = node["name"]
        if name not in cx.memo:
            r0, i0 = len(cx.rules_touched), len(cx.inputs_touched)
            value = ev(cx.facts[name], cx)
            cx.memo[name] = (value, cx.rules_touched[r0:], cx.inputs_touched[i0:])
            return value
        value, rules_seen, inputs_seen = cx.memo[name]
        cx.rules_touched.extend(rules_seen)
        cx.inputs_touched.extend(inputs_seen)
        return value
    if op == "and":
        pending = []
        for arg in node["args"]:
            v = ev(arg, cx)
            if isinstance(v, Tainted):
                pending.append(v)
            elif not v:
                return False
        return taint_of(*pending) or True
    if op == "if":
        cond = ev(node["cond"], cx)
        if isinstance(cond, Tainted):
            return taint_of(cond, ev(node["then"], cx), ev(node["else"], cx))
        return ev(node["then"] if cond else node["else"], cx)
    if op == "format":
        values = {k: ev(v, cx) for k, v in node["args"].items()}
        return taint_of(*values.values()) or node["template"].format(**values)
    if op not in STRICT:
        raise EngineError(f"unknown op {op!r}")
    args = [ev(a, cx) for a in node["args"]]
    tainted = taint_of(*args)
    if tainted:
        return tainted
    try:
        return STRICT[op](*args)
    except (TypeError, ValueError) as exc:
        raise EngineError(f"op {op!r} failed on {args!r}: {exc}") from exc


def bind_inputs(spec, given, today=None):
    """Declared inputs in declared order. Returns (scenario, typed): scenario is
    what the output records, typed is what the clauses read."""
    unknown = sorted(set(given) - {i["name"] for i in spec})
    if unknown:
        raise EngineError(f"undeclared input(s): {unknown}")
    scenario, typed = {}, {}
    for inp in spec:
        name = inp["name"]
        raw = given.get(name, inp.get("default"))
        if raw is None and inp.get("required"):
            raise EngineError(f"input {name} is required")
        if raw is None:
            value = (today or date.today()) if inp.get("default_today") else None
        elif inp["type"] == "date":
            value = raw if isinstance(raw, date) else datetime.strptime(raw, "%Y-%m-%d").date()
        elif inp["type"] == "int":
            value = int(raw)
        else:
            raise EngineError(f"input {name}: unknown type {inp['type']!r}")
        scenario[name] = value if inp["type"] == "int" and raw is not None else raw
        typed[name] = value
    return scenario, typed


def admit(live, ledger, quorum):
    return {row["assertion"]: row["status"] for row in derive(live, ledger, quorum)}


def blocker(rid, rules):
    return f"{rid} [{rules[rid]['verification']}]"


def evaluate_clauses(doc, rules, clause_status, inputs, identifier):
    cx = Context(rules, {f["name"]: f["expr"] for f in doc.get("facts", [])}, inputs)
    findings, withheld, proof = [], [], []
    groups = {}
    for c in doc["clauses"]:
        groups.setdefault(c["item"], []).append(c)
    for item, clauses in groups.items():
        # First match: a line rests on every clause tried ahead of the one that
        # answers, because each of those decided not to answer. So what they
        # touched accumulates across the group and lands in the proof.
        cx.rules_touched, cx.inputs_touched = [], []
        for i, c in enumerate(clauses):
            earlier = clauses[:i]
            # An earlier clause the ledger has not admitted blocks this one
            # whatever its guard says. Its guard is part of unadmitted logic
            # too, so a false guard is no evidence it would not have answered.
            prior_blockers = [f"logic/{e['id']} [{clause_status[e['id']]}]" for e in earlier
                              if clause_status[e["id"]] != VERIFIED]
            if "guard" in c and not ev(c["guard"], cx):
                continue
            blockers = [blocker(r, rules) for r in c["requires"]
                        if rules[r]["verification"] != VERIFIED]
            blockers += prior_blockers
            if clause_status[c["id"]] != VERIFIED:
                blockers.append(f"logic/{c['id']} [{clause_status[c['id']]}]")
            when = ev(c["when"], cx) if "when" in c else True
            if not blockers and not isinstance(when, Tainted) and not when:
                continue
            value = ev(c["value"], cx)
            note = ev(c["note"], cx) if "note" in c else ""
            dynamic = taint_of(when, value, note)
            if dynamic:
                named = {b.split(" [")[0] for b in blockers}
                blockers += [blocker(r, rules) for r in dynamic.rules if r not in named]
            cited = rules[c["cite"]]["citation"]
            if blockers:
                withheld.append({"item": item, "citation": cited["label"],
                                 "identifier": cited["identifier"],
                                 "withheld_because": blockers})
            else:
                findings.append({"item": item, "value": value, "citation": cited["label"],
                                 "identifier": cited["identifier"], "note": note})
                proof.append({"item": item,
                              "clause": clause_assertion_id(identifier, c["id"]),
                              "basis": c["basis"],
                              "clause_citation": c["citation"],
                              "rules": sorted(set(cx.rules_touched)),
                              "inputs": sorted(set(cx.inputs_touched)),
                              "preceded_by": [e["id"] for e in earlier]})
            break
    return findings, withheld, proof


def run(logic_path, inputs, *, ledger_path=LEDGER, policy_path=POLICY, today=None) -> dict:
    """The decision, as data, with its proof. Callable in-process by renderers
    and by the claims table, so the page, the CLI and the tests are one
    implementation."""
    logic_path = Path(logic_path)
    doc = json.loads(logic_path.read_text(encoding="utf-8"))
    rules_doc = json.loads((logic_path.parent / doc["rules_file"]).read_text(encoding="utf-8"))
    identifier = rules_doc["source"]["identifier"]
    quorum, deviation = load_policy(Path(policy_path))
    ledger = load_ledger(Path(ledger_path))

    rule_live = {rule_assertion_id(identifier, r["id"]):
                 {"assertion": rule_assertion_id(identifier, r["id"]), "kind": "rule",
                  "hash": rule_hash(r)} for r in rules_doc["rules"]}
    rule_status = admit(rule_live, ledger, quorum)
    rules = {r["id"]: {**r, "verification": rule_status[rule_assertion_id(identifier, r["id"])]}
             for r in rules_doc["rules"]}

    clause_live = {clause_assertion_id(identifier, c["id"]):
                   {"assertion": clause_assertion_id(identifier, c["id"]), "kind": "clause",
                    "hash": clause_dependency_hash(doc, c["id"])} for c in doc["clauses"]}
    admitted = admit(clause_live, ledger, quorum)
    clause_status = {c["id"]: admitted[clause_assertion_id(identifier, c["id"])]
                     for c in doc["clauses"]}

    scenario, typed = bind_inputs(doc["inputs"], inputs, today)
    findings, withheld, proof = evaluate_clauses(doc, rules, clause_status, typed, identifier)

    status = {rid: r["verification"] for rid, r in rules.items()}
    unadmitted = sorted(rid for rid, st in status.items() if st != VERIFIED)
    return {"source": rules_doc["source"]["label"], "scenario": scenario,
            "decision": findings, "withheld": withheld,
            "out_of_scope": [r["text"] for r in doc.get("refusals", [])],
            "verification": {"by_rule": status,
                             "quorum_deviation": deviation,
                             "summary": ("all rules VERIFIED in the ledger" if not unadmitted
                                         else f"{len(unadmitted)} rule(s) not admitted; "
                                              f"lines depending on them withheld: {unadmitted}"),
                             "by_clause": clause_status},
            "proof": proof}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--logic", default=str(LOGIC_DEFAULT))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--input", action="append", default=[], metavar="NAME=VALUE")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    given = dict(pair.split("=", 1) for pair in args.input)
    try:
        result = run(args.logic, given, ledger_path=args.ledger, policy_path=args.policy)
    except EngineError as exc:
        print(f"engine: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0
    print(f"Decision basis: {result['source']}")
    print(f"Verification: {result['verification']['summary']}\n")
    proof = {p["item"]: p for p in result["proof"]}
    for line in result["decision"]:
        p = proof[line["item"]]
        note = f"  ({line['note']})" if line["note"] else ""
        print(f"  {line['item']}: {line['value']}{note}")
        print(f"      per {line['citation']}  [{line['identifier']}]")
        print(f"      logic {p['basis']} from {p['clause_citation']['label']}; "
              f"rules {', '.join(p['rules']) or '-'}; inputs {', '.join(p['inputs']) or '-'}")
    for w in result["withheld"]:
        print(f"  {w['item']}: WITHHELD - depends on {', '.join(w['withheld_because'])}")
        print(f"      would cite {w['citation']}  [{w['identifier']}]")
    print("\nNot answerable from encoded rules:")
    for r in result["out_of_scope"]:
        print(f"  - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
