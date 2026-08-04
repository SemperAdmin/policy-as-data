#!/usr/bin/env python3
"""
Refuse to publish contact data.

Two modes, both reading git rather than the working tree, so a masked file on
disk and an unmasked one in the object store cannot be confused.

  python tools/contact_guard.py                 scan the staging index
  python tools/contact_guard.py pipeline-x      scan a branch, tag, or commit

Uses `git grep`, so a 1,100-file tree scans in seconds. Exit 1 on any hit.

On the seven-digit form. A bare NNN-NNNN is indistinguishable from a document
identifier - config/revision_index.json holds
"PRIUM-51209-government-equipment-operator-license-ttc-489-0050" - so this
guard only flags the seven-digit form next to a phone label. A gate that
blocks a legitimate push teaches people to skip the gate, which costs more
than the narrow miss. The maskers in export_issuance.py, render_authority_chain.py,
and build_search.py stay broader, because over-masking prose is harmless.
"""

import re
import subprocess
import sys

EMAIL = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(mil|gov|com|org|net|edu)"
PHONE_FULL = r"\(?[0-9]{3}\)?[-. ][0-9]{3}[-. ][0-9]{4}"
LABEL = r"(DSN|Comm|Commercial|Tel|Telephone|Phone|Fax|Cell)[.: ]"
PHONE_LABELED = LABEL + r"[ ]*\(?[0-9]{3}\)?[-. ]?[0-9]{3}[-.][0-9]{4}"
PHONE_LOCAL = LABEL + r"[ ]*[0-9]{3}[-.][0-9]{4}"

PATTERNS = [EMAIL, PHONE_FULL, PHONE_LABELED, PHONE_LOCAL]

# Whole-match placeholders present to show a format, not to reach anyone.
ALLOW = re.compile(r"myemail@[A-Za-z0-9.-]+|\(?123\)?[-. ]456[-. ]7890")

# Retired output is gitignored. This file carries the patterns by definition.
EXCLUDE = re.compile(r"(^|/)_to_delete|(^|/)contact_guard\.py$")

EXTRACT = re.compile("|".join(f"(?:{p})" for p in PATTERNS), re.I)


def git_grep(pattern, ref):
    # --cached is an option, so it has to precede the pattern. git rejects it
    # after a non-option argument, and the failure is quiet enough to read as
    # a clean scan if the return code is not checked.
    cmd = ["git", "grep"] + ([] if ref else ["--cached"])
    cmd += ["-I", "-n", "-E", "-i", pattern]
    if ref:
        cmd.append(ref)
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode not in (0, 1):
        print(f"   git grep failed: {r.stderr.strip()}")
        sys.exit(2)
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def parse(line, ref):
    # "<ref>:<path>:<lineno>:<text>" with a ref, "<path>:<lineno>:<text>" without
    body = line[len(ref) + 1:] if ref and line.startswith(ref + ":") else line
    parts = body.split(":", 2)
    return (parts[0], parts[2]) if len(parts) == 3 else (body, "")


def main():
    ref = sys.argv[1] if len(sys.argv) > 1 else None
    target = ref or "the staging index"

    hits = {}
    for pattern in PATTERNS:
        for line in git_grep(pattern, ref):
            path, text = parse(line, ref)
            if EXCLUDE.search(path):
                continue
            found = [m.group(0) for m in EXTRACT.finditer(text)
                     if not ALLOW.fullmatch(m.group(0))]
            if found:
                hits.setdefault(path, set()).update(found)

    if not hits:
        print(f"   clean - no contact data in {target}")
        return 0

    print(f"   CONTACT DATA IN {target}. Refused.")
    for path in sorted(hits):
        vals = sorted(hits[path])
        shown = ", ".join(vals[:4])
        more = f" (+{len(vals) - 4} more)" if len(vals) > 4 else ""
        print(f"     {path}")
        print(f"       {shown}{more}")
    print()
    print("   Mask or unstage those paths, then run again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
