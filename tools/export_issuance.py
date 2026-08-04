"""Export canonical records to usmc-issuance 2.0 XML.

Replaces tools/export_uslm.py, which was two schema versions stale and had
three defects worth naming, because each one shipped into published files:

1. It read canonical 0.2.1. The store is 0.5.0. Everything the provision
   parser and the authority extractor produce was invisible to it.
2. It wrote status="UNVERIFIED" on the root element while the companion
   authority graph for the same document wrote "status": "active". One
   attribute was carrying two orthogonal facts, so two published artifacts
   contradicted each other. 2.0 separates @lifecycle from @verification.
3. It emitted each section as one flat paragraph holding a raw text dump.
   The provision tree - the whole point of the encoding - never reached the
   XML at all.

THE FILE EXTENSION CHANGED, DELIBERATELY

Output is now .issuance.xml, not .uslm.xml, and the tool is no longer named
for USLM. The vocabulary is a SIBLING of United States Legislative Markup,
in its own namespace, and USLM's own Objective annotation states it "is not
intended to model executive branch or judicial branch documents." Naming our
files .uslm.xml invited exactly the misreading the conformance matrix warns
against. See conformance-matrix.md section 1.

PRECONDITIONS, ENFORCED HERE

- publication.publishable == false is NEVER exported. The Statement C
  quarantine holds in every output layer, by construction rather than by
  discipline.
- Contact masking defaults ON. --no-mask exists for comparison runs only.
- Every provision carries verification UNVERIFIED unless the record says
  otherwise. Promotion is explicit and recorded, never silent.

Usage:
    python tools/export_issuance.py --src canonical_staging --out issuance_export
    python tools/export_issuance.py --src canonical_staging --validate
"""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from xml.sax.saxutils import escape, quoteattr

NS = "https://policy.usmc.mil/ns/usmc-issuance/2.0"
SCHEMA_VERSION = "2.0"

XMLSAFE_RX = re.compile("[^\x09\x0a\x0d\x20-퟿-�]")
EMAIL_RX = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RX = re.compile(
    r"(?:\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}|\b\d{3}[-.]\d{4}\b|DSN[:\s]*\d{3}[-. ]?\d{4})",
    re.I)
ORIG_RX = re.compile(r"MSGID/[A-Z]+/([^/\n]+?)//", re.I)
TIER_RX = re.compile(r"tier=(T[0-9X])")
HOLDS_RX = re.compile(r"store-holds=([^;]+)")
SRC_RX = re.compile(r"^([^;]+);")
DATE_RX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

TIER_OF_TYPE = {
    "USC": "T0",
    "DODI": "T1", "DODD": "T1", "DODM": "T1", "DTM": "T1",
    "DODFMR": "T1", "DODREG": "T1", "CJCSI": "T1",
    "SECNAV": "T2", "SECNAVM": "T2", "OPNAVINST": "T2",
    "BUMEDINST": "T2", "NAVSO": "T2", "SECNAVNOTE": "T2",
    "MCO": "T3", "MCBUL": "T3",
    "NAVMC": "T4", "MCRP": "T4", "MCTP": "T4", "MCWP": "T4", "MCDP": "T4",
    "MARADMIN": "T5", "ALMAR": "T5", "ALNAV": "T5",
    "EO": "TX",
}
CONFIDENCE_TO_HELD = {"high": "held", "revision-drift": "drift",
                      "named-not-held": "absent"}


MASK_ATTRS = True


def mask(text, on):
    text = XMLSAFE_RX.sub("", text or "")
    if not on:
        return text
    text = EMAIL_RX.sub("[contact withheld]", text)
    return PHONE_RX.sub("[contact withheld]", text)


def attr(name, value):
    """Attribute values need the same XML-1.0 character filter as text.

    quoteattr escapes quotes and angle brackets; it does not remove the
    control characters XML 1.0 forbids outright. Extraction from PDF pulls
    those in - a form feed inside a distribution statement is enough - and
    they only surface at parse time, in whichever consumer reads the file
    next. Filter here rather than there.
    """
    if value in (None, ""):
        return ""
    clean = XMLSAFE_RX.sub("", str(value))
    clean = " ".join(clean.split())
    if not clean:
        return ""
    # Masking used to run on element text only, so a contact inside a section
    # heading or a citation's quoted text left the masked tier unmasked.
    # MCO 1400.31D carried a phone number in a heading that way.
    if MASK_ATTRS:
        clean = EMAIL_RX.sub("[contact withheld]", clean)
        clean = PHONE_RX.sub("[contact withheld]", clean)
    return f" {name}={quoteattr(clean)}"


