"""Citation grammar for naval reference lists - P3 authority extraction.

Turns one reference-list item into a typed, tiered, identified citation.
Written 2026-08-03 to close the measured gap: 26 cross-document citations
existed in a 615,114-provision corpus, and zero of them came from an MCO,
SECNAVINST, NAVMC, or MCBul, even though 200 MCOs and 75 SECNAVINSTs
already carried their governing authority in parsed text.

Discipline carried from the store's data contract:
- A citation is written only when the source text names the document.
  Nothing is inferred from subject matter, numbering proximity, or
  hierarchy. Unparseable items stay unparsed and keep their raw text.
- Tier is a property of the issuing level, not a guess about importance.
- in_store records whether the corpus actually holds the target. A named
  authority the corpus lacks is reported as a gap, never dropped and never
  quietly resolved to something else.
"""

import re

# Tier ladder. T6 (local SOP) is out of scope for this corpus.
TIERS = {
    "T0": "Statute",
    "T1": "Department of Defense",
    "T2": "Department of the Navy",
    "T3": "Service directive",
    "T4": "Service manual",
    "T5": "Message",
    "TX": "Other authority",
}

# Ordered. First match wins, so longer and more specific forms lead.
# Each entry: (doc_type, tier, regex, id_builder, uslm_builder)
_P = re.compile


def _clean(n):
    return n.strip().rstrip(",.;").replace(" ", "")


