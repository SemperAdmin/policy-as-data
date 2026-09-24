# Clause Engine Implementation Plan - decision logic as verified data

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Date: 2026-09-24. Owner: Stephen. Status: **APPROVED 2026-09-24** for subagent-driven execution. Owner ruling: clause quorum 1 under the existing one-verifier deviation, target 2.

**Goal:** Move the decision logic out of hand-written Python in `tools/evaluate.py` and into cited, attested data files, evaluated by a generic engine that always terminates and shows its reasoning. M1 proves this on parental leave by exact parity. M2 extends it to leave accrual (MCO 1050.3J).

**Architecture:** Rule *values* already live in `data/<doc>.rules.json` and pass through the attestation ledger. This plan adds `data/<doc>.logic.json`: an ordered list of clauses. Each clause is a condition and a result, cites the paragraph it was read from, is labelled `cited` or `inferred`, and is admitted by the same ledger that admits rule values. `tools/engine.py` evaluates clauses. `tools/check_logic.py` enforces the termination and citation guarantees statically, as a build stage.

**Tech Stack:** Python 3 standard library only. JSON data files. The existing claims-table harness in `tests/run_claims.py`. There is no pytest in this repository, and this plan does not add it.

**Spec:** This file is the spec. It follows from the conversation of 2026-09-24 and from `resources/28` (the SUMO adoption trigger) and `resources/31` (derived verdicts, the claims table).

## Why, in one paragraph

The project goal is an answer that is right every time by construction, not by an LLM's judgement. Today the values meet that bar and the logic does not: the `if/elif` in `evaluate.py` is unverified code. A logic engine is only as correct as its clauses, so clauses get the same treatment as values: paragraph citation, content hash, human attestation, and withholding when not admitted.

## What this engine is, stated honestly

It is **not** Datalog and not a theorem prover. It is a **non-recursive, ordered rule set with total built-in operators**. Facts form an acyclic graph, expressions are finite trees, and every operator returns for every input. That is the termination proof. Nothing in M1 or M2 needs recursion.

> **Corrected 2026-09-24 after final review.** "Total built-in operators" and "every operator returns for every input" were wrong. The operators are **partial**: `abs` given two args, `lt` comparing a date with an int, a `format` template naming a placeholder its args do not supply, and a missing key all raised raw Python exceptions. The accurate statement: the engine **always terminates; operators are partial and fail loudly with `EngineError`, never with a guess.** Termination still rests on the acyclic fact graph and finite trees, not on totality. `tools/check_logic.py` now gates operator shape statically (required keys, arity, format placeholders equal to args, unique fact and input names), and `tools/engine.py` wraps any `KeyError`, `IndexError`, `TypeError` or `ValueError` as an `EngineError` naming the op. The original sentence is kept above so the correction is visible.

**Revisit trigger:** the first requirement that needs recursion, such as transitive closure over authority chains. At that point evaluate a Datalog core, which still terminates, as part of the M3 decision.

## Global Constraints

Every task's requirements include these. They are copied from `CLAUDE.md` section 2 and section 11.

- `canonical/` is read-only to tooling. No task writes it.
- Machine output is UNVERIFIED. Promotion to VERIFIED is explicit, human, and recorded. No tool in this plan writes `VERIFIED` for a real assertion. Only test fixtures in temporary directories do.
- `cited` and `inferred` are never conflated. Every clause carries `basis: cited | inferred` and a paragraph citation.
- A gap is stated, never closed. If no paragraph states a piece of logic, no clause is written. A refusal is written instead.
- No period in an identifier (NAMESPACES.md N3/N4). This is enforced on every clause citation.
- The build is idempotent, proved by hashing, not by counts.
- `data/` is hand-tier. The logic files are hand-encoded and never machine-written.
- The repository is standalone: `./build.sh` on a fresh clone, stdlib Python, no new dependency.
- Writes go through `tools/atomicio.py`. The tools in this plan write nothing except `attest.py`, which already appends to the ledger by its own documented rule.
- Configuration lives in `config/`, never inlined.

---

## File map

| File | Action | Responsibility |
|---|---|---|
| `tools/normalize.py` | Modify | `clause_assertion`, `clause_hash`, `clause_assertion_id` |
| `tools/verify_status.py` | Modify | `live_clause_assertions`, `live_assertions`; `clause` in `TARGET_QUORUM`; CLI reports both kinds |
| `tools/attest.py` | Modify | Attest a clause: show it, bind `clause_hash`, record `kind: clause` |
| `config/verification_policy.json` | Modify | Quorum for `clause`. **Owner decision.** |
| `tools/engine.py` | Create | Generic evaluator: inputs, facts, clauses, withholding, proof |
| `data/maradmin-051-23.logic.json` | Create | The ten parental-leave clauses and three refusals, transcribed from `evaluate.py` |
| `tools/check_logic.py` | Create | Static checks, the build gate |
| `tests/run_claims.py` | Modify | Mechanisms `clause_hash`, `engine_parity`, `engine`, `check_logic` |
| `tests/claims.json` | Modify | Positive and negative rows for all of the above |
| `build.sh` | Modify | Stage 16a, `check_logic.py` |
| `tools/render_scenarios.py` | Modify, **gated on Task 7** | Render from the engine and show the proof |
| `SESSION_HANDOFF.md`, `BUILD.md` | Modify | Decision record, stage row |

`tools/evaluate.py` is **not modified** in M1. It is the reference implementation that the parity rows compare against. It retires after M2, by owner decision.

---

## Expression language (reference for Tasks 3-5)

Every expression is a JSON object with an `op` key.

| op | Shape | Meaning |
|---|---|---|
| `const` | `{"op":"const","value":V}` | literal |
| `input` | `{"op":"input","name":"x"}` | declared input, typed |
| `present` | `{"op":"present","name":"x"}` | the input was supplied (not None) |
| `rule` | `{"op":"rule","id":"RULE_ID"}` | rule value; **Tainted** if the ledger has not admitted it |
| `fact` | `{"op":"fact","name":"f"}` | named sub-expression, memoised |
| `and` | `{"op":"and","args":[...]}` | left to right; the first untainted false returns false; otherwise any taint wins |
| `if` | `{"op":"if","cond":C,"then":T,"else":E}` | a tainted condition taints the result with both branches' taint |
| `format` | `{"op":"format","template":"...{a}...","args":{"a":X}}` | string output |
| strict | `{"op":OP,"args":[...]}` | `lt le gt ge eq add sub mul abs max min add_days days_between iso` |

`days_between(a, b)` is `(b - a).days`, which is signed. A strict operator with any tainted argument returns the union of the taints and does not compute.

