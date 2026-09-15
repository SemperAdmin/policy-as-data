"""MPLP decision evaluator - the deterministic, cited decision engine.

Evaluates a Military Parental Leave Program scenario against the encoded
rules of MARADMIN 051/23 and returns a decision in which EVERY value carries
its citation.

Discipline:
- Rule VALUES come only from data/maradmin-051-23.rules.json. Nothing is
  hardcoded - correct the data, and the decisions change with it.
- Decision LOGIC mirrors specific provisions, cited by identifier on every
  output line.
- Questions the encoded rules cannot answer are REFUSED with the reason
  (convalescent leave, commander extension determinations, RC forfeiture
  particulars). An engine that answers beyond its data is the failure mode
  this project exists to prevent.
- Verification status comes from the attestation ledger, derived the same
  way tools/verify_status.py derives it, never from the inline `status`
  field in the rules file. That field is a legacy claim. ACTION-REGISTER 5.4.
- A rule that is not VERIFIED is not used. Every decision line that depends
  on it is WITHHELD and names the rule (decision B1, applied to the evaluator).
  Nothing computed from an unadmitted value reaches the output.

Usage:
  python tools/evaluate.py --event-date 2023-01-01 --used-days 70 \
      --second-event-date 2023-03-12
  python tools/evaluate.py --event-date 2025-06-01 --proposed-increment 5
  python tools/evaluate.py --event-date 2025-06-01 --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import rule_assertion_id, rule_hash  # noqa: E402
from verify_status import LEDGER, POLICY, VERIFIED, derive, load_ledger, load_policy  # noqa: E402

RULES_DEFAULT = Path(__file__).resolve().parent.parent / "data" / "maradmin-051-23.rules.json"

# Rule ids the logic below depends on. Values still come from the file.
REQUIRED = ("MAX_PARENTAL_LEAVE_DAYS", "ENTITLEMENT_WINDOW_DAYS", "MIN_INCREMENT_DAYS",
            "MAX_INCREMENTS", "EVENT_PROXIMITY_MERGE_HOURS")


def load_rules(path: Path, ledger_path: Path, policy_path: Path):
    """Rules from the file, status from the ledger. The inline status is ignored."""
    data = json.loads(path.read_text(encoding="utf-8"))
    identifier = data["source"]["identifier"]
    live = {}
    for r in data["rules"]:
        aid = rule_assertion_id(identifier, r["id"])
        live[aid] = {"assertion": aid, "kind": "rule", "hash": rule_hash(r)}
    quorum, deviation = load_policy(policy_path)
    derived = {row["assertion"]: row for row in derive(live, load_ledger(ledger_path), quorum)}
    rules = {}
    for r in data["rules"]:
        row = derived[rule_assertion_id(identifier, r["id"])]
        rules[r["id"]] = {**r, "verification": row["status"], "verification_detail": row.get("detail", "")}
    missing = [rid for rid in REQUIRED if rid not in rules]
    if missing:
        raise SystemExit(f"rules file {path} lacks required rule id(s): {missing}")
    return rules, data["source"]["label"], deviation


def cite(rule) -> str:
    return rule["citation"]["label"]


def d(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def evaluate(rules, source, deviation, *, event_date, as_of=None, second_event_date=None,
             used_days=0, increments_used=0, proposed_increment=None) -> dict:
    """The decision, as data. Every line cites; every line resting on a rule
    the ledger has not admitted is withheld and names the rule. Callable
    in-process by docs/scenarios.html's renderer so the page and the CLI
    are one implementation, not two."""
    scenario = {"event_date": event_date, "as_of": as_of, "second_event_date": second_event_date,
                "used_days": used_days, "increments_used": increments_used,
                "proposed_increment": proposed_increment}
    MAX = rules["MAX_PARENTAL_LEAVE_DAYS"]
    WINDOW = rules["ENTITLEMENT_WINDOW_DAYS"]
    MININC = rules["MIN_INCREMENT_DAYS"]
    MAXINC = rules["MAX_INCREMENTS"]
    MERGE = rules["EVENT_PROXIMITY_MERGE_HOURS"]
    event = d(event_date)
    as_of = d(as_of) if as_of else date.today()
    findings, withheld, refusals = [], [], []

    def admitted(*deps) -> bool:
        return all(r["verification"] == VERIFIED for r in deps)

    def add(key, value, rule, note="", also=()):
        """Emit a decision line, or withhold it if any rule it rests on is
        not VERIFIED in the ledger. The withheld line still names its
        citation, so the reader can see what was not said and why."""
        deps = (rule, *also)
        if admitted(*deps):
            findings.append({"item": key, "value": value,
                             "citation": cite(rule),
                             "identifier": rule["citation"]["identifier"],
                             "note": note})
        else:
            blockers = [f"{r['id']} [{r['verification']}]" for r in deps
                        if r["verification"] != VERIFIED]
            withheld.append({"item": key, "citation": cite(rule),
                             "identifier": rule["citation"]["identifier"],
                             "withheld_because": blockers})

    # Multiple events. The governing event feeds the forfeiture date, so if the
    # merge rule is unadmitted the forfeiture line is withheld as well.
    governing_event = event
    merge_deps = ()
    if second_event_date:
        e2 = d(second_event_date)
        gap_hours = abs((e2 - event).days) * 24
        merge_deps = (MERGE,)
        if admitted(MERGE) and gap_hours <= MERGE["value"]:
            add("multiple_events", "single event - within the merge period",
                MERGE, f"gap {gap_hours}h <= {MERGE['value']}h")
        elif admitted(MERGE):
            add("multiple_events", "separate events - new entitlement runs "
                "concurrently with unexpired prior leave", MERGE,
                f"gap {gap_hours}h > {MERGE['value']}h; concurrency per "
                f"MARADMIN 051/23 para 8.b.(2)(a)")
            governing_event = max(event, e2)
        else:
            add("multiple_events", None, MERGE)

    add("authorized_total_days", MAX["value"], MAX)
    if admitted(MAX):
        remaining = max(0, MAX["value"] - used_days)
        add("remaining_days", remaining, MAX,
            f"{MAX['value']} authorized minus {used_days} used")
    else:
        add("remaining_days", None, MAX)

    if admitted(WINDOW, *merge_deps):
        forfeit = governing_event + timedelta(days=WINDOW["value"])
        add("forfeiture_date", forfeit.isoformat(), WINDOW,
            "unused leave forfeits after this date unless para 8.a.(3) applies - "
            "commander determination, not computed here", also=merge_deps)
        if as_of > forfeit:
            add("window_status", "EXPIRED as of evaluation date", WINDOW,
                f"as-of {as_of.isoformat()} is past {forfeit.isoformat()}", also=merge_deps)
        else:
            add("window_status",
                f"{(forfeit - as_of).days} days remain in the entitlement window",
                WINDOW, also=merge_deps)
    else:
        add("forfeiture_date", None, WINDOW, also=merge_deps)
        add("window_status", None, WINDOW, also=merge_deps)

    if proposed_increment is not None:
        if not admitted(MININC, MAXINC):
            add("proposed_increment", None, MININC, also=(MAXINC,))
        elif proposed_increment < MININC["value"]:
            add("proposed_increment", f"INVALID - {proposed_increment} days "
                f"is under the {MININC['value']}-day minimum", MININC)
        elif increments_used >= MAXINC["value"]:
            add("proposed_increment", f"INVALID - {MAXINC['value']}-increment "
                "maximum already reached", MAXINC)
        else:
            add("proposed_increment", f"valid - increment {increments_used + 1} "
                f"of at most {MAXINC['value']}", MININC, also=(MAXINC,))

    refusals.append("Convalescent leave - requires a health care provider "
                    "recommendation and commander approval (para 7.a.(1)(a)); "
                    "not computable from encoded rules.")
    refusals.append("Window extension under para 8.a.(3) - a commander "
                    "determination against six qualifying conditions; the engine "
                    "reports the unextended date only.")
    refusals.append("Reserve Component forfeiture particulars (para 8.c.(4)) - "
                    "not yet encoded in rules.json.")

    status = {rid: r["verification"] for rid, r in rules.items()}
    unadmitted = sorted(rid for rid, st in status.items() if st != VERIFIED)
    result = {"source": source, "scenario": scenario,
              "decision": findings, "withheld": withheld,
              "out_of_scope": refusals,
              "verification": {"by_rule": status,
                               "quorum_deviation": deviation,
                               "summary": ("all rules VERIFIED in the ledger" if not unadmitted
                                           else f"{len(unadmitted)} rule(s) not admitted; "
                                                f"lines depending on them withheld: {unadmitted}")}}

    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default=str(RULES_DEFAULT))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--event-date", required=True, help="qualifying event date, YYYY-MM-DD")
    ap.add_argument("--second-event-date", help="second qualifying event date, if any")
    ap.add_argument("--used-days", type=int, default=0,
                    help="parental leave days already used")
    ap.add_argument("--increments-used", type=int, default=0)
    ap.add_argument("--proposed-increment", type=int,
                    help="length in days of a proposed leave increment")
    ap.add_argument("--as-of", help="evaluation date, default today")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    rules, source, deviation = load_rules(Path(args.rules), Path(args.ledger), Path(args.policy))

    result = evaluate(rules, source, deviation, event_date=args.event_date, as_of=args.as_of,
                      second_event_date=args.second_event_date, used_days=args.used_days,
                      increments_used=args.increments_used,
                      proposed_increment=args.proposed_increment)
    findings, withheld, refusals = result["decision"], result["withheld"], result["out_of_scope"]

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0

    print(f"Decision basis: {source}")
    print(f"Verification: {result['verification']['summary']}")
    if deviation:
        print(f"  QUORUM DEVIATION IN FORCE since {deviation['since']}: rule quorum "
              f"{deviation['reduced_from']} -> {deviation['reduced_to']}. "
              f"See config/verification_policy.json.")
    print()
    for f_ in findings:
        note = f"  ({f_['note']})" if f_["note"] else ""
        print(f"  {f_['item']}: {f_['value']}{note}")
        print(f"      per {f_['citation']}  [{f_['identifier']}]")
    for w in withheld:
        print(f"  {w['item']}: WITHHELD - depends on {', '.join(w['withheld_because'])}")
        print(f"      would cite {w['citation']}  [{w['identifier']}]")
    print("\nNot answerable from encoded rules:")
    for r_ in refusals:
        print(f"  - {r_}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