RULES = [
    # ---- T0 statute -------------------------------------------------
    # DoD issuances invert the order: "Section 701 of Title 10, U.S.C."
    # This form leads because the section number carries more resolving
    # power than the title, and reading it as a bare title citation is how
    # the parental-leave root was being lost.
    # "U.S. CODE TITLE 10 SECTION 10304" - the form naval messages use in
    # their NARR blocks, with the title before the section and no section
    # symbol anywhere.
    # "United States Code, Title 10" - the form a DoD reference list uses
    # when it cites a whole title and names no section. DoDI 1320.14 ends
    # its reference list with exactly this.
    ("USC_TITLE", "T0",
     _P(r"\bUnited\s+States\s+Code,?\s+Title\s+(\d{1,2})\b", re.I)),
    ("USC_INV2", "T0",
     _P(r"\bU\.?\s?S\.?\s?Code\s+Title\s+(\d{1,2})\s+Sections?\s+"
        r"(\d[\w.\-]*)", re.I)),
    ("USC_INV", "T0",
     _P(r"\bSections?\s+(\d[\w.\-]*(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+)\d[\w.\-]*)*)"
        r"(?:\([a-z0-9]+\))?\s+of\s+Title\s+(\d{1,2})\b[,]?\s*U\.?\s?S\.?\s?C",
        re.I)),
    ("USC", "T0",
     # The section symbol is optional. Reference lists write both
     # "10 U.S.C. 701" and "10 U.S.C. sec 701"; requiring the symbol
     # silently demoted every unsymbolled citation to a whole-title node.
     _P(r"\b(?:Title\s+)?(\d{1,2})[,]?\s*U\.?\s?S\.?\s?C(?:ode)?\.?"
        r"(?:\s*(?:§+|Sections?|Secs?\.?)?\s*(\d[\w.\-]*"
        r"(?:\s*(?:,\s*and\s+|,\s*|\s+and\s+)\d[\w.\-]*)*))?",
        re.I)),
    # ---- T1 DoD -----------------------------------------------------
    # Messages spell the issuer out in full: "THE DEPARTMENT OF DEFENSE
    # INSTRUCTION 1205.21 OF 20 SEP 1999".
    ("DODI", "T1",
     _P(r"\bDepartment\s+of\s+Defense\s+Instruction\s*"
        r"([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("DODD", "T1",
     _P(r"\bDepartment\s+of\s+Defense\s+Directive\s*"
        r"([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("DODI", "T1",
     _P(r"\bDoD\s*I(?:NST|nstruction)?\.?\s*([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("DODD", "T1",
     _P(r"\bDoD\s*D(?:IR|irective)?\.?\s*([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("DODM", "T1",
     _P(r"\bDoD\s*M(?:anual)?\.?\s*([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("DTM", "T1", _P(r"\bDTM[- ]([0-9]{2}-[0-9]{3})", re.I)),
    ("DODFMR", "T1",
     _P(r"\bDOD\s*7000\.14-?R\b.*?(?:Volume\s*([0-9]{1,2}[A-Z]?))?", re.I)),
    ("DODREG", "T1", _P(r"\bDOD\s*([0-9]{4}\.[0-9]{1,2}-R)\b", re.I)),
    ("EO", "TX", _P(r"\bE(?:xecutive\s+Order|\.?O\.?)\s*\(?E?\.?O?\.?\)?\s*"
                    r"([0-9]{5})", re.I)),
    # ---- T2 Department of the Navy ----------------------------------
    ("SECNAVINST", "T2",
     _P(r"\bSECNAV\s*INST(?:RUCTION)?\.?\s*([0-9]{4,5}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("SECNAVM", "T2", _P(r"\bSECNAV\s*M-?\s*([0-9]{4,5}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("OPNAVINST", "T2",
     _P(r"\bOPNAV\s*INST(?:RUCTION)?\.?\s*([0-9]{4,5}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("NAVSO", "T2", _P(r"\bNAVSO\s*P-?\s*([0-9]{4,5})", re.I)),
    ("BUMEDINST", "T2",
     _P(r"\bBUMED\s*INST(?:RUCTION)?\.?\s*([0-9]{4,5}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("SECNAVNOTE", "T2",
     _P(r"\bSECNAV\s*Not(?:ice|e)\.?\s*([0-9]{4,5}(?:\.[0-9]{1,3})?)", re.I)),
    ("CJCSI", "T1",
     _P(r"\bCJCS\s*I(?:NST|nstruction)?\.?\s*([0-9]{4}\.[0-9]{1,3}[A-Z]?)", re.I)),
    # ---- T3 service directive ---------------------------------------
    ("MCO", "T3",
     _P(r"\b(?:MCO|Marine\s+Corps\s+Order)\s*P?\s*"
        r"([0-9]{4,5}[A-Z]?\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("MCBUL", "T3",
     _P(r"\b(?:MCBul|Marine\s+Corps\s+Bulletin)\.?\s*([0-9]{4,5}(?:\.[0-9]{1,3})?)",
        re.I)),
    # ---- T4 service manual ------------------------------------------
    ("NAVMC", "T4",
     _P(r"\bNAVMC\s*(?:DIR\s*)?([0-9]{4,5}\.[0-9]{1,3}[A-Z]?)", re.I)),
    ("MCRP", "T4", _P(r"\bMCRP\s*([0-9][0-9A-Z.\-]*)", re.I)),
    ("MCTP", "T4", _P(r"\bMCTP\s*([0-9][0-9A-Z.\-]*)", re.I)),
    ("MCWP", "T4", _P(r"\bMCWP\s*([0-9][0-9A-Z.\-]*)", re.I)),
    ("MCDP", "T4", _P(r"\bMCDP\s*([0-9][0-9A-Z.\-]*)", re.I)),
    # ---- T5 message --------------------------------------------------
    ("MARADMIN", "T5", _P(r"\bMARADMIN\s*([0-9]{1,3})\s*/\s*([0-9]{2})", re.I)),
    ("ALMAR", "T5", _P(r"\bALMAR\s*([0-9]{1,3})\s*/\s*([0-9]{2})", re.I)),
    ("ALNAV", "T5", _P(r"\bALNAV\s*([0-9]{1,3})\s*/\s*([0-9]{2})", re.I)),
]

# Change and volume suffixes ride along with the base number.
CH_RX = re.compile(r"\b(?:W/?\s*)?CH[- ]?([0-9]{1,2})\b", re.I)
VOL_RX = re.compile(r"\bVol(?:ume)?\.?\s*([0-9]{1,2}[A-Z]?)\b", re.I)
SERIES_RX = re.compile(r"\bSeries\b", re.I)
DATE_RX = re.compile(
    r"\bof\s+((?:[0-9]{1,2}\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"[a-z]*\.?\s+[0-9]{2,4})", re.I)
TITLE_RX = re.compile(r"[“\"]([^”\"]{4,200})[”\"]")


def _msg_id(kind, num, yy):
    year = int(yy)
    year += 2000 if year <= 60 else 1900
    return f"{kind}-{year}-{int(num):03d}"


def classify(text: str):
    """One reference-list item -> a citation dict, or None.

    None means the text names no recognizable issuance. That is a real
    answer for items like a users manual referred to only by acronym, and
    the caller keeps the raw text rather than forcing a match.
    """
    t = " ".join((text or "").split())
    if not t:
        return None
    # Change and volume suffixes belong to the citation, not to a quoted
    # title. "NAVSO P-6034, 'Joint Federal Travel Regulations, Volume 1'"
    # names one document, not volume 1 of NAVSO P-6034.
    outside = TITLE_RX.sub(" ", t)
    for doc_type, tier, rx in RULES:
        m = rx.search(t)
        if not m:
            continue
        groups = [g for g in m.groups() if g]
        if doc_type in ("MARADMIN", "ALMAR", "ALNAV"):
            if len(m.groups()) < 2 or not m.group(2):
                continue
            did = _msg_id(doc_type, m.group(1), m.group(2))
            uslm = (f"/us/dod/don/usmc/{doc_type.lower()}/"
                    f"{did.split('-')[1]}/{did.split('-')[2]}")
            number = f"{int(m.group(1))}/{m.group(2)}"
        elif doc_type in ("USC", "USC_INV", "USC_INV2", "USC_TITLE"):
            if doc_type == "USC_TITLE":
                title, raw_secs = m.group(1), ""
                doc_type = "USC"
            elif doc_type == "USC_INV":
                title, raw_secs = m.group(2), m.group(1)
                doc_type = "USC"
            elif doc_type == "USC_INV2":
                title, raw_secs = m.group(1), m.group(2)
                doc_type = "USC"
            else:
                title, raw_secs = m.group(1), m.group(2) or ""
            secs = [_clean(s) for s in
                    re.split(r",|\band\b", raw_secs, flags=re.I)]
            secs = [s for s in secs if s]
            number = f"{title} U.S.C." + (" " + ", ".join(secs) if secs else "")
            did = f"USC-T{title}" + (f"-S{secs[0]}" if secs else "")
            uslm = f"/us/usc/t{title}" + (f"/s{secs[0].lower()}" if secs else "")
        elif doc_type == "DODFMR":
            vol = (m.group(1) or "")
            number = "DoD 7000.14-R" + (f" Volume {vol}" if vol else "")
            did = "DODFMR" + (f"-V{vol}" if vol else "")
            uslm = "/us/dod/fmr" + (f"/v{vol.lower()}" if vol else "")
        else:
            number = _clean(groups[0])
            did = f"{doc_type}-{number}"
            uslm = _uslm_for(doc_type, number)

        ch = CH_RX.search(outside)
        vol = VOL_RX.search(outside)
        if ch and doc_type not in ("USC", "DODFMR"):
            did += f"-CH{int(ch.group(1))}"
            uslm += f"/ch{int(ch.group(1))}"
        elif vol and doc_type not in ("USC", "DODFMR"):
            did += f"-V{vol.group(1).upper()}"
            uslm += f"/v{vol.group(1).lower()}"

        title_m = TITLE_RX.search(t)
        date_m = DATE_RX.search(t)
        return {
            "doc_type": doc_type,
            "tier": tier,
            "tier_name": TIERS[tier],
            "number": number,
            "doc_id": did.upper() if doc_type != "USC" else did,
            "uslm": uslm,
            "title": title_m.group(1).strip() if title_m else None,
            "cited_date": date_m.group(1) if date_m else None,
            "series": bool(SERIES_RX.search(t)),
            "text": t,
        }
    return None


def _uslm_for(doc_type, number):
    n = number.lower()
    root = {
        "DODI": f"/us/dod/dodi/{n}",
        "DODD": f"/us/dod/dodd/{n}",
        "DODM": f"/us/dod/dodm/{n}",
        "DTM": f"/us/dod/dtm/{n}",
        "DODREG": f"/us/dod/reg/{n}",
        "EO": f"/us/eop/eo/{n}",
        "SECNAVINST": f"/us/dod/don/secnavinst/{n}",
        "SECNAVM": f"/us/dod/don/secnavm/{n}",
        "OPNAVINST": f"/us/dod/don/opnavinst/{n}",
        "NAVSO": f"/us/dod/don/navso/{n}",
        "BUMEDINST": f"/us/dod/don/bumedinst/{n}",
        "SECNAVNOTE": f"/us/dod/don/secnavnote/{n}",
        "CJCSI": f"/us/dod/cjcs/cjcsi/{n}",
        "MCO": f"/us/dod/don/usmc/mco/{n}",
        "MCBUL": f"/us/dod/don/usmc/mcbul/{n}",
        "NAVMC": f"/us/dod/don/usmc/navmc/{n}",
        "MCRP": f"/us/dod/don/usmc/mcrp/{n}",
        "MCTP": f"/us/dod/don/usmc/mctp/{n}",
        "MCWP": f"/us/dod/don/usmc/mcwp/{n}",
        "MCDP": f"/us/dod/don/usmc/mcdp/{n}",
    }
    return root.get(doc_type, f"/us/dod/don/usmc/{doc_type.lower()}/{n}")
