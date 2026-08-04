"""Phase R0 - corpus text morphology profile (readability-plan.md).

Classifies every canonical record's body text BEFORE any rendering
change. Categories:

  tiny                  under 5 nonblank lines - stubs, cover sheets
  preformatted-tabular  alignment columns or TOC dot leaders dominate
  flattened             giant lines, no paragraph structure (PRIUM class)
  hard-wrapped          fixed-width extraction breaks mid-sentence
  already-clean         lines end at sentence boundaries
  mixed                 competing signals - needs block-level handling

Thresholds are constants below, tuned on the 2026-07-10 five-type sample
(MARADMIN no_term 80-91 pct, MCO/MCDP/DODFMR 75-81 pct, PRIUM max_len 295).
The R0 acceptance gate is the owner spot-check of 20 stratified records,
NOT these numbers - adjust and rerun freely, the profiler writes, never
reads, the store.

Outputs:
  readability_profile.csv                one row per record
  stdout: category counts, category x doc_type crosstab, and a seeded
          20-record stratified spot-check list for the owner gate.

Usage:
    python tools\\profile_readability.py                (full corpus)
    python tools\\profile_readability.py --sample 300   (quick pass)
"""

import argparse
import csv
import random
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
import json

GB = Path(__file__).resolve().parent.parent

TERM_RX = re.compile(r'[.:!?)\]"”]\s*$')          # sentence-terminal line end
TABULAR_RX = re.compile(r"\S {2,}\S.* {2,}\S")          # 2+ interior multi-space runs
LEADER_RX = re.compile(r"\.{4,}|(?:\. ){4,}")           # TOC dot leaders

# classification thresholds - tune here, rerun, re-gate
TINY_LINES = 5
TABULAR_PCT = 15
LEADER_PCT = 10
FLAT_MED_LEN = 120
FLAT_OVER150_PCT = 20
MIXED_TABULAR_PCT = 5
WRAP_NOTERM_PCT = 60
WRAP_MED_LO, WRAP_MED_HI = 30, 95
CLEAN_NOTERM_PCT = 35


def metrics(text: str) -> dict:
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return {"lines": 0}
    lens = [len(l) for l in lines]
    n = len(lines)
    return {
        "lines": n,
        "med_len": int(statistics.median(lens)),
        "max_len": max(lens),
        "pct_no_term": sum(1 for l in lines if not TERM_RX.search(l)) * 100 // n,
        "pct_tabular": sum(1 for l in lines if TABULAR_RX.search(l)) * 100 // n,
        "pct_leaders": sum(1 for l in lines if LEADER_RX.search(l)) * 100 // n,
        "pct_over_150": sum(1 for x in lens if x > 150) * 100 // n,
        "blank_ratio": round(text.count("\n\n") / max(n, 1), 2),
    }


def classify(m: dict) -> str:
    if m["lines"] < TINY_LINES:
        return "tiny"
    if m["pct_tabular"] >= TABULAR_PCT or m["pct_leaders"] >= LEADER_PCT:
        return "preformatted-tabular"
    if m["med_len"] >= FLAT_MED_LEN or m["pct_over_150"] >= FLAT_OVER150_PCT:
        return "flattened"
    if m["pct_tabular"] >= MIXED_TABULAR_PCT:
        return "mixed"
    if m["pct_no_term"] >= WRAP_NOTERM_PCT and WRAP_MED_LO <= m["med_len"] <= WRAP_MED_HI:
        return "hard-wrapped"
    if m["pct_no_term"] < CLEAN_NOTERM_PCT:
        return "already-clean"
    return "mixed"


FIELDS = ["id", "doc_type", "category", "sections", "lines", "med_len",
          "max_len", "pct_no_term", "pct_tabular", "pct_leaders",
          "pct_over_150", "blank_ratio"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical-dir", default=str(GB / "canonical"))
    ap.add_argument("--out", default=str(GB / "readability_profile.csv"))
    ap.add_argument("--sample", type=int, default=0,
                    help="profile a random N-record subset (seeded)")
    args = ap.parse_args()

    files = sorted(Path(args.canonical_dir).glob("*.json"))
    if args.sample:
        files = random.Random(508).sample(files, min(args.sample, len(files)))
    print(f"profiling {len(files)} records")

    rows, failures = [], 0
    for f in files:
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            failures += 1
            continue
        text = "\n".join(s["text"] for s in r["sections"])
        m = metrics(text)
        if m["lines"] == 0:
            m = {k: 0 for k in FIELDS[4:-1]} | {"lines": 0, "blank_ratio": 0.0}
            cat = "tiny"
        else:
            cat = classify(m)
        rows.append({"id": r["id"], "doc_type": r["doc_type"],
                     "category": cat, "sections": len(r["sections"]), **m})

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    cats = Counter(row["category"] for row in rows)
    print(f"\nwrote {args.out}  ({len(rows)} rows, {failures} read failures)")
    print("\nCATEGORY COUNTS")
    for c, n in cats.most_common():
        print(f"  {c:22} {n:6}  ({n * 100 // len(rows)}%)")

    cross = defaultdict(Counter)
    for row in rows:
        cross[row["doc_type"]][row["category"]] += 1
    cat_order = [c for c, _ in cats.most_common()]
    print("\nCATEGORY x DOC_TYPE")
    header = "  " + f"{'type':10}" + "".join(f"{c[:12]:>14}" for c in cat_order)
    print(header)
    for dt in sorted(cross):
        print("  " + f"{dt:10}" + "".join(f"{cross[dt][c]:>14}" for c in cat_order))

    # Owner spot-check: 20 records stratified across categories (seeded).
    rng = random.Random(508)
    per_cat = defaultdict(list)
    for row in rows:
        per_cat[row["category"]].append(row)
    quota = max(1, 20 // max(len(per_cat), 1))
    picks = []
    for c in cat_order:
        pool = per_cat[c]
        picks += rng.sample(pool, min(quota, len(pool)))
    picks = picks[:20]
    print("\nSPOT-CHECK GATE - eyeball these 20 against their category")
    print("(site page + canonical json, confirm the label fits)")
    for row in picks:
        print(f"  {row['category']:22} {row['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
