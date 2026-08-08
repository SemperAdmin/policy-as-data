"""Cross-tier rule reconciliation.

The question this answers: does the Marine Corps implementation state the same
value as the authority it claims to implement?

Nobody can check that today at any scale. A search index over PDFs cannot answer
it, which is why it is the proof that the encoding is worth having rather than a
demonstration of a feature.

How it works
------------
Values carrying the same `concept` are gathered from every tier, converted to
the concept's canonical unit through an explicit table, and compared. Every
emitted line carries the identifier and the paragraph label of the value it
came from.

Verdicts
--------
AGREE           two or more tiers, all values equal after conversion
DIVERGE         two or more tiers, values differ. THE FINDING.
NOT_HELD        the concept exists at one tier only. Also a finding: the absence
                of an encoded authority under a service rule is worth reporting,
                exactly as a missing tier on a spine page is.
NOT_COMPARABLE  something blocks the comparison, and the reason is named

Withholding (decision B1, 2026-08-08)
--------------------------------------
A value that is not VERIFIED is NOT printed and NOT compared. The tier is
reported as present, cited, and withheld, and the verdict becomes
NOT_COMPARABLE.

The rejected alternative was printing it under a downgrade banner. The banner is
the first thing lost when a number is screenshotted into an email, and these are
entitlement values. Computing AGREE from an unverified value would be worse
still: a verdict travels more easily than a number does.

Consequence, stated rather than discovered: until the DoD tier of the parental
leave concept is verified, this tool reports NOT_COMPARABLE and nothing else.
That is correct.

Usage
-----
    python tools/reconcile.py
    python tools/reconcile.py --json
    python tools/reconcile.py --out config/reconciliation.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_status import (  # noqa: E402
    DATA, LEDGER, POLICY, VERIFIED, derive, live_rule_assertions, load_ledger,
    load_policy,
)

ROOT = Path(__file__).resolve().parent.parent
CONCEPTS = ROOT / "config" / "rule_concepts.json"
UNITS = ROOT / "config" / "units.json"

AGREE = "AGREE"
DIVERGE = "DIVERGE"
NOT_HELD = "NOT_HELD"
NOT_COMPARABLE = "NOT_COMPARABLE"

# Tier from the identifier, per NAMESPACES.md section 2. Longest prefix wins,
# so the DON and USMC branches are matched before the bare /us/dod/ one.
TIER_PREFIXES = [
    ("/us/usc/", "T0", "statute"),
    ("/us/dod/don/usmc/maradmin/", "T5", "message"),
    ("/us/dod/don/usmc/navmc/", "T4", "service manual"),
    ("/us/dod/don/usmc/mcrp/", "T4", "doctrine"),
    ("/us/dod/don/usmc/mctp/", "T4", "doctrine"),
    ("/us/dod/don/usmc/mcwp/", "T4", "doctrine"),
    ("/us/dod/don/usmc/mcdp/", "T4", "doctrine"),
    ("/us/dod/don/usmc/mcbul/", "T3", "service directive"),
    ("/us/dod/don/usmc/mco/", "T3", "service directive"),
    ("/us/dod/don/", "T2", "department of the navy"),
    ("/us/dod/", "T1", "department of defense"),
    ("/us/eop/", "TX", "executive"),
]


def tier_of(identifier: str):
    """Return (tier, label). Unknown is stated, never guessed."""
    for prefix, tier, label in sorted(TIER_PREFIXES, key=lambda p: -len(p[0])):
        if identifier.startswith(prefix):
            return tier, label
    return "T?", "unrecognised identifier space"


def load_units(path: Path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    table = {(c["from"], c["to"]): c for c in doc["conversions"]}
    refused = {r["unit"]: r["reason"] for r in doc.get("refused", [])}
    return table, refused


def convert(value, unit, target, table, refused):
    """Convert or refuse. Never infers a factor."""
    if unit == target:
        return value, None
    if unit in refused:
        return None, f"unit '{unit}' is refused: {refused[unit]}"
    conv = table.get((unit, target))
    if conv is None:
        return None, f"no conversion from '{unit}' to '{target}' in config/units.json"
    return value * conv["factor"], None


def gather(data_dir: Path, status_by_assertion: dict):
    """Every rule value in the corpus, with its tier and verification status."""
    items = []
    for path in sorted(data_dir.glob("*.rules.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        source = doc.get("source", {})
        identifier = source.get("identifier", path.stem)
        tier, tier_label = tier_of(identifier)
        for rule in doc.get("rules", []):
            aid = f"{identifier}#{rule['id']}"
            citation = rule.get("citation") or {}
            items.append({
                "assertion": aid,
                "concept": rule.get("concept"),
                "rule_id": rule["id"],
                "value": rule.get("value"),
                "unit": rule.get("unit"),
                "tier": tier,
                "tier_label": tier_label,
                "document": source.get("label"),
                "document_identifier": identifier,
                "source_url": source.get("url"),
                "citation_label": citation.get("label"),
                "citation_identifier": citation.get("identifier"),
                "verification": status_by_assertion.get(aid, "UNVERIFIED"),
            })
    return items


def reconcile(concepts: list, items: list, table: dict, refused: dict):
    findings = []
    for concept in concepts:
        cid, target = concept["id"], concept["canonical_unit"]
        members = [i for i in items if i.get("concept") == cid]

        tiers, withheld, blocked = [], [], []
        for item in members:
            row = {
                "tier": item["tier"], "tier_label": item["tier_label"],
                "document": item["document"],
                "source_url": item.get("source_url"),
                "citation_label": item["citation_label"],
                "citation_identifier": item["citation_identifier"],
                "assertion": item["assertion"],
                "verification": item["verification"],
            }
            # B1: not verified means not printed and not compared.
            if item["verification"] != VERIFIED:
                withheld.append({**row, "reason": (
                    f"value present but {item['verification']}; withheld per the "
                    f"publication rule for unverified values")})
                continue
            converted, problem = convert(item["value"], item["unit"], target,
                                         table, refused)
            if problem:
                blocked.append({**row, "reason": problem})
                continue
            row.update({"stated": f"{item['value']} {item['unit']}",
                        "canonical": converted})
            tiers.append(row)

        if withheld or blocked:
            verdict = NOT_COMPARABLE
            detail = "; ".join(
                f"{w['tier']} {w['reason']}" for w in (withheld + blocked))
        elif len(tiers) == 0:
            verdict = NOT_HELD
            detail = "no verified value at any tier"
        elif len(tiers) == 1:
            verdict = NOT_HELD
            detail = (f"stated only at {tiers[0]['tier']} "
                      f"({tiers[0]['tier_label']}); no other tier holds it")
        else:
            values = {t["canonical"] for t in tiers}
            verdict = AGREE if len(values) == 1 else DIVERGE
            detail = (f"{len(tiers)} tiers agree at {tiers[0]['canonical']} {target}"
                      if verdict == AGREE else
                      f"{len(tiers)} tiers state "
                      + ", ".join(f"{t['tier']}={t['canonical']}" for t in tiers)
                      + f" {target}")

        findings.append({
            "concept": cid, "label": concept["label"],
            "canonical_unit": target, "verdict": verdict, "detail": detail,
            "tiers": sorted(tiers, key=lambda t: t["tier"]),
            "withheld": sorted(withheld, key=lambda t: t["tier"]),
            "not_comparable": sorted(blocked, key=lambda t: t["tier"]),
        })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--concepts", default=str(CONCEPTS))
    ap.add_argument("--units", default=str(UNITS))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write findings JSON to this path")
    args = ap.parse_args()

    data_dir = Path(args.data)
    # Load the SAME quorum policy verify_status uses. Reading it twice from one
    # file is fine; deciding it twice in two places is not, and an earlier
    # version of this line did exactly that - verify_status reported VERIFIED
    # while reconcile reported QUORUM_SHORT for the same assertion.
    quorum, deviation = load_policy(Path(args.policy))
    status = {r["assertion"]: r["status"]
              for r in derive(live_rule_assertions(data_dir),
                              load_ledger(Path(args.ledger)), quorum)}
    concepts = json.loads(Path(args.concepts).read_text(encoding="utf-8"))["concepts"]
    table, refused = load_units(Path(args.units))
    items = gather(data_dir, status)
    findings = reconcile(concepts, items, table, refused)

    unassigned = [i for i in items if not i.get("concept")]
    payload = {
        "quorum": quorum,
        "deviation": deviation,
        "findings": findings,
        "unassigned_rules": [
            {"assertion": i["assertion"], "tier": i["tier"],
             "citation": i["citation_label"]} for i in unassigned
        ],
    }

    if args.out:
        Path(args.out).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print(f"Reconciliation - {len(findings)} concept(s)")
    if deviation:
        print(f"  QUORUM DEVIATION IN FORCE since {deviation['since']}: "
              f"{deviation['affects']} reduced {deviation['reduced_from']} -> "
              f"{deviation['reduced_to']}. See config/verification_policy.json.")
    print()
    for f in findings:
        print(f"  {f['concept']}  [{f['verdict']}]")
        print(f"    {f['label']}")
        print(f"    {f['detail']}")
        for t in f["tiers"]:
            print(f"      {t['tier']} {t['stated']:>12}  = {t['canonical']} "
                  f"{f['canonical_unit']}   {t['citation_label']}")
            print(f"         {t['citation_identifier']}")
            if t.get("source_url"):
                print(f"         source: {t['source_url']}")
        for w in f["withheld"] + f["not_comparable"]:
            print(f"      {w['tier']} {'(withheld)':>12}  {w['reason']}")
            print(f"         {w['citation_identifier']}  [{w['verification']}]")
        print()

    counts = {}
    for f in findings:
        counts[f["verdict"]] = counts.get(f["verdict"], 0) + 1
    print("Summary: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))

    if unassigned:
        print(f"\nRules carrying no concept ({len(unassigned)}) - not reconciled, "
              f"not silently dropped:")
        for i in unassigned:
            print(f"  {i['tier']}  {i['assertion']}")
            print(f"      {i['citation_label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
