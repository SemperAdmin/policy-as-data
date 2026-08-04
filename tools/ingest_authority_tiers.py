"""Mint the statute and DoD records a top-down chain terminates in.

The corpus holds nothing above the Department of the Navy. Every authority
chain therefore ran off the top of the store. These records close that for
the leave spine.

HONESTY POSTURE - read before extending this file.

These are METADATA-GRADE records. Identity, dates, supersession, reference
lists, and section headings are transcribed from the authoritative source
named in provenance.source_path. Section TEXT is not ingested, and no
provision text is invented. Every section carries an explicit note saying
so, and every record is UNVERIFIED. A metadata-grade record is enough to
terminate an authority chain, resolve a citation, and state currency. It is
not enough to answer a question about what the statute says, and the record
says that on its face rather than leaving a reader to assume otherwise.

Promotion to full text is a separate, later step that replaces the section
bodies from a retrieved source file.
"""

import argparse
import hashlib
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from atomicio import write_json  # noqa: E402
import os

# When the metadata table in this file was hand-entered. It is a fact about
# the entry, not about when the build last ran, so it is a literal rather than
# datetime.now(). Reading the clock here made this the one stage that could not
# run twice without changing the corpus: every build rewrote extracted_at and
# converted_at on the eleven top-tier records - the statute and DoD spine,
# exactly the records a reader checks for provenance - and a diff of two
# identical builds showed eleven changed files with no changed content.
#
# Bump this when the RECORDS table below is edited, and only then.
ENTERED = "2026-08-03T00:00:00+00:00"
NOW = ENTERED
TODAY = ENTERED[:10]
METADATA_NOTE = ("METADATA-GRADE - headings and identity transcribed from the "
                 "authoritative source; section text not ingested. Do not quote "
                 "this record as the words of the issuance.")


def section(anchor, heading, note=None, provisions=None):
    return {"anchor": anchor, "heading": heading,
            "text": note or METADATA_NOTE,
            "provisions": provisions or []}


def ref_provisions(items):
    """A reference list in the same shape the fixed parser emits."""
    out = [{"path": "ref", "number": "Ref:", "label": "Ref:", "depth": 0,
            "parent": None, "text": "", "raw_marker": "Ref:"}]
    letters = "abcdefghijklmnopqrstuvwxyz"
    for i, t in enumerate(items):
        v = letters[i] if i < 26 else f"z{i}"
        out.append({"path": f"ref/{v}", "number": f"({v})", "label": f"({v})",
                    "depth": 1, "parent": "ref", "text": t,
                    "raw_marker": f"({v})"})
    return out


def build(doc_id, doc_type, native, uslm, title, subject, status, signed,
          source_url, sections, relationships=None, notes=None):
    payload = json.dumps(sections, sort_keys=True).encode("utf-8")
    rec = {
        "schema_version": "0.5.0",
        "id": doc_id,
        "doc_type": doc_type,
        "native_number": native,
        "uslm_identifier": uslm,
        "verification": "UNVERIFIED",
        "corrections": [],
        "title": title,
        "subject": subject,
        "status": status,
        "dates": {"signed": signed, "effective": signed,
                  "cancelled": None, "archived": None},
        "issuing_authority": None,
        "relationships": relationships or {
            "cancels": [], "cancelled_by": [], "supersedes": [],
            "superseded_by": [], "references": [], "edge_meta": []},
        "publication": {"publishable": True, "reason": None,
                        "distribution_statement": None,
                        "adjudication_ref": None},
        "provenance": {
            "source_path": source_url,
            "source_hash": hashlib.sha256(payload).hexdigest(),
            "source_site": source_url.split("/")[2] if "//" in source_url else None,
            "extraction_engine": "manual-metadata-entry",
            "extracted_at": NOW, "cleaned_at": None, "converted_at": NOW},
        "pocs": [],
        "sections": sections,
        "conversion_notes": [f"ingest_authority_tiers.py {TODAY} - {METADATA_NOTE}"]
        + (notes or []),
    }
    return rec