def iso_date(value):
    """Only emit a date the schema will accept. Junk is dropped, not coerced."""
    return value if value and DATE_RX.match(str(value)) else None


def nest(provisions):
    """Rebuild the tree from parent paths.

    The store holds provisions flat with a parent pointer, because that is
    what survives a JSON round trip cleanly. The XML wants them nested, so
    the hierarchy is structural rather than inferable. Orphans - a provision
    whose parent path is absent, which happens when a parent line failed to
    parse - are attached at the top level rather than dropped.
    """
    by_path, children, roots = {}, {}, []
    for p in provisions:
        by_path[p["path"]] = p
        children[p["path"]] = []
    for p in provisions:
        parent = p.get("parent")
        if parent and parent in children:
            children[parent].append(p)
        else:
            roots.append(p)
    return roots, children


def provision_xml(prov, children, indent, do_mask, out):
    sp = " " * indent
    path = prov.get("path", "")
    role = ("reference" if path.split("/")[0].rstrip("0123456789") == "ref"
            else "enclosure" if path.split("/")[0].rstrip("0123456789") == "encl"
            else None)
    out.append(
        f"{sp}<provision"
        + attr("identifier", prov.get("uslm_identifier"))
        + attr("path", path)
        + attr("number", prov.get("number"))
        + attr("label", prov.get("label") or path)
        + attr("depth", prov.get("depth"))
        + attr("role", role)
        + attr("verification", prov.get("verification") or "UNVERIFIED")
        + ">")
    text = mask(prov.get("text", ""), do_mask)
    if text:
        out.append(f"{sp}  <text>{escape(text)}</text>")
    for cit in prov.get("citations") or []:
        out.append(
            f"{sp}  <citation"
            + attr("target", cit.get("target_doc"))
            + attr("targetIdentifier", cit.get("target_uslm"))
            + attr("targetPath", cit.get("target_path"))
            + attr("basis", cit.get("basis") or "cited")
            + attr("text", (cit.get("text") or "")[:300])
            + "/>")
    for child in children.get(path, []):
        provision_xml(child, children, indent + 2, do_mask, out)
    out.append(f"{sp}</provision>")


