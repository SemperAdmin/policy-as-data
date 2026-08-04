"""Remove the period from USLM path segments.

WHY THIS EXISTS

USLM's Referencing Model (USLM User Guide section 12.2) assigns the period a
reserved meaning in a reference:

    manifestation (". " prefix) - identifies the format as a simple file
    extension (".xml" for the XML file, ".htm" for HTML, ".pdf" for the PDF).

Our directive numbers carry periods natively - MCO 1050.3J, DoDI 1327.06 -
and rendering them straight into the path produced identifiers like

    /us/dod/don/usmc/mco/1050.3j

A resolver following the published grammar reads that as the work
/us/dod/don/usmc/mco/1050 in the manifestation "3j". The identifier is
ambiguous against the only grammar GPO has published. It is not a
hypothetical: the whole point of adopting the convention is that a third
party can resolve our references without asking us what we meant.

THE FIX

Within every path segment, the period becomes an underscore. RFC 3986
section 2.3 lists the underscore in the unreserved set, and the USLM 2.1
Review Guide requires version strings to be built from exactly that set, so
the substitute is drawn from the vocabulary the specification already uses.

    /us/dod/don/usmc/mco/1050.3j   ->  /us/dod/don/usmc/mco/1050_3j
    /us/dod/dodi/1327.06           ->  /us/dod/dodi/1327_06
    /us/usc/t10/s701               unchanged - statute paths carry no period

The scheme is otherwise untouched. Document ids, native numbers, titles, and
displayed text keep their periods, because that is how a Marine writes them.
Only the machine identifier changes.

THIS IS AN IDENTITY CHANGE under the data contract [ID2]. Every touched
record gets a dated corrections entry, and promotion needs an owner ruling.
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atomicio import write_json  # noqa: E402
from corrections import record as record_correction  # noqa: E402

USLM_RX = re.compile(r"^/us/")


def fix(identifier):
    """Period to underscore inside every segment. Leading slash preserved."""
    if not identifier or not USLM_RX.match(identifier):
        return identifier, False
    parts = identifier.split("/")
    new = [p.replace(".", "_") for p in parts]
    out = "/".join(new)
    return out, out != identifier


def walk(rec):
    changed = 0
    examples = []

    def touch(obj, key):
        nonlocal changed
        val = obj.get(key)
        new, did = fix(val)
        if did:
            obj[key] = new
            changed += 1
            if len(examples) < 3:
                examples.append(f"{val} -> {new}")

    touch(rec, "uslm_identifier")
    for sec in rec.get("sections", []):
        touch(sec, "uslm_identifier")
        for prov in sec.get("provisions", []):
            touch(prov, "uslm_identifier")
            for cit in prov.get("citations", []) or []:
                touch(cit, "target_uslm")
    for m in rec.get("relationships", {}).get("edge_meta", []) or []:
        res = m.get("resolution")
        if not res or "uslm=" not in res:
            continue
        def sub(match):
            new, _ = fix(match.group(1))
            return "uslm=" + new
        newres = re.sub(r"uslm=(/us/[^;]+)", sub, res)
        if newres != res:
            m["resolution"] = newres
            changed += 1
    return changed, examples


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical_staging")
    ap.add_argument("--out", default="canonical_staging")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    total_docs = total_ids = 0
    for name in sorted(os.listdir(args.src)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        n, ex = walk(rec)
        if not n:
            continue
        total_docs += 1
        total_ids += n
        print(f"{rec['id']:24} {n:6} identifier(s)   {ex[0] if ex else ''}")
        if args.dry_run:
            continue
        record_correction(rec, "normalize_identifiers.py", {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "against": "USLM User Guide section 12.2, Referencing Model",
            "changes": [
                "normalize_identifiers.py - period replaced with underscore in "
                "every USLM path segment",
                "the period is reserved in USLM for the manifestation suffix, so "
                "a segment such as mco/1050.3j is ambiguous against the "
                "published grammar",
                "underscore is drawn from the RFC 3986 unreserved set, which the "
                "USLM 2.1 Review Guide already requires for version strings",
                f"{n} identifier(s) rewritten in this record",
                "document id, native number, and displayed text are unchanged",
                "IDENTITY CHANGE - owner adjudication required under [ID2] "
                "before promotion out of staging",
            ],
        })
        write_json(os.path.join(args.out, name), rec)

    print(f"\n{total_docs} record(s), {total_ids} identifier(s) "
          f"{'would be' if args.dry_run else ''} rewritten")


if __name__ == "__main__":
    main()