# ---------------------------------------------------------------------------
# T0 - statute. Subsection headings from the Office of the Law Revision
# Counsel prelim text. Two subsections carry verbatim opening language
# because it is quoted directly in the source; the rest are headings only.
USC_701 = build(
    doc_id="USC-T10-S701",
    doc_type="USC",
    native="10 U.S.C. 701",
    uslm="/us/usc/t10/s701",
    title="10 U.S.C. 701 - Entitlement and accumulation",
    subject="ENTITLEMENT AND ACCUMULATION OF LEAVE",
    status="active",
    signed=None,
    source_url=("https://uscode.house.gov/view.xhtml?req=granuleid:"
                "USC-prelim-title10-section701&num=0&edition=prelim"),
    sections=[
        section("front-matter", "10 U.S.C. 701 - Entitlement and accumulation"),
        section(
            "subsections", "Subsections",
            note=METADATA_NOTE,
            provisions=[
                {"path": "a", "number": "(a)", "label": "(a)", "depth": 0,
                 "parent": None, "raw_marker": "(a)",
                 "text": ("Basic entitlement. “A member of an armed force is "
                          "entitled to leave at the rate of 2½ calendar days "
                          "for each month of active service, excluding periods "
                          "of-”")},
                {"path": "b", "number": "(b)", "label": "(b)", "depth": 0,
                 "parent": None, "raw_marker": "(b)",
                 "text": "Accumulation limits - 60-day cap on accumulated leave."},
                {"path": "e", "number": "(e)", "label": "(e)", "depth": 0,
                 "parent": None, "raw_marker": "(e)",
                 "text": ("Excess leave retention - Secretary may authorize "
                          "retention of up to 30 days excess leave.")},
                {"path": "h", "number": "(h)", "label": "(h)", "depth": 0,
                 "parent": None, "raw_marker": "(h)",
                 "text": ("Parental leave. “Under regulations prescribed by "
                          "the Secretary of Defense, a member of the armed forces "
                          "described in paragraph (2) is allowed up to a total of "
                          "12 weeks of parental leave during the one-year period "
                          "beginning after” specified events including birth, "
                          "adoption, and foster placement.")},
                {"path": "l", "number": "(l)", "label": "(l)", "depth": 0,
                 "parent": None, "raw_marker": "(l)",
                 "text": "Bereavement leave - two weeks for immediate family death."},
                {"path": "m", "number": "(m)", "label": "(m)", "depth": 0,
                 "parent": None, "raw_marker": "(m)",
                 "text": "Convalescent leave - medical provider recommended."},
            ]),
    ],
    notes=["Subsection (h) is the statutory root of the Military Parental "
           "Leave Program. Subsection (a) is the root of MCO 1050.3J."],
)

