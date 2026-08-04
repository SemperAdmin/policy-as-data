#!/usr/bin/env python3
"""
Refuse a commit that stages contact data.

Reads what is actually in the index, not what is on disk, so a masked file on
disk and an unmasked one staged cannot be confused. Exit 1 on any hit.

Usage:  python tools/contact_guard.py
"""

import re
import subprocess
import sys

EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.(?:mil|gov)")
PHONE = re.compile(rb"\(?\d{3}\)?[ -]\d{3}-\d{4}")

# Placeholders that exist to show the format, not to reach anyone.
ALLOW = {b"myemail@usmc.mil", b"(123) 456-7890", b"123-456-7890"}


def staged_files():
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [line for line in out.splitlines() if line.strip()]


def blob(path):
    r = subprocess.run(["git", "show", ":" + path], capture_output=True)
    return r.stdout if r.returncode == 0 else b""


def main():
    findings = []
    for path in staged_files():
        data = blob(path)
        if not data:
            continue
        hits = {m.group(0) for m in EMAIL.finditer(data)} - ALLOW
        hits |= {m.group(0) for m in PHONE.finditer(data)} - ALLOW
        if hits:
            findings.append((path, sorted(h.decode("utf-8", "replace") for h in hits)))

    if not findings:
        print("   clean - no contact data staged")
        return 0

    print("   CONTACT DATA STAGED. Commit refused.")
    for path, hits in findings:
        shown = ", ".join(hits[:4])
        more = f" (+{len(hits) - 4} more)" if len(hits) > 4 else ""
        print(f"     {path}")
        print(f"       {shown}{more}")
    print()
    print("   Unstage those paths, or mask them, then run again.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
