"""Record a human verification, one assertion at a time.

The act this tool captures: a person opened the issuing authority's copy, read
the paragraph, and said whether the encoding matches it. Everything else here is
bookkeeping around that act.

Hard rules, each from an existing constraint:

  - NEVER writes canonical/ or data/. DATA_CONTRACT.md makes the store read-only
    to tooling, and a verification tool that edits the thing it is verifying is
    not a verification tool.
  - Appends to the ledger and nothing else. Append-only, so a wrong entry is
    superseded by a later one rather than erased.
  - A rejection writes a correction REQUEST, not a correction. The change goes
    through tools/corrections.py as an owner action.
  - Binds the content hash at the moment of the reading. If the content later
    changes, verify_status.py reports INVALIDATED. That binding is the point.

Usage
-----
    python tools/attest.py --list
    python tools/attest.py --next --verifier V-001
    python tools/attest.py --assertion '<id>' --verifier V-001
    python tools/attest.py --seed          # one-time import of legacy statuses
    python tools/attest.py --ingest        # admit files from verification/incoming/

Verifier ids are opaque. Map them to people in verification/roster.json, which
is gitignored and never published. A public register of who attested to what is
personal data attached to an official act.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import file_hash, rule_hash  # noqa: E402
from verify_status import (  # noqa: E402
    DATA, LEDGER, POLICY, derive, live_rule_assertions, load_ledger, load_policy,
)

ROOT = Path(__file__).resolve().parent.parent
REQUESTS = ROOT / "verification" / "correction_requests.jsonl"
INCOMING = ROOT / "verification" / "incoming"

NEEDS_WORK = {"UNVERIFIED", "INVALIDATED", "QUORUM_SHORT"}


def append(path: Path, record: dict) -> None:
    """Append one JSON object as a line. Atomic enough for an append-only log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def pending(rows: list) -> list:
    return [r for r in rows if r["status"] in NEEDS_WORK]


def show(row: dict, rule: dict) -> None:
    citation = rule.get("citation") or {}
    print("=" * 72)
    print(f"ASSERTION   {row['assertion']}")
    print(f"STATUS      {row['status']}  ({row.get('detail','')})")
    print("-" * 72)
    print(f"CLAIM       {rule.get('value')} {rule.get('unit')}")
    print(f"CITED TO    {citation.get('label')}")
    print(f"            {citation.get('identifier')}")
    print(f"SOURCE      {row.get('source_label')}")
    if row.get("source_url"):
        print(f"OPEN        {row['source_url']}")
    if row.get("source_artifact"):
        print(f"ARTIFACT    {row['source_artifact']}")
        print("            Pass --artifact <path> to bind this reading to the exact")
        print("            file you opened, rather than to whatever the URL serves later.")
    if rule.get("note"):
        print("-" * 72)
        print("NOTE (not hashed, not part of the claim):")
        for line in str(rule["note"]).splitlines():
            print(f"  {line}")
    print("-" * 72)
    print("Open the issuing authority's copy. Confirm the cited paragraph states")
    print("this value. Do not confirm from the note, from another tier, or from")
    print("memory.")
    print("=" * 72)


def load_rule(file_name: str, rule_id: str, data_dir: Path):
    doc = json.loads((data_dir / file_name).read_text(encoding="utf-8"))
    for rule in doc.get("rules", []):
        if rule["id"] == rule_id:
            return doc, rule
    raise SystemExit(f"rule {rule_id} not found in {file_name}")


