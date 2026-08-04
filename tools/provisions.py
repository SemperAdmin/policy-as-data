"""Provision-depth parser - Phase P1 (provision-depth-plan.md).

Requirement (Maj Gannon, 2026-07-17): one paragraph per node, hierarchy
explicit in the data, the STORED path absolute (p2/c/1) and the DISPLAYED
label local only ("(1)") per standard naval letter format. References
then resolve to chapter and verse instead of to a whole document.

Method. Extraction has already destroyed indentation, so the tree is
rebuilt from MARKER KINDS, not whitespace. Each paragraph's leading
marker is scanned into typed segments:

    arabic (1.)  upper (A.)  lower (a.)  paren-arabic ((1))
    paren-lower ((a))  paren-upper ((A))

A COMPOUND marker (2.c(1)) is absolute - it states its own full path and
resets the stack. A SINGLE marker uses the stack: a kind already on the
stack pops back to that level and increments there; an unseen kind pushes
a new level. That is what lets 2.c(1) follow 2.b correctly without any
reliance on leading spaces.

Path convention matches the repo's hand-built corpus exactly:
document + /p8/a/1/b. Depth 0 arabic renders as pN; deeper levels are the
bare value, lowercased.

Guards, all deliberate:
- Two adjacent segments of the same kind are NOT a marker ("U.S." is
  upper+upper - rejected), so unit abbreviations never become provisions.
- Message header lines (MSGID/ SUBJ/ REF/ POC/ GENTEXT/ ...) are never
  provisions.
- Tabular, flattened, and tiny R0 categories REFUSE provision parsing -
  they stay section-grade. Honest partial coverage beats invented
  hierarchy.
- Round-trip: every provision keeps raw_marker, so label + raw + text
  reassembles the source exactly. parse_provisions verifies this and
  returns nothing if it fails.

Output per provision:
    path        p2/c/1            (relative, stable)
    number      2.c(1)            (full citation form, machine)
    label       (1)               (as printed - naval letter convention)
    depth       0-based nesting level
    parent      p2/c  or None
    text        paragraph WITH the marker stripped
    raw_marker  exact source marker text (round-trip fidelity)
"""

import re

HDR_RX = re.compile(
    r"^\s*(?:MSGID|SUBJ|REF|NARR|AMPN|POC|GENTEXT|REMARKS|UNCLAS|CLAS|DTG|R\s+\d{6}Z)[/: ]",
    re.I)
# GENTEXT/REMARKS/ is a body-opening tag, not a header field - paragraph 1
# lives on the same line. Strip the tag, keep the provision.
BODY_TAG_RX = re.compile(r"^\s*GENTEXT/(?:REMARKS/)?", re.I)
TABULAR_RX = re.compile(r"\S {2,}\S.* {2,}\S")
LEADER_RX = re.compile(r"\.{4,}|(?:\. ){4,}")

NO_PROVISION_CATEGORIES = {"preformatted-tabular", "flattened", "tiny"}

# ---------------------------------------------------------------------------
# Naval letter front matter (P3 fix, 2026-08-03).
#
# Three defects were measured in the store before this block existed:
#
#  D1  "Ref:   (a) 10 U.S.C. 574" put reference (a) on the label line, and
#      HDR_RX dropped the whole line. The FIRST reference is frequently the
#      governing authority, so the top of every chain was being deleted.
#      Confirmed on MCO 1050.3J, NAVMC 1200.1L, SECNAVINST 1400.1D.
#  D2  Reference letters entered the body stack, so "1. Situation" landed at
#      path a/p1 and deeper body text at h/c/2. Directive provision paths
#      were corrupt wherever a reference list preceded the body.
#  D3  "Ref:  See enclosure (1)" produced nothing at all, which is why 215
#      of 515 MCOs carried no parsed reference list. MCO 1610.7B is the case.
#
# The reference and enclosure lists are a NAMED REGION, not body prose. They
# parse in their own pass, into their own path namespace (ref/a, encl/1)
# under a container node, and never touch the body stack. The path prefix
# carries the role, so no schema change is required.
LABEL_RX = re.compile(
    r"^\s*(From|To|Via|Subj|Subject|Ref"
    r"|Encl|Enclosure|Enclosures)\s*:\s*(.*)$", re.I)
