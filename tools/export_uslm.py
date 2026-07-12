"""Export canonical records to the policy-as-data repo schema.

Canonical 0.2.1 JSON -> usmc-issuance-1.0 XML (v1.1) plus an authority
JSON-LD stub per document. The factory feeding the verified tier.

Non-negotiable preconditions, enforced here:
- publication.publishable == false records are NEVER exported (the Statement C
  quarantine holds in the new home).
- Every issuance and every paragraph exports status="UNVERIFIED" - honest
  under the repo's verification legend, since machine output is not confirmed
  line-by-line against source. Promotion to VERIFIED happens in the repo,
  by a human, per its DATA_CONTRACT.
- Contact masking defaults ON in exported text (emails, phone patterns).
  --no-mask exists for comparison runs only - do not publish unmasked without
  an owner ruling.

Usage:
    python tools\\export_uslm.py --limit 10          (pilot sample)
    python tools\\export_uslm.py                     (full export -> E:\\GunnyBot\\uslm_export)
"""

import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

GB = Path(__file__).resolve().parent.parent
NS = "https://policy.usmc.mil/ns/uslm/1.0"

XMLSAFE_RX = re.compile("[^\x09\x0a\x0d\x20-\ud7ff\ue000-\ufffd]")

EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RX = re.compile(r"(?:\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|\b\d{3}[-.]\d{4}\b|DSN[:\s]*\d{3}[-. ]?\d{4})", re.I)
ORIG_RX = re.compile(r"MSGID/[A-Z]+/([^/\n]+?)//", re.I)
FM_RX = re.compile(r"^FM\s+(.+?)\(?[a-z]*\)?\s*$", re.M)

ONTOLOGY_TYPE = {
    "MARADMIN": "ServiceMessage", "ALMAR": "ServiceMessage", "ALNAV": "ServiceMessage",
    "MCO": "MarineCorpsOrder", "MCBUL": "MarineCorpsOrder", "NAVMC": "MarineCorpsOrder",
    "SECNAV": "NavyIssuance",
}


def mask(text: str, on: bool) -> str:
    text = XMLSAFE_RX.sub("", text)  # strip chars XML 1.0 forbids
    if not on:
        return text
    text = EMAIL_RX.sub("[contact withheld]", text)
    return PHONE_RX.sub("[contact withheld]", text)


def originator_of(r) -> str:
    text = r["sections"][0]["text"][:1500]
    if m := ORIG_RX.search(text):
        return m.group(1).strip()
    if m := FM_RX.search(text):
        return m.group(1).strip()
    return ""


def to_xml(r, do_mask: bool) -> str:
    u = r["uslm_identifier"]
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        "<!-- Machine export from the GunnyBot canonical store (schema 0.2.1).",
        "     Every provision is UNVERIFIED until confirmed against source per",
        "     DATA_CONTRACT.md. Contact details are masked pending owner policy. -->",
        f'<issuance xmlns="{NS}"',
        f'          identifier="{escape(u, {chr(34): "&quot;"})}"',
        f'          issuanceType="{escape(r["doc_type"])}"',
        '          status="UNVERIFIED">',
        "  <meta>",
        f'    <originator>{escape(mask(originator_of(r), do_mask))}</originator>',
    ]
    if r["dates"].get("signed"):
        parts.append(f'    <isoDate>{escape(r["dates"]["signed"])}</isoDate>')
    subject = r.get("subject") or r["title"]
    parts.append(f'    <subject>{escape(mask(subject, do_mask))}</subject>')
    parts.append("  </meta>")

    for s in r["sections"]:
        sid = escape(s["uslm_identifier"], {chr(34): "&quot;"})
        parts.append(f'  <paragraph identifier="{sid}" status="UNVERIFIED" level="section">')
        if s.get("number"):
            num = str(s["number"])
            style = ' style="arabic"' if num.isdigit() else ""
            parts.append(f'    <num{style}>{escape(num)}</num>')
        if s.get("heading"):
            parts.append(f'    <heading>{escape(mask(s["heading"], do_mask))}</heading>')
        parts.append("    <content>")
        body = mask(s["text"], do_mask) or " "
        for chunk in body.split("\n\n") or [" "]:
            parts.append(f'      <p>{escape(chunk)}</p>')
        parts.append("    </content>")
        parts.append("  </paragraph>")
    parts.append("</issuance>")
    return "\n".join(parts)


def to_authority(r, uslm_index) -> dict:
    u = r["uslm_identifier"]
    meta = {e["target"]: e for e in r["relationships"].get("edge_meta", [])
            if e["rel"] == "cancels"}
    supersedes = []
    for tgt in r["relationships"]["cancels"]:
        entry = {"@id": uslm_index.get(tgt, tgt)}
        if tgt in meta:
            entry["basis"] = meta[tgt]["basis"]
        supersedes.append(entry)
    doc = {
        "@id": u,
        "generator": "gunnybot canonical export - UNVERIFIED stub, human review required",
        "canonicalId": r["id"],
        "status": r["status"],
    }
    if r["doc_type"] in ONTOLOGY_TYPE:
        doc["@type"] = ONTOLOGY_TYPE[r["doc_type"]]
    if supersedes:
        doc["supersedes"] = supersedes
    if r["relationships"]["references"]:
        doc["referencesRaw"] = r["relationships"]["references"]
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical-dir", default=str(GB / "canonical"))
    ap.add_argument("--out-dir", default=str(GB / "uslm_export"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="",
                    help="comma-separated record ids (curated subset export)")
    ap.add_argument("--no-mask", action="store_true")
    args = ap.parse_args()
    do_mask = not args.no_mask

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cdir = Path(args.canonical_dir)

    files = sorted(cdir.glob("*.json"))
    if args.limit:
        files = files[: args.limit]
    if args.ids:
        want = {i.strip() for i in args.ids.split(",") if i.strip()}
        files = [f for f in files if f.stem in want]
        missing = want - {f.stem for f in files}
        if missing:
            print(f"WARNING - ids not found: {sorted(missing)}")

    # first pass: uslm index for cross-linking
    uslm_index = {}
    records = []
    for f in files:
        r = json.loads(f.read_text(encoding="utf-8"))
        uslm_index[r["id"]] = r["uslm_identifier"]
        records.append(r)

    exported, excluded = 0, []
    for r in records:
        if not r["publication"]["publishable"]:
            excluded.append(r["id"])
            continue
        stem = r["id"].replace("/", "-")
        (out / f"{stem}.uslm.xml").write_text(to_xml(r, do_mask), encoding="utf-8")
        (out / f"{stem}.authority.jsonld").write_text(
            json.dumps(to_authority(r, uslm_index), indent=2), encoding="utf-8")
        exported += 1

    print(f"exported {exported}, gate-excluded {len(excluded)}, "
          f"masking {'ON' if do_mask else 'OFF'} -> {out}")
    for x in excluded:
        print(f"  excluded: {x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