def to_xml(rec, do_mask=True):
    doc_type = rec.get("doc_type")
    dates = rec.get("dates") or {}
    prov = rec.get("provenance") or {}
    pub = rec.get("publication") or {}

    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append(
        "<!-- Machine export from the canonical store "
        f"(schema {rec.get('schema_version')}).\n"
        "     Every provision is UNVERIFIED until a human confirms it against\n"
        "     source per DATA_CONTRACT.md. Contact details are masked.\n"
        "     @lifecycle is whether the policy is in force. @verification is\n"
        "     whether the extraction has been confirmed. They are different\n"
        "     questions and this schema keeps them apart. -->")
    out.append(
        f'<issuance xmlns="{NS}"'
        + attr("identifier", rec.get("uslm_identifier"))
        + attr("canonicalId", rec.get("id"))
        + attr("docType", doc_type)
        + attr("nativeNumber", rec.get("native_number"))
        + attr("tier", TIER_OF_TYPE.get(doc_type))
        + attr("lifecycle", rec.get("status") or "unknown")
        + attr("verification", rec.get("verification") or "UNVERIFIED")
        + attr("startPeriod", iso_date(dates.get("effective") or dates.get("signed")))
        + attr("endPeriod", iso_date(dates.get("cancelled")))
        + attr("schemaVersion", SCHEMA_VERSION)
        + ">")

    # ---- meta
    out.append("  <meta>")
    for tag, val in (("title", rec.get("title")), ("subject", rec.get("subject"))):
        if val:
            out.append(f"    <{tag}>{escape(mask(val, do_mask))}</{tag}>")
    originator = None
    for sec in rec.get("sections", []):
        m = ORIG_RX.search(sec.get("text", ""))
        if m:
            originator = m.group(1).strip()
            break
    if originator:
        out.append(f"    <originator>{escape(originator)}</originator>")
    if iso_date(dates.get("signed")):
        out.append(f"    <signedDate>{dates['signed']}</signedDate>")
    if iso_date(dates.get("cancelled")):
        out.append(f"    <cancelledDate>{dates['cancelled']}</cancelledDate>")
    if pub.get("distribution_statement"):
        out.append("    <distributionStatement>"
                   f"{escape(pub['distribution_statement'].strip())}"
                   "</distributionStatement>")
    out.append(
        "    <provenance"
        + attr("sourcePath", prov.get("source_path"))
        + attr("sourceHash", prov.get("source_hash"))
        + attr("extractionEngine", prov.get("extraction_engine"))
        + attr("convertedAt", prov.get("converted_at"))
        + attr("storeSchemaVersion", rec.get("schema_version"))
        + "/>")
    out.append("  </meta>")

    # ---- authority
    edges = rec.get("relationships", {}).get("edge_meta") or []
    if edges:
        out.append("  <authority>")
        for m in edges:
            res = m.get("resolution") or ""
            tier = TIER_RX.search(res)
            holds = HOLDS_RX.search(res)
            src = SRC_RX.search(res)
            uslm = re.search(r"uslm=(/us/[^;]+)", res)
            out.append(
                "    <ref"
                + attr("rel", m.get("rel"))
                + attr("target", m.get("target"))
                + attr("targetIdentifier", uslm.group(1) if uslm else None)
                + attr("basis", m.get("basis") or "cited")
                + attr("tier", tier.group(1) if tier else None)
                + attr("held", CONFIDENCE_TO_HELD.get(m.get("confidence")))
                + attr("storeHolds", holds.group(1) if holds else None)
                + attr("from", src.group(1).strip() if src else None)
                + "/>")
        out.append("  </authority>")

    # ---- body
    for sec in rec.get("sections", []):
        provisions = sec.get("provisions") or []
        out.append(
            "  <section"
            + attr("anchor", sec.get("anchor"))
            + attr("identifier", sec.get("uslm_identifier"))
            + attr("heading", sec.get("heading"))
            + attr("verification", sec.get("verification") or "UNVERIFIED")
            + ">")
        roots, children = nest(provisions)
        for p in roots:
            provision_xml(p, children, 4, do_mask, out)
        out.append("  </section>")

    # ---- corrections
    corrections = rec.get("corrections") or []
    if corrections:
        out.append("  <corrections>")
        for c in corrections:
            out.append("    <correction"
                       + attr("date", c.get("date"))
                       + attr("against", c.get("against"))
                       + ">")
            for ch in c.get("changes") or []:
                out.append(f"      <change>{escape(str(ch))}</change>")
            out.append("    </correction>")
        out.append("  </corrections>")

    out.append("</issuance>")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical_staging")
    ap.add_argument("--out", default="issuance_export")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-mask", action="store_true")
    ap.add_argument("--validate", action="store_true",
                    help="validate every output against schema/usmc-issuance-2.0.xsd")
    ap.add_argument("--schema", default="schema/usmc-issuance-2.0.xsd")
    args = ap.parse_args()

    global MASK_ATTRS
    MASK_ATTRS = not args.no_mask

    names = sorted(f for f in os.listdir(args.src) if f.endswith(".json"))
    if args.only:
        names = [f for f in names if f[:-5] in set(args.only)]
    os.makedirs(args.out, exist_ok=True)

    validator = None
    if args.validate:
        from lxml import etree
        with open(args.schema, "rb") as fh:
            validator = etree.XMLSchema(etree.parse(fh))

    written = skipped = failed = 0
    provisions = citations = auth_edges = 0
    for name in names:
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        if not rec.get("publication", {}).get("publishable", True):
            skipped += 1
            print(f"  QUARANTINED, not exported: {rec['id']}")
            continue
        xml = to_xml(rec, not args.no_mask)
        path = os.path.join(args.out, f"{rec['id']}.issuance.xml")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(xml)
        written += 1
        for sec in rec.get("sections", []):
            for p in sec.get("provisions") or []:
                provisions += 1
                citations += len(p.get("citations") or [])
        auth_edges += len(rec.get("relationships", {}).get("edge_meta") or [])
        if validator is not None:
            from lxml import etree
            try:
                validator.assertValid(etree.parse(path))
            except etree.DocumentInvalid as exc:
                failed += 1
                print(f"  INVALID {rec['id']}: {str(exc)[:180]}")

    print(f"\nwritten     {written}")
    print(f"quarantined {skipped}")
    print(f"provisions  {provisions}")
    print(f"citations   {citations}")
    print(f"authority   {auth_edges}")
    if validator is not None:
        print(f"schema      {'ALL VALID' if not failed else str(failed) + ' INVALID'}"
              f"  ({args.schema})")
    print(f"out         {args.out}")


if __name__ == "__main__":
    main()