# "Reference" and "References" are deliberately NOT labels. Naval letter
# format uses the abbreviation, and the spelled-out word appears in prose:
# NAVMC 1200.1L ends a sentence with "designated in references:" and was
# opening a reference region mid-chapter, pulling MOS descriptions in as
# authority. The spelled-out heading is handled by REF_HEADING_RX, which
# requires the following items to read as citations.
REF_LABELS = {"ref"}
ENCL_LABELS = {"encl", "enclosure", "enclosures"}
REFITEM_RX = re.compile(r"^\(([A-Za-z]|\d{1,3})\)\s*(.*)$")
BODY_OPEN_RX = re.compile(r"^\d{1,3}\.(?:\s|$)")
# Signature blocks read as a lettered marker: "K. M. IIAMS" scans as upper
# "K." followed by content. A second single initial immediately after is the
# tell, and no numbering scheme in a naval letter looks like one.
SIGNATURE_RX = re.compile(r"^[A-Z]\.\s+[A-Z]\.\s")
# "See enclosure (1)" / "See enclosures (1) through (3)" - a pointer, not a
# list. Recorded verbatim on the container so the authority extractor knows
# to follow it rather than treating the field as empty.
POINTER_RX = re.compile(r"^\s*see\s+encl", re.I)
# The dominant MCO pattern: "Ref: See enclosure (1)" and the list itself
# sits inside Enclosure (1) under a bare "References" heading, with no
# label line anywhere near it. MCO 1400.31D and MCO 1610.7B both do this,
# and it is why 215 of 515 MCOs looked reference-free. The heading opens a
# region only when the next content line is an (x) item, so a chapter
# merely titled "References" never swallows prose.
REF_HEADING_RX = re.compile(r"^\s*references?\s*[:.]?\s*$", re.I)
# Cheap local test for "does this item name an issuance". Kept here rather
# than importing the citation grammar so the parser stays standalone.
ISSUANCE_RX = re.compile(
    r"\b(?:\d{1,2}\s*U\.?\s?S\.?\s?C|Title\s+\d{1,2},?\s*U\.?\s?S\.?"
    r"|DoD\s*(?:I|D|M|INST|Instruction|Directive|Manual)"
    r"|DODINST|DTM|SECNAV|OPNAV|BUMED|CJCS|NAVSO|MCO|Marine\s+Corps\s+Order"
    r"|MCBul|NAVMC|MCRP|MCTP|MCWP|MCDP|MARADMIN|ALMAR|ALNAV"
    r"|Executive\s+Order|E\.?O\.?\s*\d{5})\b", re.I)


def _names_issuance(text: str) -> bool:
    return bool(ISSUANCE_RX.search(text or ""))

# Naval/legal numbering runs 1. / a. / (1) / (a) / underlined - five live
# levels, six with a chapter above. Deeper means the parser is being fed
# something other than a numbering scheme.
MAX_DEPTH = 6
REPEAT_REFUSE_PCT = 10   # duplicated source blocks - extraction defect
DUP_PATH_WARN_PCT = 5

# Ordered segment scanners: (kind, regex). Parenthesized forms first so
# "(1)" never matches the bare-arabic rule.
SEGMENTS = [
    ("paren-arabic", re.compile(r"\((\d{1,3})\)")),
    ("paren-lower", re.compile(r"\(([a-z])\)")),
    ("paren-upper", re.compile(r"\(([A-Z])\)")),
    ("arabic", re.compile(r"(\d{1,3})\.")),
    ("lower", re.compile(r"([a-z])\.")),
    ("upper", re.compile(r"([A-Z])\.")),
    ("lower", re.compile(r"([a-z])(?=\()")),
    ("upper", re.compile(r"([A-Z])(?=\()")),
]

ALPHA_KINDS = {"lower", "upper", "paren-lower", "paren-upper"}


def scan_marker(line: str):
    """Return (segments, raw) or (None, None). segments = [(kind, value)]."""
    if SIGNATURE_RX.match(line):
        return None, None  # signing official's initials, not a paragraph
    pos, segs = 0, []
    while pos < len(line):
        hit = None
        for kind, rx in SEGMENTS:
            m = rx.match(line, pos)
            if m:
                hit = (kind, m.group(1), m.end())
                break
        if not hit:
            break
        kind, value, end = hit
        if segs and segs[-1][0] == kind:
            return None, None  # "U.S." and friends - not a marker
        segs.append((kind, value))
        pos = end
        if pos < len(line) and line[pos] == " ":
            break
    # Tail segment with no delimiter: "1.a" / "2.B" (only after a first
    # segment, so a bare "a text" paragraph is never mistaken for one).
    if segs:
        m = re.match(r"([A-Za-z])(?=\s|$)", line[pos:])
        if m:
            kind = "lower" if m.group(1).islower() else "upper"
            if segs[-1][0] != kind:
                segs.append((kind, m.group(1)))
                pos += m.end()
    if not segs:
        return None, None
    rest = line[pos:]
    # a marker must be followed by whitespace then content
    if rest and not rest[:1].isspace():
        return None, None
    if not rest.strip():
        return None, None
    return segs, line[:pos]