# ---------------------------------------------------------------------------
# T1 - DoD. The current edition, which absorbed the DTM that MARADMIN 051/23
# implements and superseded the 2009 edition MCO 1050.3J points at.
DODI_132706 = build(
    doc_id="DODI-1327.06",
    doc_type="DODI",
    native="1327.06",
    uslm="/us/dod/dodi/1327.06",
    title="DoD Instruction 1327.06 - Military Leave, Liberty, and Administrative Absence",
    subject="MILITARY LEAVE, LIBERTY, AND ADMINISTRATIVE ABSENCE",
    status="active",
    signed="2025-08-07",
    source_url=("https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/"
                "dodi/132706p.pdf"),
    sections=[
        section("front-matter",
                "DoD Instruction 1327.06, Military Leave, Liberty, and "
                "Administrative Absence, August 7, 2025",
                provisions=ref_provisions([
                    "Section 501 of Title 37, U.S.C.",
                    "Section 602 of Public Law 116-283",
                    "Section 603 of Title 37, U.S.C.",
                    "Section 604 of Public Law 116-283",
                    "Section 632 of Public Law 117-263",
                    "Section 701 of Title 10, U.S.C.",
                    "Section 703(a) of Title 10, U.S.C.",
                    "Section 704 of Title 10, U.S.C.",
                    "Section 709 of Title 10, U.S.C.",
                    "Section 711 of Title 10, U.S.C.",
                    "Section 876a of Title 10, U.S.C.",
                    "DoD Directive 5124.02",
                    "DoDI 1215.07",
                    "DoDI 1215.13",
                    "DoDI 1315.18",
                    "DoDI 1340.09",
                    "DoDI 1340.25",
                    "DoDI 1340.26",
                    "DoDI 4515.13",
                    "DoDI 6310.09",
                    "Chapter 35 of Volume 7A of DoD 7000.14-R",
                    "Chapter 44 of Volume 7A of DoD 7000.14-R",
                ])),
        section("s-1", "SECTION 1: GENERAL ISSUANCE INFORMATION"),
        section("s-2", "SECTION 2: RESPONSIBILITIES"),
        section("s-3", "SECTION 3: LEAVE PROCEDURES", provisions=[
            {"path": "p3/11", "number": "3.11.", "label": "3.11.", "depth": 1,
             "parent": "p3", "raw_marker": "3.11.",
             "text": "NON-CHARGEABLE LEAVE"},
            {"path": "p3/11/b", "number": "3.11.b.", "label": "b.", "depth": 2,
             "parent": "p3/11", "raw_marker": "b.",
             "text": "Reserve Component Maternity Leave"},
            {"path": "p3/11/c", "number": "3.11.c.", "label": "c.", "depth": 2,
             "parent": "p3/11", "raw_marker": "c.",
             "text": "Active Duty Parental Leave (ADPL)"},
            {"path": "p3/11/d", "number": "3.11.d.", "label": "d.", "depth": 2,
             "parent": "p3/11", "raw_marker": "d.",
             "text": "Inactive Duty Parental Leave (IDPL)"},
        ]),
        section("s-4", "SECTION 4: AUTHORIZED ABSENCES OTHER THAN LEAVE"),
        section("s-5", "SECTION 5: ADMINISTRATIVE REQUIREMENTS"),
        section("s-6", "SECTION 6: FEML PROGRAM DATA SHEET"),
        section("glossary", "GLOSSARY"),
    ],
    relationships={
        "cancels": ["DTM-22-004", "DTM-23-001", "DTM-23-003"],
        "cancelled_by": [], "supersedes": ["DODI-1327.6"],
        "superseded_by": [], "references": [],
        "edge_meta": [
            {"rel": "cancels", "target": "DTM-23-001", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; incorporates and cancels DTM 23-001, "
                           "Expansion of the Military Parental Leave Program, "
                           "January 4, 2023, as amended"},
            {"rel": "cancels", "target": "DTM-22-004", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; Reserve Component Maternity Leave "
                           "Program, June 9, 2022, as amended"},
            {"rel": "cancels", "target": "DTM-23-003", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; Bereavement Leave for Service Members, "
                           "March 29, 2023, as amended"},
            {"rel": "supersedes", "target": "DODI-1327.6", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; supersedes DoDI 1327.06, Leave and "
                           "Liberty Policy and Procedures, June 16, 2009, as amended"},
        ]},
    notes=["CURRENCY: this edition absorbed DTM 23-001, the memorandum "
           "MARADMIN 051/23 implements, and superseded the 2009 edition. "
           "MCO 1050.3J cites 'DODI 1327.6' of April 22, 2005 - two editions "
           "behind. That drift is the point of the chain, not a defect in it."],
)

# The edition MCO 1050.3J actually names, held so the citation resolves to
# the document the text points at rather than to its replacement.
DODI_132706_2009 = build(
    doc_id="DODI-1327.6",
    doc_type="DODI",
    native="1327.6",
    uslm="/us/dod/dodi/1327.6",
    title="DoD Instruction 1327.06 - Leave and Liberty Policy and Procedures",
    subject="LEAVE AND LIBERTY POLICY AND PROCEDURES",
    status="superseded",
    signed="2009-06-16",
    source_url="https://www.usff.navy.mil/Portals/36/132706p.pdf",
    sections=[section("front-matter",
                      "DoD Instruction 1327.06, Leave and Liberty Policy and "
                      "Procedures, June 16, 2009, incorporating Change 3")],
    relationships={
        "cancels": [], "cancelled_by": [], "supersedes": [],
        "superseded_by": ["DODI-1327.06"], "references": [],
        "edge_meta": [{"rel": "superseded_by", "target": "DODI-1327.06",
                       "basis": "cited", "confidence": "high",
                       "resolution": "the 2025 edition states it supersedes "
                                     "this issuance"}]},
    notes=["This is the edition MCO 1050.3J names in its reference list, "
           "under the older 1327.6 number. Held so the cited edge resolves "
           "to the document the source text points at."],
)


