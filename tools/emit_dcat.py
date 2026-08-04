"""Emit the corpus as a DCAT-US 3.0 catalog record.

WHY

OMB M-25-05, "Phase 2 Implementation of the Foundations for Evidence-Based
Policymaking Act of 2018," 15 January 2025, rescinded and replaced M-13-13
and states:

    The OMB-approved standard metadata schema will conform to the United
    States profile of the W3C Data Catalog Vocabulary Version 3, known as
    the DCAT-US 3.0.

Its compliance table sets 30 September 2026 for agency inventories to be
updated to DCAT-US 3.0 and hosted at www.[agency].gov/data.json. Publishing
this file is what makes the corpus harvestable by data.gov, which reads the
source verbatim and corrects nothing.

WHAT THIS DOES NOT CLAIM

This is a catalog record for an UNOFFICIAL reference corpus. It is not an
agency data inventory, and emitting it does not make anyone compliant with
M-25-05. It exists so the packaging is right the day an issuing authority
wants to adopt it, and so the shape can be validated now rather than
discovered later.

Two DCAT-US 3.0 notes that bite:
- the schema moved from JSON Schema Draft-04 to 2020-12, so old validators
  give false passes
- accessLevel is not a v3.0 core field; accessRights carries that meaning.
  Both are emitted, because data.gov harvests 1.1 and 3.0 side by side
  during the transition.
"""

import argparse
import json
import os
from collections import Counter
from datetime import datetime, timezone

SCHEMA = ("https://raw.githubusercontent.com/GSA/dcat-us/main/schemas/"
          "dataset.json")


def build(store, base_url, publisher, contact_name, contact_email):
    recs, types, statuses, oldest, newest = [], Counter(), Counter(), None, None
    for name in sorted(os.listdir(store)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(store, name), encoding="utf-8") as fh:
            r = json.load(fh)
        if not r.get("publication", {}).get("publishable", True):
            continue          # the quarantine gate holds in every output
        recs.append(r)
        types[r.get("doc_type")] += 1
        statuses[r.get("status")] += 1
        signed = (r.get("dates") or {}).get("signed")
        if signed:
            oldest = signed if not oldest or signed < oldest else oldest
            newest = signed if not newest or signed > newest else newest

    now = datetime.now(timezone.utc).isoformat()
    today = now[:10]
    type_list = ", ".join(f"{k} ({v})" for k, v in types.most_common())

    dataset = {
        "@type": "dcat:Dataset",
        "identifier": f"{base_url}/dataset/marine-corps-policy-as-data",
        "title": "Marine Corps policy as data - canonical issuance corpus",
        "description": (
            "Marine Corps and Department of the Navy policy issuances recast as "
            "structured data. Each record carries a stable identifier, a "
            "paragraph-level provision tree with citation anchors, publication "
            "status with supersession and cancellation chains, cited authority "
            "edges to the issuances above it, and full extraction provenance. "
            f"Covers {len(recs)} document(s): {type_list}. "
            "Every record is a machine extraction marked UNVERIFIED until a "
            "human confirms it line by line against the authoritative source. "
            "Records marked cancelled or superseded are retained and labelled "
            "rather than removed. This is an unofficial reference compiled from "
            "public documents; the issuing authority's copy governs."),
        "keyword": ["policy", "directives", "Marine Corps", "Department of the Navy",
                    "military personnel", "issuances", "USLM", "policy as data",
                    "authority chain", "supersession"],
        "issued": today,
        "modified": today,
        "publisher": {"@type": "org:Organization", "name": publisher},
        "contactPoint": {"@type": "vcard:Contact",
                         "fn": contact_name,
                         "hasEmail": f"mailto:{contact_email}"},
        "accessRights": "public",
        "accessLevel": "public",          # DCAT-US 1.1 field, kept for the
                                          # transition window
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "spatial": "United States",
        "temporal": f"{oldest or '2001-01-01'}/{newest or today}",
        "accrualPeriodicity": "R/P1D",
        "language": ["en-US"],
        "theme": ["government"],
        "describedBy": f"{base_url}/schema/policy_document.schema.json",
        "describedByType": "application/schema+json",
        "distribution": [
            {"@type": "dcat:Distribution",
             "title": "Canonical records (JSON)",
             "description": ("One JSON record per issuance, validating against "
                             "policy_document.schema.json 0.5.0."),
             "downloadURL": f"{base_url}/canonical.zip",
             "mediaType": "application/zip",
             "format": "JSON"},
            {"@type": "dcat:Distribution",
             "title": "Issuance XML export",
             "description": ("Per-document XML in the usmc-issuance namespace, "
                             "built on United States Legislative Markup "
                             "conventions and extended to service issuances."),
             "downloadURL": f"{base_url}/uslm_export.zip",
             "mediaType": "application/zip",
             "format": "XML"},
            {"@type": "dcat:Distribution",
             "title": "Authority graph (JSON-LD)",
             "description": ("Cited authority edges between issuances, each "
                             "carrying its basis and the paragraph it was read "
                             "from."),
             "downloadURL": f"{base_url}/authority.jsonld",
             "mediaType": "application/ld+json",
             "format": "JSON-LD"},
            {"@type": "dcat:Distribution",
             "title": "Public library",
             "description": "Rendered, Section 508 targeted HTML.",
             "accessURL": base_url,
             "mediaType": "text/html",
             "format": "HTML"},
        ],
    }

    return {
        "@context": "https://resources.data.gov/vocab/dcat-us/v3/context.jsonld",
        "@type": "dcat:Catalog",
        "conformsTo": "https://resources.data.gov/vocab/dcat-us/v3/schema",
        "describedBy": SCHEMA,
        "dataset": [dataset],
    }, recs, types, statuses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="canonical_staging")
    ap.add_argument("--out", default="data.json")
    ap.add_argument("--base-url", default="https://example.invalid/policy")
    ap.add_argument("--publisher", default="Unofficial reference - publisher not asserted")
    ap.add_argument("--contact-name", default="Corpus owner")
    ap.add_argument("--contact-email", default="owner@example.invalid")
    args = ap.parse_args()

    catalog, recs, types, statuses = build(
        args.store, args.base_url.rstrip("/"), args.publisher,
        args.contact_name, args.contact_email)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=1, ensure_ascii=False)

    ds = catalog["dataset"][0]
    print(f"{args.out}: 1 dataset, {len(ds['distribution'])} distributions, "
          f"{len(recs)} publishable record(s)")
    print(f"  doc types  {dict(types)}")
    print(f"  statuses   {dict(statuses)}")
    print(f"  temporal   {ds['temporal']}")
    missing = [k for k in ("title", "description", "identifier", "publisher",
                           "contactPoint", "modified", "accessRights",
                           "distribution") if not ds.get(k)]
    print(f"  mandatory fields present: {'yes' if not missing else missing}")


if __name__ == "__main__":
    main()
