#!/usr/bin/env python3
"""Run the claims table in tests/claims.json and print it, Table I style.

Each row is a claim the tooling makes about itself, the mechanism that tests
it, and the expected result. Positive rows expect a result to be derivable;
negative rows expect it NOT to be. The negatives are the rows that matter: a
tool that answered everything asked of it would pass every positive row and
fail every negative one.

This script writes nothing to the repository. Fixtures for the CLI claim go to
a temporary directory that is removed afterwards. Exit status is 1 on any
FAIL and 0 otherwise, so CI can gate on it.

Usage:
    python tests/run_claims.py
    python tests/run_claims.py --json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
CLAIMS = ROOT / "tests" / "claims.json"
sys.path.insert(0, str(TOOLS))

import reconcile as rc  # noqa: E402
from verify_status import derive  # noqa: E402


# --------------------------------------------------------------------------
# Fixture helpers
# --------------------------------------------------------------------------

def resolve_units(spec, fixtures):
    """'config' means the live table; any other key is an inline fixture."""
    if spec == "config":
        return rc.load_units(rc.UNITS)
    doc = fixtures[spec]
    table = {(c["from"], c["to"]): c for c in doc["conversions"]}
    refused = {r["unit"]: r["reason"] for r in doc.get("refused", [])}
    return table, refused


def resolve_concepts(spec, fixtures):
    if spec == "config":
        return json.loads(rc.CONCEPTS.read_text(encoding="utf-8"))["concepts"]
    return fixtures[spec]


def make_items(rows):
    """Minimal fixture rows into the shape reconcile.gather() produces."""
    items = []
    for n, r in enumerate(rows, 1):
        tier = r["tier"]
        items.append({
            "assertion": f"/fixture/{tier}#R{n}",
            "concept": r.get("concept"),
            "rule_id": f"R{n}",
            "value": r["value"],
            "unit": r["unit"],
            "tier": tier,
            "tier_label": f"fixture {tier}",
            "document": f"fixture document {tier}",
            "document_identifier": f"/fixture/{tier}",
            "source_url": None,
            "citation_label": f"fixture {tier} para {n}",
            "citation_identifier": f"/fixture/{tier}/p{n}",
            "verification": r["verification"],
        })
    return items


# --------------------------------------------------------------------------
# Mechanisms. Each returns (actual: dict, failures: list[str]).
# --------------------------------------------------------------------------

def check(expect, actual):
    """Compare every expectation key against the actual dict."""
    fails = []
    for key, want in expect.items():
        if key.endswith("_not"):
            base = key[:-4]
            if actual.get(base) == want:
                fails.append(f"{base} is {want!r}, expected anything else")
        elif actual.get(key) != want:
            fails.append(f"{key}: expected {want!r}, got {actual.get(key)!r}")
    return fails


def mech_reconcile(fx, fixtures):
    concepts = resolve_concepts(fx["concepts"], fixtures)
    table, refused = resolve_units(fx["units"], fixtures)
    findings = rc.reconcile(concepts, make_items(fx["items"]), table, refused)
    f = findings[0]
    printed_values = [t.get("stated") for t in f["tiers"]]
    withheld_rows = f["withheld"]
    actual = {
        "verdict": f["verdict"],
        "tiers_printed": len(f["tiers"]),
        "canonical": [t["canonical"] for t in f["tiers"]],
        "withheld": len(withheld_rows),
        "not_comparable": len(f["not_comparable"]),
        # B1: a withheld row carries no value key at all, not a masked one.
        "withheld_value_absent": all(
            "stated" not in w and "canonical" not in w and "value" not in w
            for w in withheld_rows) and not any(
            v is None for v in printed_values),
    }
    return actual


def mech_reconcile_unassigned(fx, fixtures):
    items = make_items(fx["items"])
    return {"unassigned": len([i for i in items if not i.get("concept")])}


def mech_units(fx, fixtures):
    table, refused = resolve_units(fx["units"], fixtures)
    converted, problem = rc.convert(fx["value"], fx["unit"], fx["target"], table, refused)
    return {"refused": converted is None and bool(problem), "reason": problem}


def mech_verify_status(fx, fixtures):
    aid = "/fixture#R1"
    live = {aid: {"assertion": aid, "kind": fx["kind"], "hash": fx["hash"]}}
    ledger = {aid: [dict(a, assertion=aid, kind=fx["kind"]) for a in fx["attestations"]]}
    row = derive(live, ledger, fx["quorum"])[0]
    return {"status": row["status"], "detail": row.get("detail")}


def mech_evaluate(fx, fixtures):
    proc = subprocess.run(
        [sys.executable, str(TOOLS / "evaluate.py"), *fx["args"], "--json"],
        capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        return {"error": proc.stderr.strip()[-400:]}
    out = json.loads(proc.stdout)
    lines = out["decision"]
    refusals = " ".join(out["out_of_scope"])
    actual = {
        "every_decision_line_has_identifier": all(
            str(l.get("identifier", "")).startswith("/us/") for l in lines),
        "min_decision_lines": len(lines),
    }
    return actual, {"lines": lines, "refusals": refusals}


def eval_extra_checks(expect, actual, extra):
    """Expectations that are not plain equality: substring and pattern checks."""
    fails = []
    if "refusals_mention" in expect:
        for needle in expect["refusals_mention"]:
            if needle not in extra["refusals"]:
                fails.append(f"refusals do not mention {needle!r}")
    if "min_decision_lines" in expect:
        if actual["min_decision_lines"] < expect["min_decision_lines"]:
            fails.append(f"only {actual['min_decision_lines']} decision lines")
    if "no_decision_item_matching" in expect:
        needle = expect["no_decision_item_matching"].lower()
        hits = [l["item"] for l in extra["lines"] if needle in str(l["item"]).lower()]
        if hits:
            fails.append(f"decision items match {needle!r}: {hits}")
    return fails


def mech_reconcile_cli(fx, fixtures):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "fixture.rules.json").write_text(
            json.dumps(fx["rules_file"], indent=2), encoding="utf-8")
        (tmp / "empty.jsonl").write_text("", encoding="utf-8")
        out = tmp / "out.json"
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "reconcile.py"),
             "--data", str(tmp), "--ledger", str(tmp / "empty.jsonl"),
             "--out", str(out)],
            capture_output=True, text=True, cwd=str(ROOT))
        return {
            "exit_nonzero": proc.returncode != 0,
            "stderr_mentions": fx["rules_file"]["rules"][0]["concept"]
            if fx["rules_file"]["rules"][0]["concept"] in proc.stderr else proc.stderr[-200:],
            "out_file_written": out.exists(),
        }


def mech_evaluate_fixture(fx, fixtures):
    """Evaluator against a fixture rules file and a fixture ledger, so the
    claim is about the evaluator's discipline, not about today's ledger."""
    from normalize import rule_assertion_id, rule_hash  # noqa: E402
    rules_doc = fixtures[fx["rules"]]
    ident = rules_doc["source"]["identifier"]
    by_id = {r["id"]: r for r in rules_doc["rules"]}
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        rules_path = tmp / "fixture.rules.json"
        rules_path.write_text(json.dumps(rules_doc, indent=2), encoding="utf-8")
        lines = []
        for a in fx.get("attest", []):
            rule = by_id[a["rule"]]
            for v in a["verifiers"]:
                lines.append(json.dumps({
                    "assertion": rule_assertion_id(ident, rule["id"]), "kind": "rule",
                    "content_hash": rule_hash(rule), "result": "VERIFIED",
                    "verifier": v, "at": "2026-09-11T00:00:00+00:00",
                    "method": "read-and-compare",
                    "verified_against": {"edition": "fixture", "obtained": "fixture",
                                         "artifact_hash": None}}))
        (tmp / "ledger.jsonl").write_text(chr(10).join(lines) + (chr(10) if lines else ""),
                                          encoding="utf-8")
        policy = tmp / "policy.json"
        policy.write_text(json.dumps({"quorum": fx.get("quorum", {"rule": 2, "provision": 1})}),
                          encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "evaluate.py"), "--rules", str(rules_path),
             "--ledger", str(tmp / "ledger.jsonl"), "--policy", str(policy),
             *fx["args"], "--json"],
            capture_output=True, text=True, cwd=str(ROOT))
    if proc.returncode != 0:
        return {"error": proc.stderr.strip()[-400:]}
    out = json.loads(proc.stdout)
    dec, wh = out["decision"], out["withheld"]
    return {
        "decision_lines": len(dec),
        "decision_items": [l["item"] for l in dec],
        "withheld_min": len(wh),
        "every_withheld_names_rule": all(w.get("withheld_because") for w in wh),
        "every_withheld_has_identifier": all(
            str(w.get("identifier", "")).startswith("/us/") for w in wh),
    }


def mech_report(fx, fixtures):
    """Consistency of the live authority report, which the currency and impact
    pages read. Live data by design: the claim is about the report the build
    just wrote, not about a fixture."""
    r = json.loads((ROOT / "config" / "authority_report.json").read_text(encoding="utf-8"))
    status = r.get("status", {})
    gone = r.get("cites_superseded_detail", [])
    drift = r.get("drift_edges", [])
    nb = r.get("named_by", {})
    return {
        "gone_targets_all_gone": all(status.get(d["target"]) in ("superseded", "cancelled") for d in gone),
        "gone_citers_all_active": all(status.get(d["citing"]) == "active" for d in gone),
        "drift_holds_equal_target": sum(1 for d in drift if d["target"] in d["holds"]),
        "named_by_sum_equals_edges": sum(len(v) for v in nb.values()) == r["totals"]["edges"],
    }


def mech_exports(fx, fixtures):
    """Element counts in data/exports against the per-document provision counts
    the authority report measured in the store. Config and exports only."""
    r = json.loads((ROOT / "config" / "authority_report.json").read_text(encoding="utf-8"))
    per = r.get("per_document", {})
    mismatch, total_el = [], 0
    for f in (ROOT / "data" / "exports").glob("*.issuance.xml"):
        did = f.name[:-len(".issuance.xml")]
        n = len(re.findall(r"<provision\b", f.read_text(encoding="utf-8", errors="replace")))
        total_el += n
        want = per.get(did, {}).get("provisions")
        if want is not None and want != n:
            mismatch.append((did, n, want))
    return {"docs_with_element_count_mismatch": len(mismatch), "mismatches": mismatch[:5],
            "total_elements_equal_total_provisions": total_el == r["totals"].get("provisions")}


def mech_clause_hash(fx, fixtures):
    from normalize import clause_hash  # noqa: E402
    base = fx["base"]
    return {"hash_changed": clause_hash(base) != clause_hash({**base, **fx["edit"]})}


DATA_DIR = ROOT / "data"
MPLP_RULES = DATA_DIR / "maradmin-051-23.rules.json"
MPLP_LOGIC = DATA_DIR / "maradmin-051-23.logic.json"


def _fixture_ledger(tmp, rules_doc, logic_doc, attest_rules, attest_clauses):
    """A two-verifier ledger admitting the named rules and clauses, quorum 2.
    'all' admits everything. Hashes are taken from the documents passed in, so a
    document mutated afterwards reads as INVALIDATED - which is the point."""
    from normalize import (  # noqa: E402
        clause_assertion_id, clause_dependency_hash, rule_assertion_id, rule_hash)
    ident = rules_doc["source"]["identifier"]

    def rec(aid, kind, digest, verifier):
        return json.dumps({"assertion": aid, "kind": kind, "content_hash": digest,
                           "result": "VERIFIED", "verifier": verifier,
                           "at": "2026-09-11T00:00:00+00:00", "method": "read-and-compare",
                           "verified_against": {"edition": "fixture", "obtained": "fixture",
                                                "artifact_hash": None}})

    lines = []
    for r in rules_doc["rules"]:
        if attest_rules == "all" or r["id"] in attest_rules:
            lines += [rec(rule_assertion_id(ident, r["id"]), "rule", rule_hash(r), v)
                      for v in ("V-001", "V-002")]
    for c in logic_doc["clauses"]:
        if attest_clauses == "all" or c["id"] in attest_clauses:
            digest = clause_dependency_hash(logic_doc, c["id"])
            lines += [rec(clause_assertion_id(ident, c["id"]), "clause", digest, v)
                      for v in ("V-001", "V-002")]
    ledger = tmp / "ledger.jsonl"
    ledger.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    policy = tmp / "policy.json"
    policy.write_text(json.dumps({"quorum": {"rule": 2, "provision": 1, "clause": 2}}),
                      encoding="utf-8")
    return ledger, policy


def mech_engine_parity(fx, fixtures):
    """The engine against tools/evaluate.py: same rules, same ledger, same inputs.
    Compared as sorted-key JSON, so this is a byte comparison and not a count.
    The engine's additions (proof, verification.by_clause and
    verification.clause_summary) are removed first;
    everything else must match exactly."""
    import engine as eg  # noqa: E402
    import evaluate as old  # noqa: E402
    rules_doc = json.loads(MPLP_RULES.read_text(encoding="utf-8"))
    logic_doc = json.loads(MPLP_LOGIC.read_text(encoding="utf-8"))
    cases = fixtures[fx["cases"]]
    mismatches = []
    with tempfile.TemporaryDirectory() as tmp:
        ledger, policy = _fixture_ledger(Path(tmp), rules_doc, logic_doc,
                                         fx["attest_rules"], fx["attest_clauses"])
        rules, source, deviation = old.load_rules(MPLP_RULES, ledger, policy)
        for args in cases:
            want = old.evaluate(rules, source, deviation, **args)
            got = eg.run(MPLP_LOGIC, args, ledger_path=ledger, policy_path=policy)
            got.pop("proof")
            got["verification"].pop("by_clause")
            got["verification"].pop("clause_summary")
            if json.dumps(want, sort_keys=True, default=str) != \
                    json.dumps(got, sort_keys=True, default=str):
                mismatches.append(args)
    return {"mismatches": mismatches}


def _step(target, key):
    """Path step. 'clause:ID' selects a clause by id, and 'fact:NAME' and
    'input:NAME' a fact or input by name, so a fixture does not depend on
    order in the file."""
    if isinstance(key, str):
        for prefix, field in (("clause:", "id"), ("fact:", "name"), ("input:", "name")):
            if key.startswith(prefix):
                return next(c for c in target if c[field] == key[len(prefix):])
    return target[key]


def _resolve(doc, path):
    target = doc
    for key in path:
        target = _step(target, key)
    return target


def apply_mutation(doc, m):
    """One edit. Forms: value (set path), append (to the list at path), remove
    (the element of the list at path), move ... before (reorder within the list
    at path). remove and move exist so an attested file can be edited by
    deletion and by reordering, not only by rewriting a value."""
    if "remove" in m:
        seq = _resolve(doc, m["path"])
        seq.remove(_step(seq, m["remove"]))
        return
    if "move" in m:
        seq = _resolve(doc, m["path"])
        moving = _step(seq, m["move"])
        seq.remove(moving)
        seq.insert(seq.index(_step(seq, m["before"])), moving)
        return
    target = _resolve(doc, m["path"][:-1])
    last = m["path"][-1]
    if "append" in m:
        _step(target, last).append(m["append"])
    else:
        target[last] = m["value"]


def mech_engine(fx, fixtures):
    """The engine on a temporary copy of the live clause file. The ledger is
    built from the file BEFORE any mutation, so a mutation is an edit made after
    attestation."""
    import engine as eg  # noqa: E402
    rules_doc = json.loads(MPLP_RULES.read_text(encoding="utf-8"))
    logic_doc = json.loads(MPLP_LOGIC.read_text(encoding="utf-8"))
    clauses = fx.get("attest_clauses")
    if "attest_clauses_except" in fx:
        clauses = [c["id"] for c in logic_doc["clauses"] if c["id"] not in fx["attest_clauses_except"]]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        ledger, policy = _fixture_ledger(tmp, rules_doc, logic_doc, fx["attest_rules"], clauses)
        for m in fx.get("mutations", []):
            apply_mutation(logic_doc, m)
        shutil.copy(MPLP_RULES, tmp / MPLP_RULES.name)
        logic_path = tmp / MPLP_LOGIC.name
        logic_path.write_text(json.dumps(logic_doc, indent=2), encoding="utf-8")
        out = eg.run(logic_path, fx["args"], ledger_path=ledger, policy_path=policy)
    blockers = {b for w in out["withheld"] for b in w["withheld_because"]}
    proof_item = next((p for p in out["proof"] if p["item"] == fx.get("proof_item")), None)
    return {
        "proof_for_item": proof_item and {k: proof_item.get(k)
                                          for k in ("rules", "inputs", "preceded_by")},
        "proof_matches_decision": [p["item"] for p in out["proof"]] == [l["item"] for l in out["decision"]],
        "every_proof_cited": all(str(p["clause_citation"].get("identifier", "")).startswith("/us/")
                                 and p["basis"] in ("cited", "inferred") for p in out["proof"]),
        "logic_blockers": sorted(b.split(" [")[0] for b in blockers if b.startswith("logic/")),
        "logic_blocker_states": sorted(b for b in blockers if b.startswith("logic/")),
        "withheld_items": sorted(w["item"] for w in out["withheld"]),
        "clause_summary": out["verification"]["clause_summary"],
        "decision_has_remaining_days": any(l["item"] == "remaining_days" for l in out["decision"]),
    }


def mech_check_logic(fx, fixtures):
    logic_doc = json.loads(MPLP_LOGIC.read_text(encoding="utf-8"))
    for m in fx["mutations"]:
        apply_mutation(logic_doc, m)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / MPLP_LOGIC.name).write_text(json.dumps(logic_doc, indent=2), encoding="utf-8")
        shutil.copy(MPLP_RULES, tmp / MPLP_RULES.name)
        proc = subprocess.run(
            [sys.executable, str(TOOLS / "check_logic.py"), "--data", str(tmp),
             "--identifiers", str(DATA_DIR), "--identifiers", str(DATA_DIR / "exports")],
            capture_output=True, text=True, cwd=str(ROOT))
    needle = fx["stderr_has"]
    return {"exit_nonzero": proc.returncode != 0,
            "stderr_has": needle if needle in proc.stderr else proc.stderr[-300:]}


MECHANISMS = {
    "exports": mech_exports,
    "report": mech_report,
    "evaluate_fixture": mech_evaluate_fixture,
    "reconcile": mech_reconcile,
    "reconcile_unassigned": mech_reconcile_unassigned,
    "units": mech_units,
    "verify_status": mech_verify_status,
    "evaluate": mech_evaluate,
    "check_logic": mech_check_logic,
    "reconcile_cli": mech_reconcile_cli,
    "clause_hash": mech_clause_hash,
    "engine_parity": mech_engine_parity,
    "engine": mech_engine,
}

# Keys handled by eval_extra_checks rather than plain equality.
NON_EQUALITY = {"refusals_mention", "min_decision_lines", "no_decision_item_matching",
                "withheld_min"}


def run_claim(claim, fixtures):
    mech = MECHANISMS[claim["mechanism"]]
    result = mech(claim["fixture"], fixtures)
    extra = None
    if isinstance(result, tuple):
        result, extra = result
    if "error" in result:
        return result, [f"mechanism error: {result['error']}"]
    plain = {k: v for k, v in claim["expect"].items() if k not in NON_EQUALITY}
    fails = check(plain, result)
    if extra is not None:
        fails += eval_extra_checks(claim["expect"], result, extra)
    if "withheld_min" in claim["expect"]:
        if result.get("withheld_min", 0) < claim["expect"]["withheld_min"]:
            fails.append(f"withheld {result.get('withheld_min')} lines, "
                         f"expected at least {claim['expect']['withheld_min']}")
    return result, fails


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    doc = json.loads(CLAIMS.read_text(encoding="utf-8"))
    fixtures = doc.get("fixtures", {})
    rows = []
    for claim in doc["claims"]:
        actual, fails = run_claim(claim, fixtures)
        rows.append({
            "id": claim["id"], "polarity": claim["polarity"],
            "claim": claim["claim"], "mechanism": claim["mechanism"],
            "expect": claim["expect"], "actual": actual,
            "result": "PASS" if not fails else "FAIL", "failures": fails,
        })

    failed = [r for r in rows if r["result"] == "FAIL"]
    if args.json:
        print(json.dumps({"claims": rows, "failed": len(failed)}, indent=2, default=str))
        return 1 if failed else 0

    print(f"Claims table - {len(rows)} claims, "
          f"{sum(r['polarity'] == 'positive' for r in rows)} positive, "
          f"{sum(r['polarity'] == 'negative' for r in rows)} negative\n")
    print(f"  {'id':<4} {'pol':<4} {'result':<5}  claim")
    for r in rows:
        pol = "yes" if r["polarity"] == "positive" else "no"
        print(f"  {r['id']:<4} {pol:<4} {r['result']:<5}  {r['claim']}")
        for f in r["failures"]:
            print(f"             ! {f}")
    print(f"\n{len(rows) - len(failed)} of {len(rows)} as expected, {len(failed)} FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