# ---------------------------------------------------------------------------
# T0 - the titles cited as a whole. Several directives cite "Title 10, U.S.
# Code" with no section at all. That is a real citation to a real thing, so
# it gets a real node. The record says on its face that the citing document
# named no section, rather than inviting a reader to assume one.
def _title_record(num, name, url):
    return build(
        doc_id=f"USC-T{num}",
        doc_type="USC",
        native=f"{num} U.S.C.",
        uslm=f"/us/usc/t{num}",
        title=f"Title {num}, United States Code - {name}",
        subject=name.upper(),
        status="active",
        signed=None,
        source_url=url,
        sections=[section("front-matter", f"Title {num}, United States Code")],
        notes=["TITLE-LEVEL NODE. Directives citing this record name the title "
               "as a whole and no section. The citation resolves no further "
               "because the source text goes no further."],
    )


USC_T10 = _title_record(
    10, "Armed Forces",
    "https://uscode.house.gov/browse/prelim@title10&edition=prelim")
USC_T5 = _title_record(
    5, "Government Organization and Employees",
    "https://uscode.house.gov/browse/prelim@title5&edition=prelim")

# 10 U.S.C. 574 - named first in SECNAVINST 1400.1D reference (a),
# "10 U.S.C. sections 574, 621, and 649a". Worth reading the heading before
# using this node: the section governs the WARRANT OFFICER active-duty list.
# The commissioned-officer analogue is sections 621 to 623. The edge points
# here because 574 is the section the source names first, not because it is
# the better fit.
USC_574 = build(
    doc_id="USC-T10-S574",
    doc_type="USC",
    native="10 U.S.C. 574",
    uslm="/us/usc/t10/s574",
    title=("10 U.S.C. 574 - Warrant officer active-duty lists; competitive "
           "categories; number to be recommended for promotion; promotion zones"),
    subject=("WARRANT OFFICER ACTIVE-DUTY LISTS; COMPETITIVE CATEGORIES; "
             "NUMBER TO BE RECOMMENDED FOR PROMOTION; PROMOTION ZONES"),
    status="active",
    signed=None,
    source_url=("https://uscode.house.gov/view.xhtml?req=granuleid%3A"
                "USC-prelim-title10-section574&num=0&edition=prelim"),
    sections=[
        section("front-matter", "10 U.S.C. 574"),
        section("subsections", "Subsections (a) through (e)",
                note=(METADATA_NOTE + " Subsections (a) through (e) carry no "
                      "printed captions in the source.")),
    ],
    notes=["SCOPE: warrant officer active-duty list. Not the commissioned "
           "officer provision. SECNAVINST 1400.1D names this section first in "
           "a list that also names 621 and 649a."],
)

USC_552A = build(
    doc_id="USC-T5-S552a",
    doc_type="USC",
    native="5 U.S.C. 552a",
    uslm="/us/usc/t5/s552a",
    title="5 U.S.C. 552a - Records maintained on individuals",
    subject="RECORDS MAINTAINED ON INDIVIDUALS",
    status="active",
    signed=None,
    source_url=("https://uscode.house.gov/view.xhtml?req=granuleid:"
                "USC-prelim-title5-section552a&num=0&edition=prelim"),
    sections=[
        section("front-matter", "5 U.S.C. 552a - Records maintained on individuals"),
        section("subsections", "Subsections", provisions=[
            {"path": p, "number": f"({p})", "label": f"({p})", "depth": 0,
             "parent": None, "raw_marker": f"({p})", "text": t}
            for p, t in [
                ("a", "Definitions"), ("b", "Conditions of Disclosure"),
                ("c", "Accounting of Certain Disclosures"),
                ("d", "Access to Records"), ("e", "Agency Requirements"),
                ("f", "Agency Rules"), ("g", "Civil Remedies"),
                ("j", "General Exemptions"), ("k", "Specific Exemptions"),
            ]]),
    ],
    notes=["Popular name is the Privacy Act of 1974, Public Law 93-579. The "
           "printed section heading is 'Records maintained on individuals' - "
           "the words 'Privacy Act' do not appear in it."],
)

