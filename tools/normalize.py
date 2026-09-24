"""Canonical normalization and content hashing for verification.

An attestation binds to the exact content a human confirmed. That binding is
only useful if the hash changes when the meaning changes and does NOT change
when the file is merely rewritten. This module is that rule, in one place.

Why the normalization is not optional
-------------------------------------
The working tree is CRLF and files written from a Linux environment arrive with
LF (SESSION_HANDOFF.md section 8). Hashing raw bytes would invalidate every
attestation in the corpus on the first Windows/Linux round trip, and the
verification effort would evaporate silently. So bytes are normalized before
hashing, and the rule is written down rather than left to whatever the caller
happened to do.

What is hashed, and what deliberately is not
--------------------------------------------
For a PROVISION: its text only. Not the identifier, not the label, not the
depth, not the position. Renumbering or moving a provision must not invalidate a
human's reading of its words. Only a change to what it SAYS should.

For a RULE VALUE: the value, the unit, and the citation identifier - the
assertion itself. Not the note, not the label, not the id. Editing prose in a
note is not a change to the claim; changing 84 to 90, or repointing the citation
from para 11.d to para 8, is.

For a LOGIC CLAUSE: clause_hash is the clause's own core (every key but
$comment and status). The ledger does NOT bind that; it binds
clause_dependency_hash, which adds the facts the clause reaches, the input
specs it reads, the clauses ahead of it in its item group, and the rules file.
A clause's answer depends on all of them, so an attestation must too.

Normalization steps, in order:
  1. Line endings to \\n
  2. Trailing whitespace stripped per line
  3. Runs of internal whitespace collapsed to one space
  4. Leading and trailing blank lines removed
  5. Unicode NFC

Step 3 is the aggressive one and it is deliberate. Naval message text arrives
with alignment padding that carries no meaning, and a reader confirming a
paragraph is confirming words, not columns.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata

ALGORITHM = "sha256"
PREFIX = "sha256:"

_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)
_INTERNAL_WS = re.compile(r"[ \t]{2,}")


def normalize_text(text: str) -> str:
    """Apply the canonical normalization. Pure, and safe on any input."""
    if text is None:
        return ""
    s = text.replace("\r\n", "\n").replace("\r", "\n")
    s = _TRAILING_WS.sub("", s)
    s = _INTERNAL_WS.sub(" ", s)
    # Strip every line, not only blank ones. Leading indentation is layout, not
    # meaning, and a reader confirming a paragraph is confirming words. The
    # first version of this line only stripped blank lines, which is a no-op,
    # and the smoke check below caught it.
    s = "\n".join(line.strip() for line in s.split("\n"))
    s = s.strip("\n").strip()
    return unicodedata.normalize("NFC", s)


def content_hash(text: str) -> str:
    """Hash of a provision's text, after normalization."""
    digest = hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()
    return PREFIX + digest


def rule_assertion(rule: dict) -> dict:
    """The hashable core of a rule value.

    Value, unit, and the citation identifier. Nothing else. See the module
    docstring for why the note and the label are excluded.
    """
    citation = rule.get("citation") or {}
    return {
        "value": rule.get("value"),
        "unit": rule.get("unit"),
        "citation_identifier": citation.get("identifier"),
    }


