"""Canonical normalization and content hashing for verification.

An attestation binds to the exact content a human confirmed. That binding is
only useful if the hash changes when the meaning changes and does NOT change
when the file is merely rewritten. This module is that rule, in one place.

Why the normalization is not optional
-------------------------------------
The working tree is CRLF and files written from a Linux environment arrive with
LF (SESSION_HANDOFF.md section 8). Hashing raw bytes would invalidate every
attestation in the corpus on the first Windows/Linux round trip, and the
verification effort would evaporate silently. So bytes are normalized before
hashing, and the rule is written down rather than left to whatever the caller
happened to do.

What is hashed, and what deliberately is not
--------------------------------------------
For a PROVISION: its text only. Not the identifier, not the label, not the
depth, not the position. Renumbering or moving a provision must not invalidate a
human's reading of its words. Only a change to what it SAYS should.

For a RULE VALUE: the value, the unit, and the citation identifier - the
assertion itself. Not the note, not the label, not the id. Editing prose in a
note is not a change to the claim; changing 84 to 90, or repointing the citation
from para 11.d to para 8, is.

Normalization steps, in order:
  1. Line endings to \\n
  2. Trailing whitespace stripped per line
  3. Runs of internal whitespace collapsed to one space
  4. Leading and trailing blank lines removed
  5. Unicode NFC

Step 3 is the aggressive one and it is deliberate. Naval message text arrives
with alignment padding that carries no meaning, and a reader confirming a
paragraph is confirming words, not columns.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata

ALGORITHM = "sha256"
PREFIX = "sha256:"

_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)
_INTERNAL_WS = re.compile(r"[ \t]{2,}")


def normalize_text(text: str) -> str:
    """Apply the canonical normalization. Pure, and safe on any input."""
    if text is None:
        return ""
    s = text.replace("\r\n", "\n").replace("\r", "\n")
    s = _TRAILING_WS.sub("", s)
    s = _INTERNAL_WS.sub(" ", s)
    # Strip every line, not only blank ones. Leading indentation is layout, not
    # meaning, and a reader confirming a paragraph is confirming words. The
    # first version of this line only stripped blank lines, which is a no-op,
    # and the smoke check below caught it.
    s = "\n".join(line.strip() for line in s.split("\n"))
    s = s.strip("\n").strip()
    return unicodedata.normalize("NFC", s)


def content_hash(text: str) -> str:
    """Hash of a provision's text, after normalization."""
    digest = hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()
    return PREFIX + digest


def rule_assertion(rule: dict) -> dict:
    """The hashable core of a rule value.

    Value, unit, and the citation identifier. Nothing else. See the module
    docstring for why the note and the label are excluded.
    """
    citation = rule.get("citation") or {}
    return {
        "value": rule.get("value"),
        "unit": rule.get("unit"),
        "citation_identifier": citation.get("identifier"),
    }


def rule_hash(rule: dict) -> str:
    """Hash of a rule's assertion. Key order is fixed by sort_keys."""
    payload = json.dumps(
        rule_assertion(rule), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return PREFIX + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def rule_assertion_id(source_identifier: str, rule_id: str) -> str:
    """Stable id for a rule assertion: <document identifier>#<RULE_ID>."""
    return f"{source_identifier}#{rule_id}"


def file_hash(path) -> str:
    """Hash of a file's raw bytes. For signed artifacts, NOT for text.

    A signed PDF is evidence, not prose. Normalizing it would be wrong.
    """
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return PREFIX + h.hexdigest()


if __name__ == "__main__":  # pragma: no cover - smoke check
    samples = [
        "84 days\r\nper para 11.d",
        "84 days\nper para 11.d",
        "84 days   \n   per   para 11.d  ",
        "\n\n84 days\nper para 11.d\n\n",
    ]
    hashes = {content_hash(s) for s in samples}
    print("CRLF/LF/whitespace/padding variants collapse to one hash:", len(hashes) == 1)
    print(content_hash(samples[0]))
    print("a real change moves it:", content_hash("90 days\nper para 11.d") not in hashes)