# ---------------------------------------------------------------------------
# T1 - promotion spine.
DODI_132014 = build(
    doc_id="DODI-1320.14",
    doc_type="DODI",
    native="1320.14",
    uslm="/us/dod/dodi/1320.14",
    title="DoD Instruction 1320.14 - DoD Commissioned Officer Promotion Program Procedures",
    subject="DOD COMMISSIONED OFFICER PROMOTION PROGRAM PROCEDURES",
    status="active",
    signed="2020-12-16",
    source_url="https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/132014p.pdf",
    sections=[
        section("front-matter",
                "DoD Instruction 1320.14, DoD Commissioned Officer Promotion "
                "Program Procedures, December 16, 2020",
                provisions=ref_provisions([
                    "Chairman of the Joint Chiefs of Staff Instruction 1330.05A, "
                    "\u201cJoint Officer Management Program Procedures,\u201d December 15, 2015",
                    "Chairman of the Joint Chiefs of Staff Instruction 1331.01D, "
                    "\u201cManpower and Personnel Actions Involving General and Flag "
                    "Officers,\u201d August 1, 2010",
                    "DoD Directive 5124.02, \u201cUnder Secretary of Defense for "
                    "Personnel and Readiness (USD(P&R)),\u201d June 23, 2008",
                    "DoD Instruction 1300.19, \u201cDoD Joint Officer Management (JOM) "
                    "Program,\u201d April 3, 2018",
                    "DoD Instruction 1310.02, \u201cOriginal Appointment of Officers,\u201d "
                    "March 26, 2015",
                    "DoD Instruction 1320.04, \u201cMilitary Officer Actions Requiring "
                    "Presidential, Secretary of Defense, or Under Secretary of Defense "
                    "for Personnel and Readiness Approval or Senate Confirmation,\u201d "
                    "January 3, 2014, as amended",
                    "DoD Instruction 1320.13, \u201cCommissioned Officer Promotion "
                    "Reports (COPRs),\u201d October 30, 2014",
                    "DoD Instruction 1327.07, \u201cCareer Intermission Program (CIP) for "
                    "Service Members,\u201d October 18, 2018",
                    "DoD Instruction 1334.02, \u201cFrocking of Commissioned Officers,\u201d "
                    "December 7, 2012, as amended",
                    "United States Code, Title 10",
                ])),
        section("s-1", "SECTION 1: GENERAL ISSUANCE INFORMATION"),
        section("s-2", "SECTION 2: RESPONSIBILITIES"),
        section("s-3", "SECTION 3: PROCEDURES"),
        section("s-4", "SECTION 4: ALTERNATIVE PROMOTION AUTHORITY"),
        section("glossary", "GLOSSARY"),
    ],
    relationships={
        "cancels": ["DODI-1320.11"], "cancelled_by": [],
        "supersedes": ["DODI-1320.14-2013"], "superseded_by": [],
        "references": [],
        "edge_meta": [
            {"rel": "cancels", "target": "DODI-1320.11", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; incorporates and cancels DoD "
                           "Instruction 1320.11, Special Selection Boards, "
                           "February 12, 2013"},
            {"rel": "supersedes", "target": "DODI-1320.14-2013", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; reissues and cancels DoD Instruction "
                           "1320.14, Commissioned Officer Promotion Program "
                           "Procedures, December 11, 2013, as amended"},
        ]},
    notes=["Its reference list cites United States Code, Title 10 as a whole. "
           "No section-level statutory citation appears in it, so the chain "
           "resolves to the title node and stops there."],
)

