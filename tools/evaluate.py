"""MPLP decision evaluator - the deterministic, cited decision engine.

Evaluates a Military Parental Leave Program scenario against the encoded
rules of MARADMIN 051/23 and returns a decision in which EVERY value carries
its citation. Destined for the policy-as-data repo as tools/evaluate.py.

Discipline:
- Rule VALUES come only from data/maradmin-051-23.rules.json. Nothing is
  hardcoded - correct the data, and the decisions change with it.
- Decision LOGIC mirrors specific provisions, cited by identifier on every
  output line.
- Questions the encoded rules cannot answer are REFUSED with the reason
  (convalescent leave, commander extension determinations, RC forfeiture
  particulars). An engine that answers beyond its data is the failure mode
  this project exists to prevent.
- A rule whose status is not VERIFIED downgrades every decision that uses it,
  visibly.

Usage:
  python tools\\mplp_evaluate.py --event-date 2023-01-01 --used-days 70 \
      --second-event-date 2023-03-12
  python tools\\mplp_evaluate.py --event-date 2025-06-01 --proposed-increment 5
  python tools\\mplp_evaluate.py --event-date 2025-06-01 --json
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

RULES_DEFAULT = Path(__file__).resolve().parent.parent / "data" / "maradmin-051-23.rules.json"


def load_rules(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = {r["id"]: r for r in data["rules"]}
    src = data["source"]["label"]
    return rules, src


def cite(rule) -> str:
    tag = "" if rule["status"] == "VERIFIED" else f" [{rule['status']}]"
    return f"{rule['citation']['label']}{tag}"


def d(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default=str(RULES_DEFAULT))
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

    rules, source = load_rules(Path(args.rules))
    MAX = rules["MAX_PARENTAL_LEAVE_DAYS"]
    WINDOW = rules["ENTITLEMENT_WINDOW_DAYS"]
    MININC = rules["MIN_INCREMENT_DAYS"]
    MAXINC = rules["MAX_INCREMENTS"]
    MERGE = rules["EVENT_PROXIMITY_MERGE_HOURS"]

    event = d(args.event_date)
    as_of = d(args.as_of) if args.as_of else date.today()
    findings, refusals = [], []

    def add(key, value, rule, note=""):
        findings.append({"item": key, "value": value,
                         "citation": cite(rule),
                         "identifier": rule["citation"]["identifier"],
                         "note": note})

    governing_event = event
    if args.second_event_date:
        e2 = d(args.second_event_date)
        gap_hours = abs((e2 - event).days) * 24
        if gap_hours <= MERGE["value"]:
            add("multiple_events", "single event - within the merge period",
                MERGE, f"gap {gap_hours}h <= {MERGE['value']}h")
        else:
            add("multiple_events", "separate events - new entitlement runs "
                "concurrently with unexpired prior leave", MERGE,
                f"gap {gap_hours}h > {MERGE['value']}h; concurrency per "
                f"MARADMIN 051/23 para 8.b.(2)(a)")
            governing_event = max(event, e2)

    add("authorized_total_days", MAX["value"], MAX)
    remaining = max(0, MAX["value"] - args.used_days)
    add("remaining_days", remaining, MAX,
        f"{MAX['value']} authorized minus {args.used_days} used")

    forfeit = governing_event + timedelta(days=WINDOW["value"])
    add("forfeiture_date", forfeit.isoformat(), WINDOW,
        "unused leave forfeits after this date unless para 8.a.(3) applies - "
        "commander determination, not computed here")
    if as_of > forfeit:
        add("window_status", "EXPIRED as of evaluation date", WINDOW,
            f"as-of {as_of.isoformat()} is past {forfeit.isoformat()}")
    else:
        add("window_status",
            f"{(forfeit - as_of).days} days remain in the entitlement window",
            WINDOW)

    if args.proposed_increment is not None:
        if args.proposed_increment < MININC["value"]:
            add("proposed_increment", f"INVALID - {args.proposed_increment} days "
                f"is under the {MININC['value']}-day minimum", MININC)
        elif args.increments_used >= MAXINC["value"]:
            add("proposed_increment", f"INVALID - {MAXINC['value']}-increment "
                "maximum already reached", MAXINC)
        else:
            add("proposed_increment", f"valid - increment {args.increments_used + 1} "
                f"of at most {MAXINC['value']}", MININC)

    refusals.append("Convalescent leave - requires a health care provider "
                    "recommendation and commander approval (para 7.a.(1)(a)); "
                    "not computable from encoded rules.")
    refusals.append("Window extension under para 8.a.(3) - a commander "
                    "determination against six qualifying conditions; the engine "
                    "reports the unextended date only.")
    refusals.append("Reserve Component forfeiture particulars (para 8.c.(4)) - "
                    "not yet encoded in rules.json.")

    unverified = [r["id"] for r in rules.values() if r["status"] != "VERIFIED"]
    result = {"source": source, "scenario": vars(args), "decision": findings,
              "out_of_scope": refusals,
              "confidence": "all rules VERIFIED" if not unverified
                            else f"DOWNGRADED - unverified rules: {unverified}"}

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0

    print(f"Decision basis: {source}")
    print(f"Confidence: {result['confidence']}\n")
    for f_ in findings:
        note = f"  ({f_['note']})" if f_["note"] else ""
        print(f"  {f_['item']}: {f_['value']}{note}")
        print(f"      per {f_['citation']}  [{f_['identifier']}]")
    print("\nNot answerable from encoded rules:")
    for r_ in refusals:
        print(f"  - {r_}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
