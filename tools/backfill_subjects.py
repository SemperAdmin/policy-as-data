"""Recover the Subj: field from naval letter front matter.

Directive records carry subject = null, so a chain page renders "MCO 1050.3J"
where it should read "Regulations for Leave, Liberty, and Administrative
Absence". The subject is not missing from the corpus - it is sitting in the
front matter text, unread, because the provision parser treats Subj: as a
label line and skips it.

Naval letter format puts the subject on the label line and wraps continuation
onto indented lines until the next label. That is the whole grammar, and it is
the same shape the reference-list parser already handles.

Messages are left alone. Their subject comes from the SUBJ/ header field and
is already populated by the converter.

Nothing is invented. A record whose front matter has no Subj: field keeps
subject = null, and the page keeps showing the number.
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

# Subj: opens; the next naval letter label or a blank line closes.
SUBJ_RX = re.compile(
    r"^[ \t]*Subj(?:ect)?[ \t]*:[ \t]*(.*)$", re.I | re.M)
LABEL_RX = re.compile(
    r"^[ \t]*(?:From|To|Via|Ref|Encl|Enclosure|Enclosures|Subj|Subject)"
    r"[ \t]*:", re.I)
MESSAGE_TYPES = {"MARADMIN", "ALMAR", "ALNAV"}
# Page furniture that lands between wrapped subject lines in PDF extraction.
NOISE_RX = re.compile(
    r"^\s*(?:\d+|[A-Z]{2,}\s*\d{3,}|.{0,4}|(?:MCO|NAVMC|SECNAVINST|MCBUL)\s"
    r"[\w.\-]+|\d{1,2}\s+\w{3}\s+\d{2,4}|[A-Z]{1,4}\s?[&(]?[A-Z]*\)?"
    r"\s?\([A-Z\-0-9]+\))\s*$")


def titlecase(text):
    """Naval subjects are printed in caps. Present them readably.

    One rule does most of the work: ANYTHING INSIDE PARENTHESES KEEPS ITS
    CASE. Naval letter format puts the short title and its acronyms there -
    "(MARCORPROMMAN, VOL 1, OFFPROM)", "(PES)" - and title-casing them
    produces "(marcorpromman)", which is not a word in any language. Outside
    parentheses, all-caps is just the printing convention and comes down.
    """
    small = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of",
             "on", "or", "the", "to", "with"}
    keep = {"USMC", "DOD", "DON", "MOS", "PFT", "CFT", "PES", "MCO", "NAVMC",
            "SECNAV", "USC", "CH", "US", "MPLP", "SNCO", "NCO", "TAD", "FY",
            "IRAM", "PME", "BCP", "MCTFS"}
    words, out, depth = text.split(), [], 0
    for i, w in enumerate(words):
        opens, closes = w.count("("), w.count(")")
        inside = depth > 0 or opens > 0
        depth = max(0, depth + opens - closes)
        core = w.strip("(),.:;")
        if inside or core.upper() in keep:
            out.append(w)
        elif w.lower() in small and i not in (0, len(words) - 1):
            out.append(w.lower())
        else:
            out.append(w.capitalize() if w.isupper() else w)
    return " ".join(out)


def extract(rec):
    if rec.get("doc_type") in MESSAGE_TYPES:
        return None
    for sec in rec.get("sections", [])[:3]:
        text = sec.get("text", "")
        m = SUBJ_RX.search(text)
        if not m:
            continue
        parts = [m.group(1).strip()]
        # lstrip the newline the match ends on, or split() yields an empty
        # first element that reads as a blank line and closes the field
        # before the continuation is ever seen
        rest = text[m.end():].lstrip("\r\n").split("\n")
        for line in rest:
            if LABEL_RX.match(line):
                break
            stripped = line.strip()
            if not stripped:
                # a blank line ends the field unless nothing has been read yet
                if parts and parts[0]:
                    break
                continue
            if NOISE_RX.match(line):
                continue
            if len(stripped) > 120:
                break              # a wrapped subject line is short
            parts.append(stripped)
            if len(" ".join(parts)) > 220:
                break
        subject = " ".join(" ".join(parts).split()).strip(" .")
        if len(subject) < 6:
            return None
        return subject[:220]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical_staging")
    ap.add_argument("--out", default="canonical_staging")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    found = skipped = already = 0
    for name in sorted(os.listdir(args.src)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        if rec.get("subject"):
            already += 1
            continue
        subject = extract(rec)
        if not subject:
            skipped += 1
            continue
        found += 1
        print(f"  {rec['id']:24} {subject[:74]}")
        if args.dry_run:
            continue
        rec["subject"] = subject
        # The id prefix is the display form of the issuance type. doc_type
        # says SECNAV where the document says SECNAVINST, and a reader
        # citing the page should see what the document calls itself.
        prefix = rec["id"].split("-")[0]
        native = rec.get("native_number") or rec["id"]
        rec["title"] = f"{prefix} {native} - {titlecase(subject)}"
        record_correction(rec, "backfill_subjects.py", {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "against": "the Subj: field in this record's own front matter text",
            "changes": [
                "backfill_subjects.py - subject recovered from the naval letter "
                "Subj: field, which the provision parser skips as a label line",
                "title rebuilt as doc type, native number, and subject",
                "no text was invented; a record with no Subj: field keeps "
                "subject null",
            ],
        })
        write_json(os.path.join(args.out, name), rec)

    print(f"\nrecovered {found}   already had one {already}   "
          f"no Subj: field {skipped}")


if __name__ == "__main__":
    main()
