"""Derive verification status from the attestation ledger.

Status is NOT stored. It is computed, every build, by comparing what a human
attested to against what the corpus currently says. That is the whole control:
an attestation stops applying the moment the content it bound to changes, and
the change is reported rather than absorbed.

Verdicts
--------
VERIFIED      a live attestation exists, its hash matches, and the quorum for
              this assertion kind is met
INVALIDATED   an attestation exists but the content has changed since. This is
              the interesting one. It is reported loudly and never silently
              downgraded to "unverified" as if no one had ever looked.
REJECTED      a human read it and said the encoding is wrong. A found defect,
              and worth more than a confirmation.
UNABLE        a human tried and could not - usually because the source could not
              be obtained. An honest outcome, per REFERENCES.md.
QUORUM_SHORT  attested, hash matches, but fewer verifiers than the kind requires
UNVERIFIED    no attestation

Quorum
------
Rule values consumed by an evaluator require TWO attestations by DIFFERENT
verifiers. A wrong rule value produces a wrong computed answer about a Marine's
leave with no human between the error and the reader. Provision text requires
one: it is rendered next to its citation where any reader can check it.

An imported seed attestation carries verifier None. Two seeds therefore never
reach quorum on their own, which is the correct behaviour - a legacy claim is
not two independent readings.

Usage
-----
    python tools/verify_status.py                 # summary
    python tools/verify_status.py --json          # machine readable
    python tools/verify_status.py --fail-on-invalidated   # build gate
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import rule_assertion_id, rule_hash  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "verification" / "attestations.jsonl"
DATA = ROOT / "data"
POLICY = ROOT / "config" / "verification_policy.json"

# The target, and what the project holds itself to absent a recorded deviation.
TARGET_QUORUM = {"rule": 2, "provision": 1}


def load_policy(path: Path = POLICY):
    """Quorum from config, so a deviation is a recorded decision rather than an
    edit buried in code. Missing file means the target applies."""
    if not path.exists():
        return dict(TARGET_QUORUM), None
    doc = json.loads(path.read_text(encoding="utf-8"))
    quorum = dict(TARGET_QUORUM)
    quorum.update(doc.get("quorum", {}))
    dev = doc.get("deviation")
    return quorum, (dev if dev and dev.get("in_force") else None)


# Loaded once at import and used as the default everywhere. The previous version
# defaulted to TARGET_QUORUM and relied on every caller remembering to pass the
# policy; two of three callers forgot, and the tools disagreed with each other
# about the same assertion. A default that is wrong when you forget it is a
# defect, not a convention.
QUORUM, DEVIATION = load_policy()

VERIFIED = "VERIFIED"
INVALIDATED = "INVALIDATED"
REJECTED = "REJECTED"
UNABLE = "UNABLE"
QUORUM_SHORT = "QUORUM_SHORT"
UNVERIFIED = "UNVERIFIED"


def load_ledger(path: Path = LEDGER) -> dict:
    """Read the append-only ledger, newest entry per (assertion, verifier) wins."""
    entries: dict = {}
    if not path.exists():
        return entries
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{lineno}: malformed ledger entry - {exc}")
        key = (rec["assertion"], rec.get("verifier"))
        prior = entries.get(key)
        # >= not >, so a same-day supersession wins on file order. Dates are
        # day-resolution by design - a verifier records the day they read, not
        # the second - and append-only file order is the tie-break.
        if prior is None or rec.get("at", "") >= prior.get("at", ""):
            entries[key] = rec
    grouped: dict = {}
    for (assertion, _verifier), rec in entries.items():
        grouped.setdefault(assertion, []).append(rec)
    return grouped


def live_rule_assertions(data_dir: Path = DATA) -> dict:
    """Every rule value currently in the corpus, keyed by assertion id."""
    live = {}
    for path in sorted(data_dir.glob("*.rules.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        source = doc.get("source", {})
        identifier = source.get("identifier", path.stem)
        for rule in doc.get("rules", []):
            aid = rule_assertion_id(identifier, rule["id"])
            live[aid] = {
                "assertion": aid,
                "kind": "rule",
                "file": path.name,
                "rule_id": rule["id"],
                "source_label": source.get("label"),
                "source_url": source.get("url"),
                "source_artifact": (source.get("artifact") or {}).get("sha256"),
                "citation": (rule.get("citation") or {}).get("label"),
                "hash": rule_hash(rule),
                "inline_status": rule.get("status"),
            }
    return live


def derive(live: dict, ledger: dict, quorum: dict | None = None) -> list:
    """Compute a verdict per live assertion. No I/O; reads the module default
    when no quorum is passed, which is the policy loaded at import."""
    quorum = quorum or QUORUM
    results = []
    for aid, item in sorted(live.items()):
        records = ledger.get(aid, [])
        row = dict(item)
        row["attestations"] = len(records)

        if not records:
            row["status"] = UNVERIFIED
            row["detail"] = "no attestation"
            results.append(row)
            continue

        if any(r.get("result") == "REJECTED" for r in records):
            row["status"] = REJECTED
            row["detail"] = next(
                r.get("note", "") for r in records if r.get("result") == "REJECTED"
            )
            results.append(row)
            continue

        matching = [
            r for r in records
            if r.get("result") == "VERIFIED" and r.get("content_hash") == item["hash"]
        ]
        stale = [
            r for r in records
            if r.get("result") == "VERIFIED" and r.get("content_hash") != item["hash"]
        ]

        if not matching and stale:
            row["status"] = INVALIDATED
            row["detail"] = (
                f"content changed since attestation of {stale[0].get('at')}; "
                f"attested {stale[0].get('content_hash')}, live {item['hash']}"
            )
        elif not matching:
            row["status"] = UNABLE
            row["detail"] = next((r.get("note", "") for r in records), "")
        else:
            verifiers = {r.get("verifier") for r in matching}
            needed = quorum.get(item["kind"], 1)
            distinct = len([v for v in verifiers if v is not None])
            has_seed = None in verifiers
            if distinct >= needed:
                row["status"] = VERIFIED
                row["detail"] = f"{distinct} independent attestation(s)"
            elif has_seed and distinct + 1 >= needed:
                row["status"] = QUORUM_SHORT
                row["detail"] = (
                    f"{distinct} independent plus 1 imported seed carrying no named "
                    f"verifier; {needed} independent required"
                )
            else:
                row["status"] = QUORUM_SHORT
                seed_note = " plus 1 imported seed carrying no named verifier" if has_seed else ""
                row["detail"] = (
                    f"{distinct} of {needed} independent attestations{seed_note}"
                )
        row["verifiers"] = sorted(v for v in {r.get("verifier") for r in records} if v)
        results.append(row)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fail-on-invalidated", action="store_true",
                    help="exit 1 if any attestation was invalidated by a content change")
    args = ap.parse_args()

    quorum, deviation = load_policy(Path(args.policy))
    live = live_rule_assertions(Path(args.data))
    ledger = load_ledger(Path(args.ledger))
    rows = derive(live, ledger, quorum)

    orphans = sorted(set(ledger) - set(live))

    if args.json:
        print(json.dumps({"assertions": rows, "orphaned_attestations": orphans,
                          "quorum": quorum, "deviation": deviation},
                         indent=2, ensure_ascii=False))
    else:
        counts = {}
        for r in rows:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
        print(f"Verification status - {len(rows)} rule assertions")
        if deviation:
            print(f"  QUORUM DEVIATION IN FORCE since {deviation['since']}: "
                  f"{deviation['affects']} reduced {deviation['reduced_from']} -> "
                  f"{deviation['reduced_to']}. See config/verification_policy.json.")
        print()
        for r in rows:
            print(f"  [{r['status']:<12}] {r['assertion']}")
            print(f"                 {r['citation'] or '(no citation)'}")
            if r.get("detail"):
                print(f"                 {r['detail']}")
        print("\nSummary: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
        if orphans:
            print("\nOrphaned attestations - the assertion no longer exists:")
            for o in orphans:
                print(f"  {o}")

    invalidated = [r for r in rows if r["status"] == INVALIDATED]
    if invalidated and args.fail_on_invalidated:
        print(f"\nFAIL: {len(invalidated)} attestation(s) invalidated by a content change.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