**Clause fields:** `id`, `item`, `cite` (rule id; supplies the output line's citation), `requires` (ordered rule ids, `requires[0] == cite`), `citation` (`{identifier, label}`, the paragraph the logic was read from), `basis` (`cited|inferred`), optional `guard` (rule-free applicability test), optional `when`, `value`, optional `note`. Clauses sharing an `item` are tried in file order, and the first match wins. `$comment` and `status` are excluded from the hash.

> **Corrected 2026-09-24 after final review.** Two statements above were incomplete, and both let a decision change under a clause the ledger still read as VERIFIED.
>
> 1. **Hash scope.** "The hash" of a clause, as bound by the ledger, is not `clause_hash` (the clause's own keys). A clause's answer also depends on the facts it reaches, the input specs it reads (defaults included), the clauses ahead of it in its item group (first match), and the rules file. The final review measured a fact edit, a reorder, a deletion and an input-default change each altering decisions with every clause still VERIFIED. The ledger now binds `normalize.clause_dependency_hash(doc, clause_id)`: `clause` (the `clause_assertion`), `facts` (every fact reached, transitively, with its expr), `inputs` (the spec of every input read via `input` or `present` in the clause or a reached fact), `preceded_by` (each earlier clause in the group, in file order, with its own dependency hash), and `rules_file`. `clause_hash` stays as the clause's own core and is what LC1/LN1 test. Rows LN9-LN12.
>    - **Corrected again, 2026-09-24 (residual fix R11): "each earlier clause, with its own dependency hash" was exponential.** Every clause's payload carried the full hash of every earlier clause in the group, each of which carried the full hash of every clause before *it* - O(2^n) in group size, measured at 14.6s for 20 clauses sharing one item. `preceded_by` now binds only `[id, clause_dependency_hash(doc, id)]` for the one clause immediately before it in the group, or `null` for the first. The chain still covers every earlier clause, because each predecessor's hash already binds its own predecessor - coverage unchanged, cost linear. `attest.py show_clause` derives the full list of earlier clause ids from the document (not the payload) to show the verifier, and states that each is attested on its own through the chain. Rows LC8 (60 clauses, distinct hashes, under two seconds) and LN19 (invalidating a group's first clause still invalidates its last).
> 2. **Guard and admission order.** Tasks 3-4 evaluated a clause's guard before checking admission, so an unadmitted clause whose guard came out false was skipped and a later admitted clause answered. Now every earlier clause in the group that the ledger has not admitted blocks each later clause, whatever its guard evaluates to (row LN13). The proof accumulates rules and inputs across every clause tried in the group and names them in `preceded_by` (row LC7).
>    - **Corrected again, 2026-09-24 (residual fix R12): a line could still vanish, not just answer wrongly.** If every clause in a group read its own guard or `when` as false - including an unadmitted clause's, which is not trustworthy either way - the group emitted nothing: no finding, no withheld entry, the item silently absent from the decision. `evaluate_clauses` now checks, after a group's loop ends with nothing emitted, whether any clause in it is not VERIFIED; if so it emits one withheld entry for the item, citing the first unadmitted clause's rule and naming every unadmitted clause in the group. Admitted-only groups are unaffected (parity rows LC2-LC4b unchanged). Rows LN17, LN18.
>
> The code blocks in Tasks 1-4 below are the plan as executed and are left as written; `tools/normalize.py` and `tools/engine.py` are the current statement.

---

### Task 1: Clause hashing

**Files:**
- Modify: `tools/normalize.py` (after `rule_assertion_id`, around line 99)
- Modify: `tests/run_claims.py` (new mechanism, register it in `MECHANISMS`)
- Modify: `tests/claims.json` (rows LC1, LN1)

**Interfaces:**
- Produces: `clause_assertion(clause: dict) -> dict`, `clause_hash(clause: dict) -> str`, `clause_assertion_id(source_identifier: str, clause_id: str) -> str` (returns `f"{source_identifier}#logic/{clause_id}"`)

- [ ] **Step 1: Add the failing claims rows** to the `claims` array in `tests/claims.json`:

```json
{"id": "LC1", "polarity": "positive",
 "claim": "A clause hash changes when anything that changes a decision changes: its condition, value, note, requires, citation, or basis",
 "mechanism": "clause_hash",
 "fixture": {"base": {"id": "X", "item": "i", "cite": "R", "requires": ["R"], "basis": "cited",
                      "citation": {"identifier": "/us/x/p1", "label": "p1"},
                      "value": {"op": "rule", "id": "R"}},
             "edit": {"value": {"op": "const", "value": 1}}},
 "expect": {"hash_changed": true}},
{"id": "LN1", "polarity": "negative",
 "claim": "A clause hash does NOT change when only the $comment or the legacy inline status changes; neither is part of the claim",
 "mechanism": "clause_hash",
 "fixture": {"base": {"id": "X", "item": "i", "cite": "R", "requires": ["R"], "basis": "cited",
                      "citation": {"identifier": "/us/x/p1", "label": "p1"},
                      "value": {"op": "rule", "id": "R"}},
             "edit": {"$comment": "reworded", "status": "VERIFIED"}},
 "expect": {"hash_changed": false}}
```

- [ ] **Step 2: Add the mechanism** to `tests/run_claims.py`, above `MECHANISMS`:

```python
def mech_clause_hash(fx, fixtures):
    from normalize import clause_hash  # noqa: E402
    base = fx["base"]
    return {"hash_changed": clause_hash(base) != clause_hash({**base, **fx["edit"]})}
```

Also add `"clause_hash": mech_clause_hash,` to `MECHANISMS`.

- [ ] **Step 3: Run it and confirm it fails**

Run: `python tests/run_claims.py`
Expected: LC1 and LN1 FAIL with `mechanism error` or `ImportError: cannot import name 'clause_hash'`.

- [ ] **Step 4: Implement** in `tools/normalize.py`, directly after `rule_assertion_id`:

```python
# Keys that are never part of a clause's claim. The comment is prose for the
# reader; the inline status is the same legacy claim ACTION-REGISTER 5.4 retired
# for rules. Everything else in a clause changes what the engine says.
CLAUSE_UNHASHED = ("$comment", "status")


def clause_assertion(clause: dict) -> dict:
    """The hashable core of a logic clause: every key that can change a decision."""
    return {k: v for k, v in clause.items() if k not in CLAUSE_UNHASHED}


def clause_hash(clause: dict) -> str:
    """Hash of a clause's assertion. Key order is fixed by sort_keys."""
    payload = json.dumps(
        clause_assertion(clause), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def clause_assertion_id(source_identifier: str, clause_id: str) -> str:
    """Stable id for a clause assertion: <document identifier>#logic/<CLAUSE_ID>."""
    return f"{source_identifier}#logic/{clause_id}"
```

- [ ] **Step 5: Run it and confirm it passes**

Run: `python tests/run_claims.py`
Expected: LC1 PASS, LN1 PASS, and every pre-existing row unchanged.

- [ ] **Step 6: Commit**

```bash
git add tools/normalize.py tests/run_claims.py tests/claims.json
git commit -m "Clause hashing: the logic gets a content hash, as rule values have"
```

---

### Task 2: Clauses in the ledger - status, attestation, quorum

**Files:**
- Modify: `tools/verify_status.py:48` (import), `:56` (`TARGET_QUORUM`), after `live_rule_assertions` (new functions), `main()` (use `live_assertions`, wording)
- Modify: `tools/attest.py` (imports, `load_clause`, `show_clause`, the `main()` branches, the rejection payload)
- Modify: `config/verification_policy.json`

**Interfaces:**
- Consumes: `clause_hash`, `clause_assertion_id` (Task 1)
- Produces: `live_clause_assertions(data_dir: Path = DATA) -> dict`, `live_assertions(data_dir: Path = DATA) -> dict`. Each clause row carries `kind: "clause"`, `file`, `clause_id`, `citation`, `hash`.

- [ ] **Step 1: Owner decision - clause quorum.** Proposed: `clause` quorum 1 under the existing one-verifier deviation, target 2, with the deviation's `affects` widened to `"rule, clause"`. **Reason:** it is the same constraint (one verifier exists), and inventing a second identity is worse. **Alternative:** quorum 2 now, which means every clause stays QUORUM_SHORT and the engine emits nothing until a second verifier exists. Get the owner's answer, then edit `config/verification_policy.json`:

```json
  "quorum": {
    "rule": 1,
    "provision": 1,
    "clause": 1
  },
  "target_quorum": {
    "rule": 2,
    "provision": 1,
    "clause": 2
  },
```

Also change `"affects": "rule"` to `"affects": "rule, clause"`. Leave every other field untouched.

- [ ] **Step 2: verify_status.py.** Change the import at line 48:

```python
from normalize import clause_assertion_id, clause_hash, rule_assertion_id, rule_hash  # noqa: E402
```

Change line 56:

```python
TARGET_QUORUM = {"rule": 2, "provision": 1, "clause": 2}
```

Add directly after `live_rule_assertions`:

```python
def live_clause_assertions(data_dir: Path = DATA) -> dict:
    """Every logic clause currently in the corpus, keyed by assertion id. A clause
    is attested exactly as a rule value is: read against its cited paragraph."""
    live = {}
    for path in sorted(data_dir.glob("*.logic.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        rules_doc = json.loads((path.parent / doc["rules_file"]).read_text(encoding="utf-8"))
        source = rules_doc.get("source", {})
        identifier = source.get("identifier", path.stem)
        for clause in doc.get("clauses", []):
            aid = clause_assertion_id(identifier, clause["id"])
            live[aid] = {
                "assertion": aid,
                "kind": "clause",
                "file": path.name,
                "clause_id": clause["id"],
                "source_label": source.get("label"),
                "source_url": source.get("url"),
                "source_artifact": (source.get("artifact") or {}).get("sha256"),
                "citation": (clause.get("citation") or {}).get("label"),
                "hash": clause_hash(clause),
                "inline_status": clause.get("status"),
            }
    return live


def live_assertions(data_dir: Path = DATA) -> dict:
    """Rule values and logic clauses together - everything the ledger can admit."""
    return {**live_rule_assertions(data_dir), **live_clause_assertions(data_dir)}
```

In `main()`, replace `live = live_rule_assertions(Path(args.data))` with `live = live_assertions(Path(args.data))`. Replace the text `rule assertions` in the summary print with `rule and clause assertions`. Leave `reconcile.py`, `render_pages.py` and `render_verification.py` on `live_rule_assertions`: they are about values. A clause queue on the verification page is out of M1 scope.

- [ ] **Step 3: attest.py.** Import `live_assertions` in place of `live_rule_assertions`, and add `clause_hash` to the normalize import. Add these after `load_rule`:

```python
def load_clause(file_name: str, clause_id: str, data_dir: Path):
    doc = json.loads((data_dir / file_name).read_text(encoding="utf-8"))
    for clause in doc.get("clauses", []):
        if clause["id"] == clause_id:
            return doc, clause
    raise SystemExit(f"clause {clause_id} not found in {file_name}")


def show_clause(row: dict, clause: dict) -> None:
    citation = clause.get("citation") or {}
    print("=" * 72)
    print(f"ASSERTION   {row['assertion']}")
    print(f"STATUS      {row['status']}  ({row.get('detail','')})")
    print("-" * 72)
    print(f"LOGIC       line '{clause.get('item')}', basis {clause.get('basis')}")
    print(f"READ FROM   {citation.get('label')}")
    print(f"            {citation.get('identifier')}")
    print(f"SOURCE      {row.get('source_label')}")
    if row.get("source_url"):
        print(f"OPEN        {row['source_url']}")
    print("-" * 72)
    shown = {k: v for k, v in clause.items() if k not in ("$comment", "status")}
    print(json.dumps(shown, indent=2, ensure_ascii=False))
    if clause.get("$comment"):
        print("-" * 72)
        print("COMMENT (not hashed, not part of the claim):")
        print(f"  {clause['$comment']}")
    print("-" * 72)
    print("Open the issuing authority's copy. Confirm the cited paragraph states")
    print("this condition and this result. If basis is 'inferred', confirm the")
    print("derivation is the only reading the paragraph supports. Do not confirm")
    print("from the comment, from another tier, or from memory.")
    print("=" * 72)
```

In `main()`, replace `live = live_rule_assertions(data_dir)` with `live = live_assertions(data_dir)`, and replace the `--list` header text `rule assertions` with `assertions`. Replace:

```python
    doc, rule = load_rule(target["file"], target["rule_id"], data_dir)
    show(target, rule)
```

with:

```python
    if target["kind"] == "clause":
        doc, item = load_clause(target["file"], target["clause_id"], data_dir)
        show_clause(target, item)
        content_hash = clause_hash(item)
    else:
        doc, item = load_rule(target["file"], target["rule_id"], data_dir)
        show(target, item)
        content_hash = rule_hash(item)
```

In the edition fallback, replace `or doc.get("source", {}).get("label")` with `or target.get("source_label")`, because a logic file carries no `source`. In the ledger record, replace `"kind": "rule",` with `"kind": target["kind"],` and `"content_hash": rule_hash(rule),` with `"content_hash": content_hash,`. In the REJECTED payload, replace `"encoded": {"value": rule.get("value"), "unit": rule.get("unit")},` with:

```python
            "encoded": ({"clause_id": target["clause_id"]} if target["kind"] == "clause"
                        else {"value": item.get("value"), "unit": item.get("unit")}),
```

- [ ] **Step 4: Verify that nothing regressed** (there are no logic files yet, so clause output is empty)

Run: `python tools/verify_status.py`
Expected: the same counts as before this task, and the header now reads `rule and clause assertions`.

Run: `python tools/attest.py --list`
Expected: the same pending list as before.

Run: `python tests/run_claims.py`
Expected: every row PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/verify_status.py tools/attest.py config/verification_policy.json
git commit -m "Clauses are ledger assertions: kind clause, quorum recorded, attest.py reads them"
```

---

### Task 3: The engine and the parental-leave clauses, proved by parity

**Files:**
- Create: `tools/engine.py`
- Create: `data/maradmin-051-23.logic.json`
- Modify: `tests/run_claims.py` (helpers and mechanism `engine_parity`)
- Modify: `tests/claims.json` (fixture `parity_cases`, rows LC2, LC3, LC4)

**Interfaces:**
- Consumes: `clause_hash`, `clause_assertion_id`, `rule_hash`, `rule_assertion_id` (normalize); `LEDGER`, `POLICY`, `VERIFIED`, `derive`, `load_ledger`, `load_policy` (verify_status)
- Produces: `engine.run(logic_path, inputs: dict, *, ledger_path=LEDGER, policy_path=POLICY, today=None) -> dict`. The result has the same keys as `evaluate.evaluate()`, plus `proof` (a list) and `verification.by_clause` (a dict). Also `engine.OPS: set[str]` and `engine.EngineError`.

- [ ] **Step 1: Add the fixture and the failing parity rows.** Add under `fixtures` in `tests/claims.json`. `as_of` is fixed in every case, because the default is today and that is not reproducible.

```json
"parity_cases": [
  {"event_date": "2027-03-01", "as_of": "2027-06-01", "used_days": 0},
  {"event_date": "2027-03-01", "as_of": "2027-06-01", "used_days": 70, "increments_used": 2, "proposed_increment": 5},
  {"event_date": "2027-03-01", "second_event_date": "2027-03-02", "as_of": "2027-06-01", "used_days": 0},
  {"event_date": "2027-03-01", "second_event_date": "2027-03-04", "as_of": "2027-06-01"},
  {"event_date": "2027-03-01", "second_event_date": "2027-03-10", "as_of": "2027-06-01"},
  {"event_date": "2027-03-10", "second_event_date": "2027-03-01", "as_of": "2027-06-01"},
  {"event_date": "2027-03-01", "as_of": "2028-06-01"},
  {"event_date": "2027-03-01", "as_of": "2028-02-29"},
  {"event_date": "2027-03-01", "as_of": "2027-06-01", "used_days": 90},
  {"event_date": "2027-03-01", "as_of": "2027-06-01", "increments_used": 12, "proposed_increment": 10},
  {"event_date": "2027-03-01", "as_of": "2027-06-01", "increments_used": 3, "proposed_increment": 10}
]
```

Coverage of the cases: the three published scenarios; the merge boundary (exactly 72h); separate events; events given in reverse order; an expired window; the window's last day in a leap year; days used beyond the maximum; the increment maximum reached; a valid increment.

Rows:

```json
{"id": "LC2", "polarity": "positive",
 "claim": "With every rule and clause admitted, the engine reproduces the hand-written evaluator byte for byte on every parity case",
 "mechanism": "engine_parity",
 "fixture": {"cases": "parity_cases", "attest_rules": "all", "attest_clauses": "all"},
 "expect": {"mismatches": []}},
{"id": "LC3", "polarity": "positive",
 "claim": "With no rule admitted and every clause admitted, the engine withholds exactly what the hand-written evaluator withholds, naming the same rules in the same order",
 "mechanism": "engine_parity",
 "fixture": {"cases": "parity_cases", "attest_rules": [], "attest_clauses": "all"},
 "expect": {"mismatches": []}},
{"id": "LC4", "polarity": "positive",
 "claim": "With only the maximum admitted, the engine and the evaluator agree line for line (the C10 condition, applied to the engine)",
 "mechanism": "engine_parity",
 "fixture": {"cases": "parity_cases", "attest_rules": ["MAX_PARENTAL_LEAVE_DAYS"], "attest_clauses": "all"},
 "expect": {"mismatches": []}}
```

- [ ] **Step 2: Add the helpers and the mechanism** to `tests/run_claims.py`. Add `import shutil` to the imports.

```python
DATA_DIR = ROOT / "data"
MPLP_RULES = DATA_DIR / "maradmin-051-23.rules.json"
MPLP_LOGIC = DATA_DIR / "maradmin-051-23.logic.json"


def _fixture_ledger(tmp, rules_doc, logic_doc, attest_rules, attest_clauses):
    """A two-verifier ledger admitting the named rules and clauses, quorum 2.
    'all' admits everything. Hashes are taken from the documents passed in, so a
    document mutated afterwards reads as INVALIDATED - which is the point."""
    from normalize import clause_assertion_id, clause_hash, rule_assertion_id, rule_hash  # noqa: E402
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
            lines += [rec(clause_assertion_id(ident, c["id"]), "clause", clause_hash(c), v)
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
    The engine's two additions (proof, verification.by_clause) are removed first;
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
            if json.dumps(want, sort_keys=True, default=str) != \
                    json.dumps(got, sort_keys=True, default=str):
                mismatches.append(args)
    return {"mismatches": mismatches}
```

Register `"engine_parity": mech_engine_parity,` in `MECHANISMS`.

- [ ] **Step 3: Run and confirm it fails**

Run: `python tests/run_claims.py`
Expected: LC2, LC3 and LC4 FAIL with `mechanism error` (`No module named 'engine'`).

- [ ] **Step 4: Create `data/maradmin-051-23.logic.json`.** The `basis` values are the encoder's reading, and the verifier confirms or rejects each one in Task 7. Treat them as an Assumption until then.

```json
{
  "$comment": "Decision logic for MARADMIN 051/23 as data. Each clause is read from the paragraph its citation names and is admitted by the attestation ledger exactly as a rule value is. basis 'cited' means the paragraph states the condition and result; 'inferred' means the clause derives them (arithmetic, a date computed from a stated period). Transcribed from the hand-written logic in tools/evaluate.py, which it must reproduce byte for byte before it replaces it (EVALUATOR-PLAN.md, M1). Evaluated by tools/engine.py; gated by tools/check_logic.py.",
  "schema_version": "1.0",
  "rules_file": "maradmin-051-23.rules.json",
  "inputs": [
    {"name": "event_date", "type": "date", "required": true},
    {"name": "as_of", "type": "date", "default_today": true},
    {"name": "second_event_date", "type": "date"},
    {"name": "used_days", "type": "int", "default": 0},
    {"name": "increments_used", "type": "int", "default": 0},
    {"name": "proposed_increment", "type": "int"}
  ],
  "facts": [
    {"name": "gap_hours",
     "expr": {"op": "mul", "args": [
       {"op": "abs", "args": [{"op": "days_between", "args": [
         {"op": "input", "name": "event_date"}, {"op": "input", "name": "second_event_date"}]}]},
       {"op": "const", "value": 24}]}},
    {"name": "governing_event",
     "expr": {"op": "if",
       "cond": {"op": "and", "args": [
         {"op": "present", "name": "second_event_date"},
         {"op": "gt", "args": [{"op": "fact", "name": "gap_hours"},
                               {"op": "rule", "id": "EVENT_PROXIMITY_MERGE_HOURS"}]}]},
       "then": {"op": "max", "args": [{"op": "input", "name": "event_date"},
                                      {"op": "input", "name": "second_event_date"}]},
       "else": {"op": "input", "name": "event_date"}}},
    {"name": "forfeiture_date",
     "expr": {"op": "add_days", "args": [{"op": "fact", "name": "governing_event"},
                                         {"op": "rule", "id": "ENTITLEMENT_WINDOW_DAYS"}]}}
  ],
  "clauses": [
    {"id": "MULTIPLE_EVENTS_SINGLE", "item": "multiple_events", "basis": "cited",
     "cite": "EVENT_PROXIMITY_MERGE_HOURS", "requires": ["EVENT_PROXIMITY_MERGE_HOURS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/b/1", "label": "MARADMIN 051/23, para 8.b.(1)"},
     "guard": {"op": "present", "name": "second_event_date"},
     "when": {"op": "le", "args": [{"op": "fact", "name": "gap_hours"},
                                   {"op": "rule", "id": "EVENT_PROXIMITY_MERGE_HOURS"}]},
     "value": {"op": "const", "value": "single event - within the merge period"},
     "note": {"op": "format", "template": "gap {gap}h <= {merge}h",
              "args": {"gap": {"op": "fact", "name": "gap_hours"},
                       "merge": {"op": "rule", "id": "EVENT_PROXIMITY_MERGE_HOURS"}}}},
    {"id": "MULTIPLE_EVENTS_SEPARATE", "item": "multiple_events", "basis": "cited",
     "cite": "EVENT_PROXIMITY_MERGE_HOURS", "requires": ["EVENT_PROXIMITY_MERGE_HOURS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/b/2/a", "label": "MARADMIN 051/23, para 8.b.(2)(a)"},
     "guard": {"op": "present", "name": "second_event_date"},
     "value": {"op": "const", "value": "separate events - new entitlement runs concurrently with unexpired prior leave"},
     "note": {"op": "format", "template": "gap {gap}h > {merge}h; concurrency per MARADMIN 051/23 para 8.b.(2)(a)",
              "args": {"gap": {"op": "fact", "name": "gap_hours"},
                       "merge": {"op": "rule", "id": "EVENT_PROXIMITY_MERGE_HOURS"}}}},
    {"id": "AUTHORIZED_TOTAL", "item": "authorized_total_days", "basis": "cited",
     "cite": "MAX_PARENTAL_LEAVE_DAYS", "requires": ["MAX_PARENTAL_LEAVE_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p11/d", "label": "MARADMIN 051/23, para 11.d"},
     "value": {"op": "rule", "id": "MAX_PARENTAL_LEAVE_DAYS"}},
    {"id": "REMAINING_DAYS", "item": "remaining_days", "basis": "inferred",
     "$comment": "Para 11.d states the total. Subtracting days used, floored at zero, is the engine's arithmetic, not the source's sentence.",
     "cite": "MAX_PARENTAL_LEAVE_DAYS", "requires": ["MAX_PARENTAL_LEAVE_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p11/d", "label": "MARADMIN 051/23, para 11.d"},
     "value": {"op": "max", "args": [{"op": "const", "value": 0},
               {"op": "sub", "args": [{"op": "rule", "id": "MAX_PARENTAL_LEAVE_DAYS"},
                                      {"op": "input", "name": "used_days"}]}]},
     "note": {"op": "format", "template": "{max} authorized minus {used} used",
              "args": {"max": {"op": "rule", "id": "MAX_PARENTAL_LEAVE_DAYS"},
                       "used": {"op": "input", "name": "used_days"}}}},
    {"id": "FORFEITURE_DATE", "item": "forfeiture_date", "basis": "inferred",
     "$comment": "The source states a period; the clause computes a date as 365 days from the governing event. The one-year versus 365-day question is an open finding (verification/findings-forfeiture-window.md) and this clause inherits it.",
     "cite": "ENTITLEMENT_WINDOW_DAYS", "requires": ["ENTITLEMENT_WINDOW_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/c/3", "label": "MARADMIN 051/23, para 8.c.(3)"},
     "value": {"op": "iso", "args": [{"op": "fact", "name": "forfeiture_date"}]},
     "note": {"op": "const", "value": "unused leave forfeits after this date unless para 8.a.(3) applies - commander determination, not computed here"}},
    {"id": "WINDOW_EXPIRED", "item": "window_status", "basis": "inferred",
     "cite": "ENTITLEMENT_WINDOW_DAYS", "requires": ["ENTITLEMENT_WINDOW_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/c/3", "label": "MARADMIN 051/23, para 8.c.(3)"},
     "when": {"op": "gt", "args": [{"op": "input", "name": "as_of"}, {"op": "fact", "name": "forfeiture_date"}]},
     "value": {"op": "const", "value": "EXPIRED as of evaluation date"},
     "note": {"op": "format", "template": "as-of {as_of} is past {forfeit}",
              "args": {"as_of": {"op": "iso", "args": [{"op": "input", "name": "as_of"}]},
                       "forfeit": {"op": "iso", "args": [{"op": "fact", "name": "forfeiture_date"}]}}}},
    {"id": "WINDOW_OPEN", "item": "window_status", "basis": "inferred",
     "cite": "ENTITLEMENT_WINDOW_DAYS", "requires": ["ENTITLEMENT_WINDOW_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/c/3", "label": "MARADMIN 051/23, para 8.c.(3)"},
     "value": {"op": "format", "template": "{days} days remain in the entitlement window",
               "args": {"days": {"op": "days_between", "args": [{"op": "input", "name": "as_of"},
                                                                 {"op": "fact", "name": "forfeiture_date"}]}}}},
    {"id": "INCREMENT_UNDER_MIN", "item": "proposed_increment", "basis": "cited",
     "cite": "MIN_INCREMENT_DAYS", "requires": ["MIN_INCREMENT_DAYS", "MAX_INCREMENTS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/a/1/b", "label": "MARADMIN 051/23, para 8.a.(1)(b)"},
     "guard": {"op": "present", "name": "proposed_increment"},
     "when": {"op": "lt", "args": [{"op": "input", "name": "proposed_increment"}, {"op": "rule", "id": "MIN_INCREMENT_DAYS"}]},
     "value": {"op": "format", "template": "INVALID - {proposed} days is under the {minimum}-day minimum",
               "args": {"proposed": {"op": "input", "name": "proposed_increment"},
                        "minimum": {"op": "rule", "id": "MIN_INCREMENT_DAYS"}}}},
    {"id": "INCREMENT_MAX_REACHED", "item": "proposed_increment", "basis": "cited",
     "cite": "MAX_INCREMENTS", "requires": ["MAX_INCREMENTS", "MIN_INCREMENT_DAYS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/a/1/b", "label": "MARADMIN 051/23, para 8.a.(1)(b)"},
     "guard": {"op": "present", "name": "proposed_increment"},
     "when": {"op": "ge", "args": [{"op": "input", "name": "increments_used"}, {"op": "rule", "id": "MAX_INCREMENTS"}]},
     "value": {"op": "format", "template": "INVALID - {maximum}-increment maximum already reached",
               "args": {"maximum": {"op": "rule", "id": "MAX_INCREMENTS"}}}},
    {"id": "INCREMENT_VALID", "item": "proposed_increment", "basis": "inferred",
     "$comment": "Valid is the absence of both stated invalidity conditions. The paragraph states the limits, not this conclusion.",
     "cite": "MIN_INCREMENT_DAYS", "requires": ["MIN_INCREMENT_DAYS", "MAX_INCREMENTS"],
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/a/1/b", "label": "MARADMIN 051/23, para 8.a.(1)(b)"},
     "guard": {"op": "present", "name": "proposed_increment"},
     "value": {"op": "format", "template": "valid - increment {n} of at most {maximum}",
               "args": {"n": {"op": "add", "args": [{"op": "input", "name": "increments_used"}, {"op": "const", "value": 1}]},
                        "maximum": {"op": "rule", "id": "MAX_INCREMENTS"}}}}
  ],
  "refusals": [
    {"id": "CONVALESCENT",
     "text": "Convalescent leave - requires a health care provider recommendation and commander approval (para 7.a.(1)(a)); not computable from encoded rules.",
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p7/a/1/a", "label": "MARADMIN 051/23, para 7.a.(1)(a)"}},
    {"id": "WINDOW_EXTENSION",
     "text": "Window extension under para 8.a.(3) - a commander determination against six qualifying conditions; the engine reports the unextended date only.",
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/a/3", "label": "MARADMIN 051/23, para 8.a.(3)"}},
    {"id": "RC_FORFEITURE",
     "text": "Reserve Component forfeiture particulars (para 8.c.(4)) - not yet encoded in rules.json.",
     "citation": {"identifier": "/us/dod/don/usmc/maradmin/2023/051/p8/c/4", "label": "MARADMIN 051/23, para 8.c.(4)"}}
  ]
}
```

- [ ] **Step 5: Create `tools/engine.py`**

```python
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
from normalize import clause_assertion_id, clause_hash, rule_assertion_id, rule_hash  # noqa: E402
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
        for c in clauses:
            cx.rules_touched, cx.inputs_touched = [], []
            if "guard" in c and not ev(c["guard"], cx):
                continue
            blockers = [blocker(r, rules) for r in c["requires"]
                        if rules[r]["verification"] != VERIFIED]
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
                              "inputs": sorted(set(cx.inputs_touched))})
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
                    "hash": clause_hash(c)} for c in doc["clauses"]}
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
```

- [ ] **Step 6: Run and confirm it passes**

Run: `python tests/run_claims.py`
Expected: LC2, LC3 and LC4 PASS with `mismatches: []`. If a case mismatches, diff the two JSON strings for that case and fix the **clause file** first, since the transcription is the likelier fault. Change `engine.py` only when the evaluation semantics in the reference table above are wrong, and then correct the table too.

- [ ] **Step 7: Smoke-test the CLI**

Run: `python tools/engine.py --input event_date=2027-03-01 --input as_of=2027-06-01`
Expected: every line WITHHELD, and each one names `logic/<ID> [UNVERIFIED]`, because no real clause is attested. That is correct behaviour, not a failure.

- [ ] **Step 8: Commit**

```bash
git add tools/engine.py data/maradmin-051-23.logic.json tests/run_claims.py tests/claims.json
git commit -m "Clause engine: parental-leave logic as data, parity with evaluate.py proved on 11 cases"
```

---

### Task 4: Withholding and proof claims on the engine

**Files:**
- Modify: `tests/run_claims.py` (mechanism `engine`)
- Modify: `tests/claims.json` (rows LC5, LN2, LN3)

**Interfaces:**
- Consumes: `engine.run`, `_fixture_ledger`, `MPLP_RULES`, `MPLP_LOGIC` (Task 3), and `apply_mutation` (defined here; Task 5 reuses it)

- [ ] **Step 1: Add the rows**

```json
{"id": "LC5", "polarity": "positive",
 "claim": "Every emitted line has a proof entry naming its clause, its basis, and a paragraph identifier",
 "mechanism": "engine",
 "fixture": {"args": {"event_date": "2027-03-01", "as_of": "2027-06-01", "proposed_increment": 10, "increments_used": 3},
             "attest_rules": "all", "attest_clauses": "all"},
 "expect": {"proof_matches_decision": true, "every_proof_cited": true, "logic_blockers": []}},
{"id": "LN2", "polarity": "negative",
 "claim": "A VERIFIED rule does not make an unattested clause usable: with every rule admitted and REMAINING_DAYS unattested, that line is withheld and names the clause",
 "mechanism": "engine",
 "fixture": {"args": {"event_date": "2027-03-01", "as_of": "2027-06-01"},
             "attest_rules": "all", "attest_clauses_except": ["REMAINING_DAYS"]},
 "expect": {"logic_blockers": ["logic/REMAINING_DAYS"], "decision_has_remaining_days": false}},
{"id": "LN3", "polarity": "negative",
 "claim": "A clause edited after attestation is not used: its hash no longer matches, the ledger reads INVALIDATED, and the line is withheld",
 "mechanism": "engine",
 "fixture": {"args": {"event_date": "2027-03-01", "as_of": "2027-06-01"},
             "attest_rules": "all", "attest_clauses": "all",
             "mutations": [{"path": ["clauses", "clause:REMAINING_DAYS", "note", "template"], "value": "{max} minus {used}"}]},
 "expect": {"logic_blockers": ["logic/REMAINING_DAYS"], "decision_has_remaining_days": false}}
```

- [ ] **Step 2: Add the mechanism**

```python
def _step(target, key):
    """Path step. 'clause:ID' selects a clause by id, so a fixture does not
    depend on clause order."""
    if isinstance(key, str) and key.startswith("clause:"):
        return next(c for c in target if c["id"] == key[len("clause:"):])
    return target[key]


def apply_mutation(doc, m):
    target = doc
    for key in m["path"][:-1]:
        target = _step(target, key)
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
    return {
        "proof_matches_decision": [p["item"] for p in out["proof"]] == [l["item"] for l in out["decision"]],
        "every_proof_cited": all(str(p["clause_citation"].get("identifier", "")).startswith("/us/")
                                 and p["basis"] in ("cited", "inferred") for p in out["proof"]),
        "logic_blockers": sorted(b.split(" [")[0] for b in blockers if b.startswith("logic/")),
        "decision_has_remaining_days": any(l["item"] == "remaining_days" for l in out["decision"]),
    }
```

Register `"engine": mech_engine,` in `MECHANISMS`.

- [ ] **Step 3: Run**

Run: `python tests/run_claims.py`
Expected: LC5, LN2 and LN3 PASS. If LN3 fails with the line still emitted, the engine is not deriving clause status from the ledger hash. Check `run()` and do not weaken the row.

- [ ] **Step 4: Commit**

```bash
git add tests/run_claims.py tests/claims.json
git commit -m "Claims: unattested or edited clauses withhold; every line carries its proof"
```

---

### Task 5: check_logic.py, the build gate

**Files:**
- Create: `tools/check_logic.py`
- Modify: `tests/run_claims.py` (mechanism `check_logic`)
- Modify: `tests/claims.json` (rows LC6, LN4-LN8)
- Modify: `build.sh` (after stage 16)

**Interfaces:**
- Consumes: `engine.OPS`, `apply_mutation` (Task 4)
- Produces: `check_file(path: Path, idents: set[str]) -> list[str]`. CLI exit code 0 means clean and 1 means any error.

- [ ] **Step 1: Add the rows.** Each negative row breaks exactly one thing in a copy of the live file.

```json
{"id": "LC6", "polarity": "positive", "claim": "The live clause file passes every static check",
 "mechanism": "check_logic", "fixture": {"mutations": [], "stderr_has": ""},
 "expect": {"exit_nonzero": false, "stderr_has": ""}},
{"id": "LN4", "polarity": "negative", "claim": "A cycle in the fact graph is rejected; the engine could not be proven to terminate",
 "mechanism": "check_logic",
 "fixture": {"mutations": [{"path": ["facts"], "value": [
   {"name": "loop_a", "expr": {"op": "fact", "name": "loop_b"}},
   {"name": "loop_b", "expr": {"op": "fact", "name": "loop_a"}}]}], "stderr_has": "fact cycle"},
 "expect": {"exit_nonzero": true, "stderr_has": "fact cycle"}},
{"id": "LN5", "polarity": "negative", "claim": "A clause citation containing a period is rejected under NAMESPACES.md N3",
 "mechanism": "check_logic",
 "fixture": {"mutations": [{"path": ["clauses", "clause:REMAINING_DAYS", "citation", "identifier"], "value": "/us/dod/dodi/1327.06/s3/3.11"}], "stderr_has": "N3/N4"},
 "expect": {"exit_nonzero": true, "stderr_has": "N3/N4"}},
{"id": "LN6", "polarity": "negative", "claim": "A clause citing a paragraph that exists in no USLM file is rejected; no logic without the paragraph it was read from",
 "mechanism": "check_logic",
 "fixture": {"mutations": [{"path": ["clauses", "clause:REMAINING_DAYS", "citation", "identifier"], "value": "/us/dod/don/usmc/maradmin/2023/051/p99"}], "stderr_has": "not a paragraph"},
 "expect": {"exit_nonzero": true, "stderr_has": "not a paragraph"}},
{"id": "LN7", "polarity": "negative", "claim": "A clause reading a rule it does not declare in requires is rejected; its withholding would be incomplete",
 "mechanism": "check_logic",
 "fixture": {"mutations": [{"path": ["clauses", "clause:AUTHORIZED_TOTAL", "value"], "value": {"op": "rule", "id": "MIN_INCREMENT_DAYS"}}], "stderr_has": "not in requires"},
 "expect": {"exit_nonzero": true, "stderr_has": "not in requires"}},
{"id": "LN8", "polarity": "negative", "claim": "A guard that reads a rule is rejected; applicability is decided from inputs only",
 "mechanism": "check_logic",
 "fixture": {"mutations": [{"path": ["clauses", "clause:MULTIPLE_EVENTS_SINGLE", "guard"], "value": {"op": "gt", "args": [{"op": "rule", "id": "EVENT_PROXIMITY_MERGE_HOURS"}, {"op": "const", "value": 0}]}}], "stderr_has": "guard reads a rule"},
 "expect": {"exit_nonzero": true, "stderr_has": "guard reads a rule"}}
```

- [ ] **Step 2: Add the mechanism**

```python
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
```

Register `"check_logic": mech_check_logic,`. Run `python tests/run_claims.py` and expect LC6 and LN4-LN8 to FAIL (`check_logic.py` does not exist).

- [ ] **Step 3: Create `tools/check_logic.py`**

```python
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
```

- [ ] **Step 4: Run**

Run: `python tools/check_logic.py`
Expected: `10 clause(s) in 1 logic file(s): OK`, exit 0. If a MARADMIN citation reports `not a paragraph`, the identifier in the logic file is wrong. Fix the file, and do not relax the check.

Run: `python tests/run_claims.py`
Expected: LC6 and LN4-LN8 PASS. All other rows still PASS.

- [ ] **Step 5: Add the build stage.** In `build.sh`, directly after the stage 16 block:

```bash
echo "### 16a logic clauses - termination and citation checks"
python3 tools/check_logic.py
```

`set -euo pipefail` is already in force, so a failure stops the build.

- [ ] **Step 6: Commit**

```bash
git add tools/check_logic.py tests/run_claims.py tests/claims.json build.sh
git commit -m "check_logic.py: acyclic facts, declared dependencies, cited paragraphs; build stage 16a"
```

---

### Task 6: Idempotence, proved by hashing

**Files:** none changed. This task is measurement only.

`canonical/` is not tracked, so a git worktree does not have it. Run this task, and Task 8's build, in the main checkout at `D:\Coding\policy-as-data` after merging, or in a worktree where `canonical/` has been made available. `./build.sh` fails at stage 1 without it.

- [ ] **Step 1: Hash every build output across two runs**

```bash
./build.sh > /dev/null && find canonical docs data/exports config -type f | sort | xargs sha256sum > /tmp/run1.txt
./build.sh > /dev/null && find canonical docs data/exports config -type f | sort | xargs sha256sum > /tmp/run2.txt
cmp /tmp/run1.txt /tmp/run2.txt && echo IDENTICAL
```

Expected: `IDENTICAL`. Stage 16a writes nothing, so any difference comes from outside this plan. Record it in the `SESSION_HANDOFF.md` defect register rather than absorbing it.

- [ ] **Step 2: Run the full claims table**

Run: `python tests/run_claims.py`
Expected: exit 0, every row PASS. Record the row count.

---

### Task 7: Owner attests the clauses (HUMAN - the gate)

No code in this task, and no agent may perform it. An agent may prepare the list.

- [ ] **Step 1:** `python tools/attest.py --list` shows the ten `#logic/` assertions as UNVERIFIED.
> **Corrected 2026-09-24 after final review.** Each attestation binds `clause_dependency_hash`, not `clause_hash`; `attest.py` shows the facts, input specs and earlier clauses it covers, and the owner is attesting all of it. Any attestation recorded against the old clause-only hash reads INVALIDATED (none existed when this was corrected).

- [ ] **Step 2:** For each clause, the owner opens MARADMIN 051/23 at the cited paragraph and runs `python tools/attest.py --assertion '/us/dod/don/usmc/maradmin/2023/051#logic/<ID>' --verifier <V-id>`. For `basis: inferred` clauses, the question is whether the derivation is the only reading the paragraph supports. If it is not, REJECT; the correction request records why.
- [ ] **Step 3:** `python tools/verify_status.py` shows the clauses VERIFIED, or shows the rejections. Rejected clauses go through `tools/corrections.py`, and Task 8 waits for them.

---

### Task 8: Cutover - the scenarios page renders from the engine (gated on Task 7)

**Files:**
- Modify: `tools/render_scenarios.py:28` (import), `:104-115` (`main`), `scenario_html` (proof column)

**Interfaces:**
- Consumes: `engine.run`, `engine.LOGIC_DEFAULT`

- [ ] **Step 1: Swap the call.** Replace `from evaluate import RULES_DEFAULT, evaluate, load_rules` with `from engine import LOGIC_DEFAULT, run`. In `main()`, delete the `load_rules` line, and replace `result = evaluate(rules, source, deviation, **sc["args"])` with `result = run(LOGIC_DEFAULT, sc["args"])`.

- [ ] **Step 2: Show the proof.** In `scenario_html`, build `proof = {p["item"]: p for p in result["proof"]}` at the top. In each decision row, append this to the "Rests on" cell:

```python
        p = proof[line["item"]]
        logic = (f'<br><span class="cite">logic {E(p["basis"])} from '
                 f'{cite_link(p["clause_citation"]["identifier"], p["clause_citation"]["label"], pages)}</span>')
```

Then render `{cite_link(...)}{logic}` in that `<td>`.

- [ ] **Step 3: Verify the page claim.** This changes what a rendered page states (CLAUDE.md section 14). Run `./build.sh`, open `docs/scenarios.html`, and confirm each line shows its logic citation. Run `python tools/check_site.py` and expect it clean. Repeat Task 6 step 1 and expect `IDENTICAL`.

- [ ] **Step 4: Commit**

```bash
git add tools/render_scenarios.py
git commit -m "Scenarios page renders from the clause engine and shows each line's logic citation"
```

---

### Task 9: Record it

**Files:** `SESSION_HANDOFF.md`, `BUILD.md`

- [ ] **Step 1:** Add to `SESSION_HANDOFF.md` section 7 or the decisions area, in the format from `CLAUDE.md` section 7:
  - **Decision:** decision logic is hand-tier data, attested per clause.
  - **Reason:** unverified Python logic was the weak link under verified values.
  - **Alternatives:** SUMO+Vampire, LegalRuleML+SHACL, Datalog.
  - **Tradeoffs:** no recursion; a small custom expression language.
  - **Risk:** a transcription error in a clause is proved precisely; human attestation is the only guard.
  - **Revisit trigger:** the first recursive requirement, or M3.
- [ ] **Step 2:** Add stage 16a to the stage table in `BUILD.md`, with the measured clause count and the claims row count from Task 6.
- [ ] **Step 3:** Commit: `git commit -am "Record the clause engine decision and build stage 16a"`

---

## M2 - Leave accrual (MCO 1050.3J). Outline; gets its own detailed plan after M1 lands

M2 is deliberately not written to step level yet. Three blocking unknowns decide its shape, and writing code before they are answered would mean guessing at a source (CLAUDE.md section 3).

### Confirmed from the store (read 2026-09-24, `canonical/MCO-1050.3J.json`)

- Encl (1) ch 2 para 2.a: "Leave is accrued at the rate of 2.5 days for each month of active military service. Except as provided in paragraph 9 or when a member is in a missing status, leave accumulated in excess of 60 days shall be lost at the end of the fiscal year..."
- Para 9.a: Special Leave Accrual (SLA). "Marines are authorized to accrue up to 120 days earned leave" under qualifying duty. Qualification is a commander determination.
- Para 2.c: a temporary 75-day cap, 1 Oct 2008 to 31 Dec 2010. It is expired.
- The machine tier holds provision identifiers such as `/us/dod/don/usmc/mco/1050_3j/p-2-2/p2/a`. `REFERENCES.md` still lists Encl (1) as "not yet encoded" in the hand tier.

### Blocking before M2 starts

1. **B-M2-1, identifier mapping (Unknown).** Is `.../1050_3j/p-2-2/p2/a` chapter 2 para 2.a, or page 2-2 para 2? The segment looks like a page anchor. Read the export text at that identifier and confirm. If it is a page anchor, clause citations would pin to a page and not a paragraph. That is a parser defect to log in the register, not something to work around.
2. **B-M2-2, the interaction (Unknown).** M2 is meant to prove two orders interacting. The candidate interaction is that parental leave is non-chargeable, so it does not reduce the accrued balance. **Find the paragraph that states it**, in MARADMIN 051/23 or DoWI 1327.06. If no paragraph states it, the interaction is a GAP and is refused by name (constraint 5). M2 would then prove a single domain only, and the row 28 trigger for the SUMO evaluation would not yet be met. Say so; do not manufacture the interaction.
3. **B-M2-3, identifier grammar (Open decision #2).** The hand tier still uses periods (`/us/dod/don/usmc/mco/1050.3J`, `/us/dod/dodi/1327.06/...`). `check_logic.py` rejects periods in citations. Recommendation: new M2 files follow N3 (`1050_3j`), because a hard constraint outranks consistency with a known open defect. Any clause citing DoWI 1327.06 is blocked until open decision #2 is resolved for that file.

### M2 shape, once unblocked

| Task | Content |
|---|---|
| M2-1 rules | `data/mco-1050-3J.rules.json`: `ACCRUAL_DAYS_PER_MONTH` 2.5, `FY_CARRYOVER_MAX_DAYS` 60, `SLA_MAX_DAYS` 120. Concepts go in `config/rule_concepts.json` by owner assignment, and units in `config/units.json` (`days_per_month` is new). Stage 16 `reconcile.py` then compares the carryover against DoWI 1327.06 if that tier states it, which is the value-level cross-tier check. |
| M2-2 engine | `bind_inputs` gains `number` and `bool` types. Nothing else changes, which is the test of genericity. |
| M2-3 clauses | `data/mco-1050-3J.logic.json`: `ACCRUED_THIS_FY` (cited 2.a), `PROJECTED_FY_END_BALANCE` (inferred), `LOST_AT_FY_END` (cited 2.a; guard: not in missing status), `SELL_BACK` refused. Refusals by name: SLA qualification (para 9, commander determination), missing status, excess leave (para 7), the para 2.c temporary cap (expired, and out of range for any date after 2010). |
| M2-4 interaction | Only if B-M2-2 finds a paragraph: a clause that consumes MARADMIN's parental-leave days as an input and cites the non-chargeable paragraph. `check_logic.py` gains a cross-file check: two cited clauses from different documents that produce the same `concept` must agree on the shared parity cases, or the build reports DIVERGE, as reconcile does for values. |
| M2-5 claims | Parity is not available, since no hand-written accrual evaluator exists. Replace it with hand-computed expected outputs for at least 8 cases, including the 60-day boundary, a fractional month total, missing status (refused), and a date inside the expired 2008-2010 window (refused). Each expected value is computed by the owner from the paragraph, not by the engine. |

### M3 - the formalism decision (P1, after M2)

This is the `resources/28` trigger: compare SUMO+Sigma against LegalRuleML+SHACL on one worked M2 example, and decide once. One independent (non-Pease) evaluation is required first (row 28, independence gap). `tools/evaluate.py` retires after M2, by owner decision.

---

## Risks

| Risk | Mitigation |
|---|---|
| Rewriting a working evaluator (CLAUDE.md section 10) | `evaluate.py` is untouched in M1. The byte parity rows on 11 cases, under 3 ledger states, gate the cutover. |
| Clause transcription error, proved precisely | Human attestation per clause (Task 7). `inferred` is labelled, so the verifier knows where to push. |
| Custom expression language grows into a programming language | The operator set is fixed in `engine.OPS`, and a new operator needs a stated clause that requires it. No loops, no recursion, no user functions. |
| Quorum of one for clauses | The existing recorded deviation, extended explicitly (Task 2 step 1). Its condition stands: restore quorum 2 before any output reaches a Marine. |
| The 365-day versus one-year finding propagates into the engine | Inherited deliberately and labelled `inferred` on `FORFEITURE_DATE`. The open finding stays open. |