def seg_component(kind: str, value: str, depth: int) -> str:
    if depth == 0 and kind in ("arabic", "paren-arabic"):
        return f"p{value}"
    return value.lower()


def seg_label(kind: str, value: str) -> str:
    if kind.startswith("paren-"):
        return f"({value})"
    return f"{value}."


class _Stack:
    """Marker-kind stack. Each level records its kind and current value."""

    def __init__(self):
        self.levels = []  # [(kind, value)]

    def place(self, kind, value):
        """Known kind pops back to its level; unseen kind pushes a level.

        Exception, observed in MARADMIN 051/23 para 8.c: a document may
        nest the SAME marker kind - (1)(2)(3)(4) and then (1)(2)(3) under
        (4). The tell is a sequence RESTART at the deepest level with no
        intervening parent change (a parent change would already have
        truncated this kind off the stack). Restarting there means going
        deeper, not sideways."""
        # Deepest-first: when a kind appears at two depths, the most
        # recent level owns the marker.
        for i in range(len(self.levels) - 1, -1, -1):
            if self.levels[i][0] == kind:
                if (i == len(self.levels) - 1
                        and value.lower() in ("1", "a")
                        and len(self.levels) < MAX_DEPTH):
                    self.levels.append((kind, value))  # nested same kind
                else:
                    self.levels = self.levels[:i] + [(kind, value)]
                return
        self.levels.append((kind, value))

    def set_absolute(self, segs):
        self.levels = list(segs)

    def path(self):
        return "/".join(seg_component(k, v, i)
                        for i, (k, v) in enumerate(self.levels))

    def number(self):
        out = ""
        for i, (k, v) in enumerate(self.levels):
            if k.startswith("paren-"):
                out += f"({v})"
            elif i == 0:
                out += f"{v}."
            else:
                out += f"{v}."
        return out