DODI_130019 = build(
    doc_id="DODI-1300.19",
    doc_type="DODI",
    native="1300.19",
    uslm="/us/dod/dodi/1300.19",
    title="DoD Instruction 1300.19 - DoD Joint Officer Management Program",
    subject="DOD JOINT OFFICER MANAGEMENT PROGRAM",
    status="active",
    signed="2018-04-03",
    source_url="https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/130019p.pdf",
    sections=[
        section("front-matter",
                "DoD Instruction 1300.19, DoD Joint Officer Management Program, "
                "April 3, 2018, incorporating Change 1, May 18, 2023"),
    ] + [section(f"s-{i}", h) for i, h in enumerate([
        "SECTION 1: GENERAL ISSUANCE INFORMATION",
        "SECTION 2: RESPONSIBILITIES",
        "SECTION 3: JOINT QUALIFICATIONS",
        "SECTION 4: JDAS AND THE JDAL",
        "SECTION 5: JDA CREDIT",
        "SECTION 6: JOINT EXPERIENCE, TRAINING, AND EDUCATION",
        "SECTION 7: JDA TOUR LENGTH REQUIREMENTS AND EARLY RELEASES",
        "SECTION 8: DESIGNATING LEVEL III JQOS",
        "SECTION 9: PROMOTION SELECTION BOARDS FOR ADL AND RASL",
        "SECTION 10: GO/FO PROVISIONS",
        "SECTION 11: REPORT REQUIREMENTS",
        "SECTION 12: RC OFFICER PROVISIONS",
        "GLOSSARY",
    ], start=1)],
    relationships={
        "cancels": [], "cancelled_by": [],
        "supersedes": ["DODI-1300.19-2014"], "superseded_by": [],
        "references": [],
        "edge_meta": [
            {"rel": "supersedes", "target": "DODI-1300.19-2014", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; reissues and cancels DoD Instruction "
                           "1300.19, DoD Joint Officer Management (JOM) Program, "
                           "March 4, 2014"},
        ]},
    notes=["REFERENCE LIST NOT INGESTED. The printed reference list sits after "
           "the glossary and could not be retrieved from the authoritative "
           "source. No reference edges are asserted from this record. An "
           "earlier partial read produced a plausible list of Title 10 "
           "sections assembled from in-body citations rather than the printed "
           "page; it was discarded rather than recorded as cited."],
)

# ---------------------------------------------------------------------------
# T1 - fitness spine. The same two-edition shape as leave: the orders name
# the 2002 number, and a 2022 reissue under a zero-padded number replaced it.
DODI_130803 = build(
    doc_id="DODI-1308.03",
    doc_type="DODI",
    native="1308.03",
    uslm="/us/dod/dodi/1308.03",
    title="DoD Instruction 1308.03 - DoD Physical Fitness/Body Composition Program",
    subject="DOD PHYSICAL FITNESS/BODY COMPOSITION PROGRAM",
    status="active",
    signed="2022-03-10",
    source_url="https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodi/130803p.pdf",
    sections=[
        section("front-matter",
                "DoD Instruction 1308.03, DoD Physical Fitness/Body Composition "
                "Program, March 10, 2022, incorporating Change 1, June 25, 2025",
                provisions=ref_provisions([
                    "DoD 5400.11-R, \u201cDepartment of Defense Privacy Program,\u201d "
                    "May 14, 2007",
                    "DoD Directive 5124.02, \u201cUnder Secretary of Defense for "
                    "Personnel and Readiness (USD(P&R)),\u201d June 23, 2008",
                    "DoD Directive 5136.01, \u201cAssistant Secretary of Defense for "
                    "Health Affairs (ASD(HA)),\u201d September 30, 2013, as amended",
                    "DoD Instruction 5400.11, \u201cDoD Privacy and Civil Liberties "
                    "Program,\u201d January 29, 2019, as amended",
                    "DoD Instruction 6130.03, Volume 1, \u201cMedical Standards for "
                    "Military Service: Appointment, Enlistment, or Induction,\u201d "
                    "May 6, 2018, as amended",
                    "DoD Manual 8910.01, Volume 1, \u201cDoD Information Collections "
                    "Manual: Procedures for DoD Internal Information Collections,\u201d "
                    "June 30, 2014, as amended",
                    "Executive Order 14183, \u201cPrioritizing Military Excellence and "
                    "Readiness,\u201d January 27, 2025",
                ])),
        section("s-1", "SECTION 1: GENERAL ISSUANCE INFORMATION"),
        section("s-2", "SECTION 2: RESPONSIBILITIES"),
        section("s-3", "SECTION 3: PROCEDURES", provisions=[
            {"path": "p3/1", "number": "3.1.", "label": "3.1.", "depth": 1,
             "parent": "p3", "raw_marker": "3.1.", "text": "Physical Fitness"},
            {"path": "p3/2", "number": "3.2.", "label": "3.2.", "depth": 1,
             "parent": "p3", "raw_marker": "3.2.", "text": "Evaluation"},
            {"path": "p3/3", "number": "3.3.", "label": "3.3.", "depth": 1,
             "parent": "p3", "raw_marker": "3.3.", "text": "MSK Injury Reporting"},
            {"path": "p3/4", "number": "3.4.", "label": "3.4.", "depth": 1,
             "parent": "p3", "raw_marker": "3.4.",
             "text": "Annual Military Service PF/BC Report"},
        ]),
        section("glossary", "GLOSSARY"),
    ],
    relationships={
        "cancels": ["DODD-1308.1", "DODD-1308.2"], "cancelled_by": [],
        "supersedes": ["DODI-1308.3"], "superseded_by": [], "references": [],
        "edge_meta": [
            {"rel": "supersedes", "target": "DODI-1308.3", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; reissues and cancels DoD Instruction "
                           "1308.3, DoD Physical Fitness and Body Fat Programs "
                           "Procedures, November 5, 2002"},
            {"rel": "cancels", "target": "DODD-1308.1", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; incorporates and cancels DoD Directive "
                           "1308.1, DoD Physical Fitness and Body Fat Program, "
                           "June 30, 2004"},
            {"rel": "cancels", "target": "DODD-1308.2", "basis": "cited",
             "confidence": "high",
             "resolution": "front-matter; incorporates and cancels DoD Directive "
                           "1308.2, Joint DoD Committee on Fitness, "
                           "February 4, 2005"},
        ]},
    notes=["Its reference list carries no statutory citation - seven entries, "
           "all DoD issuances plus Executive Order 14183. The fitness chain "
           "therefore terminates at the Department of Defense, and the page "
           "states that rather than reaching for a statute the text never names."],
)