def rule_hash(rule: dict) -> str:
    """Hash of a rule's assertion. Key order is fixed by sort_keys."""
    payload = json.dumps(
        rule_assertion(rule), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def rule_assertion_id(source_identifier: str, rule_id: str) -> str:
    """Stable id for a rule assertion: <document identifier>#<RULE_ID>."""
    return f"{source_identifier}#{rule_id}"


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


def _expression_refs(node, facts: set, inputs: set) -> None:
    """Collect fact and input names read anywhere in an expression tree. Walks
    every dict and list value generically, so this module needs no knowledge of
    the engine's operators and does not import it."""
    if isinstance(node, list):
        for item in node:
            _expression_refs(item, facts, inputs)
        return
    if not isinstance(node, dict):
        return
    op = node.get("op")
    if op == "fact":
        facts.add(node.get("name"))
    elif op in ("input", "present"):
        inputs.add(node.get("name"))
    for value in node.values():
        _expression_refs(value, facts, inputs)


def clause_dependency_payload(doc: dict, clause_id: str) -> dict:
    """Everything a clause's answer depends on, besides admitted rule values
    (which the ledger admits separately, per rule).

    The clause alone is not enough. Measured in the final review of the clause
    engine (2026-09-24): editing a fact, reordering an item group, deleting an
    earlier clause, or changing an input default all changed decisions while
    every clause hash stayed put and every clause stayed VERIFIED. So the hash a
    verifier binds covers:
      clause       the clause's own assertion (clause_assertion)
      facts        every fact the clause reaches, transitively, with its expr
      inputs       the declared spec of every input the clause or a reached
                   fact reads (op input or present), default included
      preceded_by  [id, clause_dependency_hash(doc, id)] for the one clause
                   directly before this one in its item group, or null for
                   the first clause in the group - first match means an
                   earlier clause decides whether this one is ever reached.
                   Only the immediate predecessor is bound, not the full list
                   of earlier clauses: each predecessor's own dependency hash
                   already binds ITS predecessor, so the chain transitively
                   covers every earlier clause in the group at O(1) links per
                   clause. Binding the full list (as this did before the
                   2026-09-24 review) makes each hash embed every earlier
                   hash's own embedded history, which is exponential in group
                   size (measured: 14.6s at 20 clauses) for the same coverage
                   the chain gives in linear time.
      rules_file   which rules file the clause's rule ids resolve against
    """
    clauses = doc.get("clauses", [])
    clause = next(c for c in clauses if c.get("id") == clause_id)
    fact_exprs = {f.get("name"): f.get("expr") for f in doc.get("facts", [])}
    input_specs = {i.get("name"): i for i in doc.get("inputs", [])}

    core = clause_assertion(clause)
    facts: set = set()
    inputs: set = set()
    _expression_refs(core, facts, inputs)
    # Transitive closure over facts. A seen-set, not an acyclicity assumption:
    # check_logic.py rejects a cycle, but this must terminate on a file that
    # has not been checked yet.
    seen: set = set()
    queue = sorted(n for n in facts if n is not None)
    while queue:
        name = queue.pop()
        if name in seen:
            continue
        seen.add(name)
        more: set = set()
        _expression_refs(fact_exprs.get(name), more, inputs)
        queue.extend(n for n in more if n is not None and n not in seen)

    prev = None
    for c in clauses:
        if c is clause:
            break
        if c.get("item") == clause.get("item"):
            prev = c
    preceded_by = ([prev.get("id"), clause_dependency_hash(doc, prev.get("id"))]
                    if prev is not None else None)

    return {
        "clause": core,
        "facts": {n: fact_exprs.get(n) for n in sorted(seen)},
        "inputs": {n: input_specs.get(n) for n in sorted(i for i in inputs if i is not None)},
        "preceded_by": preceded_by,
        "rules_file": doc.get("rules_file"),
    }


def clause_dependency_hash(doc: dict, clause_id: str) -> str:
    """The hash the ledger binds for a clause: its dependency payload, sorted
    keys, same pattern as clause_hash. See clause_dependency_payload."""
    payload = json.dumps(
        clause_dependency_payload(doc, clause_id),
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def clause_assertion_id(source_identifier: str, clause_id: str) -> str:
    """Stable id for a clause assertion: <document identifier>#logic/<CLAUSE_ID>."""
    return f"{source_identifier}#logic/{clause_id}"


def file_hash(path) -> str:
    """Hash of a file's raw bytes. For signed artifacts, NOT for text.

    A signed PDF is evidence, not prose. Normalizing it would be wrong.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return PREFIX + h.hexdigest()


if __name__ == "__main__":  # pragma: no cover - smoke check
    samples = [
        "84 days\r\nper para 11.d",
        "84 days\nper para 11.d",
        "84 days   \n   per   para 11.d  ",
        "\n\n84 days\nper para 11.d\n\n",
    ]
    hashes = {content_hash(s) for s in samples}
    print("CRLF/LF/whitespace/padding variants collapse to one hash:", len(hashes) == 1)
    print(content_hash(samples[0]))
    print("a real change moves it:", content_hash("90 days\nper para 11.d") not in hashes)