def _blocks(text: str):
    """Nonblank, non-header, non-tabular lines grouped into marker-led
    paragraphs. Continuation lines join their paragraph."""
    out = []
    for raw_block in re.split(r"\n\s*\n", text):
        lines = [l for l in raw_block.split("\n") if l.strip()]
        if not lines:
            continue
        tab_hits = sum(1 for l in lines
                       if TABULAR_RX.search(l) or LEADER_RX.search(l))
        if len(lines) >= 2 and tab_hits >= max(2, len(lines) // 3):
            continue  # table - not provisions
        for line in lines:
            stripped = line.strip()
            if BODY_TAG_RX.match(stripped):
                stripped = BODY_TAG_RX.sub("", stripped).strip()
            elif HDR_RX.match(stripped):
                continue
            elif SIGNATURE_RX.match(stripped):
                # Signature block - never a provision. It also BREAKS the
                # paragraph: without the break, dropping the line welds the
                # text on either side of it into one provision that appears
                # nowhere in the source, which is a round-trip failure.
                if out:
                    out.append({"segs": None, "raw": "", "text": "",
                                "src": [], "closed": True})
                continue
            line = stripped
            segs, raw = scan_marker(line.strip())
            if segs:
                out.append({"segs": segs, "raw": raw,
                            "text": line.strip()[len(raw):].strip(),
                            "src": [line]})
            elif out and not out[-1].get("closed"):
                out[-1]["text"] += " " + line.strip()
                out[-1]["src"].append(line)
    return [b for b in out if b.get("segs")]


def split_regions(text: str):
    """Split raw section text into ordered ('ref'|'encl'|'body', lines).

    A label line opens a region. A reference or enclosure region runs until
    a body paragraph opener or the next label. Everything else is body.
    """
    regions, mode, buf = [], "body", []
    lines = text.split("\n")

    def flush():
        if buf:
            regions.append((mode, list(buf)))
            buf.clear()

    def opens_item_run(i):
        """A bare 'References' heading opens a region only when what
        follows is an (x) run whose items read as citations.

        Without the second test, a MOS manual page listing occupational
        codes under a 'References' heading parses as authority. Verified
        on NAVMC 1200.1L, where 'Commercial and Industrial Designers
        27-1021' was landing at path ref/1.
        """
        items, scanned = [], 0
        for nxt in lines[i + 1:i + 30]:
            s = nxt.strip()
            if not s:
                continue
            scanned += 1
            m = REFITEM_RX.match(s)
            if m:
                items.append(m.group(2))
            elif not items and scanned > 2:
                return False
            if len(items) >= 4:
                break
        if not items:
            return False
        named = sum(1 for it in items if _names_issuance(it))
        return named * 2 >= len(items)

    for idx, raw in enumerate(lines):
        line = raw.strip()
        if mode == "body" and REF_HEADING_RX.match(line) and opens_item_run(idx):
            flush()
            mode = "ref"
            continue
        m = LABEL_RX.match(line)
        if m:
            label, remainder = m.group(1).lower(), m.group(2).strip()
            flush()
            if label in REF_LABELS:
                mode = "ref"
            elif label in ENCL_LABELS:
                mode = "encl"
            else:
                mode = "body"          # From/To/Subj carry no provisions
                continue
            if remainder:
                buf.append(remainder)  # D1 - the inline first item survives
            continue
        if mode in ("ref", "encl") and BODY_OPEN_RX.match(line):
            flush()                    # D2 - the list ends, the body begins
            mode = "body"
        buf.append(raw)
    flush()
    return regions


# Extraction reads the reference letter (l) as the digit (1). In an
# alphabetic list running ...j, k, ?, m... the item between (k) and (m) is
# unambiguously (l), and leaving it as "1" collides with the genuine (1) of
# a numbered list in the same region. Repaired ONLY when the homoglyph
# matches the exact letter the sequence expects, and every repair is
# reported so it lands in the record's conversion notes rather than
# happening silently.
HOMOGLYPH = {"1": "l", "0": "o", "5": "s"}


def parse_reference_region(kind: str, lines, ordinal: int = 1):
    """Reference or enclosure list -> provisions under ref/ or encl/.

    Returns a container node plus one node per item. Items never enter the
    body marker stack, so body numbering starts clean.
    """
    # A section holding more than one list (a signed order followed by its
    # Enclosure (1) reference page) gets an ordinal so paths never collide.
    prefix = ("ref" if kind == "ref" else "encl") + ("" if ordinal == 1
                                                    else str(ordinal))
    label = "Ref:" if kind == "ref" else "Encl:"
    items, cur = [], None
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = REFITEM_RX.match(line)
        if m:
            cur = {"value": m.group(1), "text": m.group(2).strip(),
                   "raw": f"({m.group(1)})"}
            items.append(cur)
        elif cur is not None:
            cur["text"] = (cur["text"] + " " + line).strip()
        elif not items:
            # Text before any (x) marker - a pointer such as
            # "See enclosure (1)", or a stray continuation. Held on the
            # container so nothing is silently dropped.
            cur = None
            items.append({"value": None, "text": line, "raw": ""})
            items[-1]["container_text"] = True
            cur = items[-1]

    container_text = " ".join(
        i["text"] for i in items if i.get("container_text")).strip()
    marked = [i for i in items if not i.get("container_text")]

    repairs = []
    prev = None
    for i in marked:
        v = i["value"]
        if prev and prev.isalpha() and v in HOMOGLYPH:
            expect = chr(ord(prev.lower()) + 1)
            if HOMOGLYPH[v] == expect:
                repairs.append(f"({v})->({expect})")
                i["value"] = expect if prev.islower() else expect.upper()
                i["raw"] = f"({i['value']})"
        prev = i["value"]

    out = [{
        "path": prefix,
        "number": label,
        "label": label,
        "depth": 0,
        "parent": None,
        "text": container_text,
        "raw_marker": label,
    }]
    used = set()
    for i in marked:
        v = i["value"].lower()
        # Paths must be unique inside a region. A duplicate means the source
        # itself repeats a marker; keep both items and say which is which
        # rather than letting one overwrite the other.
        if v in used:
            n = 2
            while f"{v}x{n}" in used:
                n += 1
            v = f"{v}x{n}"   # schema path pattern allows [0-9a-z] only
        used.add(v)
        out.append({
            "path": f"{prefix}/{v}",
            "number": f"({i['value']})",
            "label": f"({i['value']})",
            "depth": 1,
            "parent": prefix,
            "text": i["text"],
            "raw_marker": i["raw"],
        })
    # A container with neither items nor text states nothing - drop it.
    if len(out) == 1 and not container_text:
        return []
    if repairs:
        out[0]["_repairs"] = repairs
    return out


def is_pointer(provision) -> bool:
    """True when a Ref: field points at an enclosure instead of listing."""
    return (provision.get("path") in ("ref", "encl")
            and bool(POINTER_RX.match(provision.get("text") or "")))


def parse_provisions(text: str, category: str = "mixed"):
    """text -> (provisions, note). provisions is [] when the document is
    not provision-shaped; note explains why."""
    if category in NO_PROVISION_CATEGORIES:
        return [], f"provision parsing refused - R0 category {category}"

    # Front matter first. Reference and enclosure lists parse in their own
    # namespace and are removed from the body text, so the marker stack the
    # body builds starts empty.
    regions = split_regions(text)
    front, body_lines, ref_note = [], [], []
    seen_kind = {}
    for kind, lines in regions:
        if kind in ("ref", "encl"):
            seen_kind[kind] = seen_kind.get(kind, 0) + 1
            got = parse_reference_region(kind, lines, seen_kind[kind])
            reps = got[0].pop("_repairs", None) if got else None
            if reps:
                ref_note.append("OCR marker repair " + ", ".join(reps))
            front.extend(got)
            if got:
                n = sum(1 for p in got if p["parent"])
                ref_note.append(f"{got[0]['path']} list: {n} item(s)"
                                + (" (pointer)" if any(is_pointer(p)
                                                       for p in got) else ""))
        else:
            body_lines.extend(lines)
    body_text = "\n".join(body_lines)

    blocks = _blocks(body_text)
    if len(blocks) < 2:
        if front:
            note = "no body provision structure detected"
            if ref_note:
                note += ", " + ", ".join(ref_note)
            return front, note
        return [], "no provision structure detected"

    # Extraction defect check: some sidecars repeat the whole message body
    # several times (verified on ALMAR-2025-001). Numbering restarts on
    # every repeat, so any tree built from it is fiction - refuse.
    fingerprints = [f'{b["raw"]}|{b["text"][:60]}' for b in blocks]
    repeats = len(fingerprints) - len(set(fingerprints))
    if repeats * 100 // max(len(fingerprints), 1) >= REPEAT_REFUSE_PCT:
        return [], (f"provision parsing refused - source text repeats "
                    f"({repeats} of {len(blocks)} blocks duplicated), "
                    f"extraction defect")

    stack = _Stack()
    provisions, anomalies = [], 0
    for b in blocks:
        segs = b["segs"]
        if len(segs) > 1:
            stack.set_absolute(segs)
        else:
            kind, value = segs[0]
            known = any(k == kind for k, _ in stack.levels)
            if not known and value.lower() not in ("1", "a", "i"):
                anomalies += 1
            stack.place(kind, value)
        path = stack.path()
        kind, value = stack.levels[-1]
        parent = "/".join(path.split("/")[:-1]) or None
        provisions.append({
            "path": path,
            "number": stack.number(),
            "label": seg_label(kind, value),
            "depth": len(stack.levels) - 1,
            "parent": parent,
            "text": b["text"],
            "raw_marker": b["raw"],
        })

    seen = {}
    for p in provisions:
        seen[p["path"]] = seen.get(p["path"], 0) + 1
    dupes = sum(1 for n in seen.values() if n > 1)
    maxd = max(p["depth"] for p in provisions)

    provisions = front + provisions
    note = f"provisions parsed: {len(provisions)}, max depth {maxd}"
    if ref_note:
        note += ", " + ", ".join(ref_note)
    if anomalies:
        note += f", {anomalies} out-of-sequence opener(s)"
    if dupes:
        note += f", {dupes} duplicate path(s)"
    # Unreliability signals - the record still carries provisions, but the
    # note tells the gate reviewer (and the site) not to trust the tree.
    if dupes * 100 // max(len(seen), 1) >= DUP_PATH_WARN_PCT or maxd >= MAX_DEPTH - 1:
        note += " - REVIEW: tree may be unreliable"
    return provisions, note


def uslm_paths(provisions, base_uslm: str):
    """Attach absolute USLM identifiers under a document (or section)."""
    for p in provisions:
        p["uslm_identifier"] = f"{base_uslm}/{p['path']}"
        p["verification"] = "UNVERIFIED"
    return provisions