def seed(data_dir: Path, ledger_path: Path, verifier: str | None = None) -> int:
    """One-time import of inline statuses as attestations.

    Honest terms. An inline VERIFIED becomes an attestation with method
    'imported' and verifier None, carrying whatever the corrections array says
    it was confirmed against. It binds the hash NOW, so future drift is caught,
    and it does not pretend to be an independent reading - verifier None never
    counts toward quorum. An inline UNVERIFIED seeds nothing; absence of an
    attestation already says that.
    """
    existing = load_ledger(ledger_path)
    written = 0
    for path in sorted(data_dir.glob("*.rules.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        source = doc.get("source", {})
        identifier = source.get("identifier", path.stem)
        corrections = doc.get("corrections", [])
        latest = corrections[-1] if corrections else {}
        for rule in doc.get("rules", []):
            if rule.get("status") != "VERIFIED":
                continue
            aid = f"{identifier}#{rule['id']}"
            if any(r.get("method") == "imported" for r in existing.get(aid, [])):
                continue
            append(ledger_path, {
                "assertion": aid,
                "kind": "rule",
                "content_hash": rule_hash(rule),
                "verified_against": {
                    "edition": source.get("label"),
                    "obtained": latest.get("against", "not recorded"),
                    "artifact_hash": None,
                },
                "verifier": verifier,
                "at": (latest.get("date") or "1970-01-01") + "T00:00:00+00:00",
                "method": "imported",
                "result": "VERIFIED",
                "note": ("Imported from the inline status on 2026-08-08. Binds the "
                         "hash so later drift is detected. "
                         + ("Attributed to a named verifier by owner decision; carries "
                            "no source artifact hash."
                            if verifier else
                            "Carries no named verifier and no source artifact hash, so "
                            "it does not count toward quorum.")),
            })
            written += 1
    print(f"seeded {written} imported attestation(s) into {ledger_path}")
    return 0


def ingest(data_dir: Path, ledger_path: Path, incoming: Path) -> int:
    """Admit attestation files produced by docs/verification.html.

    The trust boundary is here. A file from a browser carries a hash the browser
    saw; this recomputes the hash from the corpus and compares. A mismatch means
    the record changed after the person read it, so the reading no longer applies
    to what is on disk and the file is refused rather than reconciled. Guessing
    which one is right would be exactly the kind of silent repair this project
    exists to prevent.
    """
    if not incoming.exists():
        print(f"nothing to ingest: {incoming} does not exist")
        return 0
    live = live_rule_assertions(data_dir)
    existing = load_ledger(ledger_path)
    admitted = refused = skipped = 0

    for path in sorted(incoming.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"  REFUSED {path.name}: not valid JSON - {exc}")
            refused += 1
            continue

        problems = [f"missing {f}" for f in
                    ("assertion", "verifier", "at", "result", "verified_against")
                    if not rec.get(f)]
        aid = rec.get("assertion")
        item = live.get(aid)
        if item is None:
            problems.append(f"unknown assertion {aid!r}")
        if rec.get("result") not in ("VERIFIED", "REJECTED", "UNABLE"):
            problems.append(f"result {rec.get('result')!r} is not a recognised outcome")
        if rec.get("result") != "VERIFIED" and not str(rec.get("note", "")).strip():
            problems.append("a reason is required for rejected or unable")
        va = rec.get("verified_against") or {}
        if len(str(va.get("obtained", ""))) < 12:
            problems.append("verified_against.obtained is too thin to retrace")

        if item is not None:
            seen = rec.get("content_hash_seen") or rec.get("content_hash")
            if seen and seen != item["hash"]:
                problems.append(
                    f"content changed since the reading. Seen {seen}, live "
                    f"{item['hash']}. The record was edited after it was read, so "
                    f"the reading has to happen again.")

        if problems:
            print(f"  REFUSED {path.name}")
            for p in problems:
                print(f"          {p}")
            refused += 1
            continue

        entry = {
            "assertion": aid,
            "kind": item.get("kind", "rule"),
            "content_hash": item["hash"],
            "verified_against": {
                "edition": va.get("edition"),
                "obtained": va.get("obtained"),
                "url": va.get("url"),
                "artifact_hash": va.get("artifact_hash"),
            },
            "verifier": rec["verifier"],
            "at": rec["at"],
            "method": rec.get("method", "read-and-compare"),
            "result": rec["result"],
            "note": rec.get("note", ""),
            "source_file": path.name,
        }
        if any(e.get("verifier") == entry["verifier"] and e.get("at") == entry["at"]
               and e.get("content_hash") == entry["content_hash"] and
               e.get("result") == entry["result"]
               for e in existing.get(aid, [])):
            print(f"  already recorded, skipping {path.name}")
            skipped += 1
            continue
        append(ledger_path, entry)
        existing.setdefault(aid, []).append(entry)
        print(f"  admitted {path.name} -> {entry['result']} {aid} by {entry['verifier']}")
        admitted += 1

    print(f"ingest: {admitted} admitted, {refused} refused, {skipped} already present")
    print("Files are left in place. Move or delete them yourself once satisfied.")
    return 1 if refused else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--list", action="store_true", help="show what still needs work")
    ap.add_argument("--next", action="store_true", help="attest the first pending assertion")
    ap.add_argument("--assertion", help="attest a specific assertion id")
    ap.add_argument("--verifier", help="opaque verifier id, e.g. V-001")
    ap.add_argument("--artifact", help="path to the file actually read; its SHA-256 is "
                                       "recorded so the reading binds to that copy")
    ap.add_argument("--seed", action="store_true", help="one-time import of inline statuses")
    ap.add_argument("--ingest", action="store_true",
                    help="admit attestation files from verification/incoming/")
    ap.add_argument("--incoming", default=str(INCOMING))
    args = ap.parse_args()

    data_dir, ledger_path = Path(args.data), Path(args.ledger)

    if args.seed:
        return seed(data_dir, ledger_path, args.verifier)

    if args.ingest:
        return ingest(data_dir, ledger_path, Path(args.incoming))

    quorum, deviation = load_policy(Path(args.policy))
    if deviation:
        print(f"QUORUM DEVIATION IN FORCE since {deviation['since']}: "
              f"{deviation['affects']} reduced {deviation['reduced_from']} -> "
              f"{deviation['reduced_to']}. See config/verification_policy.json.\n")
    live = live_rule_assertions(data_dir)
    rows = derive(live, load_ledger(ledger_path), quorum)
    todo = pending(rows)

    if args.list or not (args.next or args.assertion):
        print(f"{len(todo)} of {len(rows)} rule assertions need work\n")
        for r in todo:
            print(f"  [{r['status']:<12}] {r['assertion']}")
            print(f"                 {r['citation']}  -  {r.get('detail','')}")
        if not todo:
            print("  nothing pending")
        return 0

    if args.assertion:
        target = next((r for r in rows if r["assertion"] == args.assertion), None)
        if target is None:
            raise SystemExit(f"unknown assertion: {args.assertion}")
    else:
        if not todo:
            print("nothing pending")
            return 0
        target = todo[0]

    if not args.verifier:
        raise SystemExit("--verifier is required to record an attestation")

    doc, rule = load_rule(target["file"], target["rule_id"], data_dir)
    show(target, rule)

    answer = input("verified / rejected / unable / skip  [v/r/u/s]: ").strip().lower()
    if answer in ("s", "skip", ""):
        print("skipped, nothing written")
        return 0
    if answer not in ("v", "r", "u"):
        raise SystemExit("unrecognised answer, nothing written")

    edition = input("source edition read (blank = the label above): ").strip() \
        or doc.get("source", {}).get("label")

    # Provenance is what lets a future reader re-run this reading. One word does
    # not. Re-prompt rather than accept something that will be useless later.
    suggested = target.get("source_url") or ""
    if suggested:
        print(f"source link on record: {suggested}")
    url = input("link to the copy you read (blank = the link above): ").strip() or suggested

    while True:
        obtained = input(
            "where and when the source was obtained\n"
            "  e.g. 'esd.whs.mil, PDF downloaded 2026-08-08'\n  > ").strip()
        if len(obtained) >= 12 and any(c.isdigit() for c in obtained):
            break
        print("  too thin - name the source and the date you got it.")

    # Ask last, validate in place. An earlier version raised SystemExit here and
    # threw away every answer already typed, which is a defect in a tool whose
    # whole job is capturing careful human work.
    while True:
        at = input("date of reading, YYYY-MM-DD: ").strip()
        if len(at) == 10 and at[4] == "-" and at[7] == "-" and \
                at.replace("-", "").isdigit():
            break
        print("  need YYYY-MM-DD. Nothing typed so far is lost.")

    result = {"v": "VERIFIED", "r": "REJECTED", "u": "UNABLE"}[answer]
    while True:
        note = input("note (required for rejected and unable): ").strip()
        if result == "VERIFIED" or note:
            break
        print("  a reason is required. Nothing typed so far is lost.")

    append(ledger_path, {
        "assertion": target["assertion"],
        "kind": "rule",
        "content_hash": rule_hash(rule),
        "verified_against": {
            "edition": edition,
            "obtained": obtained,
            "url": url or None,
            "artifact_hash": file_hash(args.artifact) if args.artifact else None,
            "artifact_path": args.artifact,
        },
        "verifier": args.verifier,
        "at": at + "T00:00:00+00:00",
        "method": "read-and-compare",
        "result": result,
        "note": note,
    })
    print(f"\nrecorded {result} for {target['assertion']}")

    if result == "REJECTED":
        correct = input("what does the source actually say: ").strip()
        append(REQUESTS, {
            "assertion": target["assertion"], "raised_by": args.verifier, "at": at,
            "encoded": {"value": rule.get("value"), "unit": rule.get("unit")},
            "source_states": correct, "note": note, "state": "OPEN",
        })
        print(f"correction request written to {REQUESTS}")
        print("The data was NOT changed. Apply it through tools/corrections.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