DODI_13083_2002 = build(
    doc_id="DODI-1308.3",
    doc_type="DODI",
    native="1308.3",
    uslm="/us/dod/dodi/1308.3",
    title=("DoD Instruction 1308.3 - DoD Physical Fitness and Body Fat "
           "Programs Procedures"),
    subject="DOD PHYSICAL FITNESS AND BODY FAT PROGRAMS PROCEDURES",
    status="cancelled",
    signed="2002-11-05",
    source_url="https://www.esd.whs.mil/portals/54/documents/dd/issuances/dodi/130803p.pdf",
    sections=[section("front-matter",
                      "DoD Instruction 1308.3, DoD Physical Fitness and Body "
                      "Fat Programs Procedures, November 5, 2002")],
    relationships={
        "cancels": [], "cancelled_by": ["DODI-1308.03"], "supersedes": [],
        "superseded_by": ["DODI-1308.03"], "references": [],
        "edge_meta": [{"rel": "superseded_by", "target": "DODI-1308.03",
                       "basis": "cited", "confidence": "high",
                       "resolution": "the 2022 reissue states it reissues and "
                                     "cancels this issuance"}]},
    notes=["This is the edition MCO 6100.13A, MCO 6100.14, and MCO 6110.3A all "
           "name. It was cancelled in 2022. Three current Marine Corps orders "
           "cite a DoD instruction that has not existed for four years, and the "
           "chain shows it."],
)

RECORDS = [USC_701, DODI_132706, DODI_132706_2009,
           USC_T10, USC_T5, USC_574, USC_552A,
           DODI_132014, DODI_130019,
           DODI_130803, DODI_13083_2002]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="canonical_staging")
    ap.add_argument("--schema", default="schema/policy_document.schema.json")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    try:
        import jsonschema
        schema = json.load(open(args.schema, encoding="utf-8"))
    except Exception as exc:                      # noqa: BLE001
        schema, jsonschema = None, None
        print(f"schema check skipped: {exc}")

    for rec in RECORDS:
        if schema:
            jsonschema.validate(rec, schema)
        path = os.path.join(args.out, f"{rec['id']}.json")
        write_json(path, rec)
        print(f"{rec['id']:22} {rec['doc_type']:6} {rec['status']:11} "
              f"{rec['uslm_identifier']}")


if __name__ == "__main__":
    main()
