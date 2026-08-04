"""Re-run the provision parser over existing canonical records.

The section text in a canonical record is the faithful extraction, so the
provision tree rebuilds from it without touching source PDFs. Same rooting
rule as canonical_convert.py: messages root provisions on the document,
publications root them on their section.

Path changes are an identity change under the data contract, so every
record this touches gets a dated corrections entry naming what moved.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atomicio import write_json  # noqa: E402
from corrections import record as record_correction  # noqa: E402
from provisions import parse_provisions, uslm_paths      # noqa: E402
from profile_readability import classify, metrics        # noqa: E402

MESSAGE_TYPES = {"MARADMIN", "ALMAR", "ALNAV"}


def reparse(rec):
    doc_type = rec.get("doc_type")
    u = rec.get("uslm_identifier")
    cat = classify(metrics("\n".join(s["text"] for s in rec.get("sections", []))))
    before = {(s["anchor"], p["path"]) for s in rec.get("sections", [])
              for p in s.get("provisions", [])}
    total = 0
    for s in rec.get("sections", []):
        if doc_type in MESSAGE_TYPES and s.get("anchor") == "header":
            s["provisions"] = []
            continue
        base = u if doc_type in MESSAGE_TYPES else s.get("uslm_identifier")
        provs, _ = parse_provisions(s["text"], cat)
        uslm_paths(provs, base)
        s["provisions"] = provs
        total += len(provs)
    after = {(s["anchor"], p["path"]) for s in rec.get("sections", [])
             for p in s.get("provisions", [])}
    added, removed = after - before, before - after
    if added or removed:
        record_correction(rec, "reparse_provisions.py", {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "against": "section text already carried in this record",
            "changes": [
                f"reparse_provisions.py - provision tree rebuilt after the "
                f"reference-list and signature-block parser fixes",
                f"{len(added)} path(s) added, {len(removed)} removed, "
                f"{total} provisions total",
                "reference and enclosure lists now parse under ref/ and encl/ "
                "instead of entering the body marker stack",
                "IDENTITY CHANGE - owner adjudication required under [ID2] "
                "before promotion out of staging",
            ],
        })
    return {"total": total, "added": len(added), "removed": len(removed)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical")
    ap.add_argument("--out", default="canonical_staging")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    names = sorted(f for f in os.listdir(args.src) if f.endswith(".json"))
    if args.only:
        names = [f for f in names if f[:-5] in set(args.only)]
    os.makedirs(args.out, exist_ok=True)
    for name in names:
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        st = reparse(rec)
        write_json(os.path.join(args.out, name), rec)
        print(f"{rec['id']:24} provisions={st['total']:6} "
              f"paths +{st['added']} -{st['removed']}")


if __name__ == "__main__":
    main()
