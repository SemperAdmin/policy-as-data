#!/usr/bin/env python3
"""Stamp the build with a digest of the inputs it was built from.

Why this exists: twice, a change to a build input merged to main without its
rebuilt output (the Ontology nav link missing from 71 pages; clause quorum
missing from config/reconciliation.json). CI cannot run ./build.sh, because
stages 1-14 read canonical/, which is untracked and unpublished by design. So
CI cannot rebuild the canonical-dependent output and compare it. What it can
do is ask whether the build ran after the last input change: stage 24 writes
this stamp, and CI recomputes it.

What the stamp proves, and what it does not:
  - It proves ./build.sh ran to its last stage over exactly these inputs.
  - It does not prove the canonical-dependent output is correct.
  - It cannot see a change to canonical/ itself (untracked).
  - A hand-edited output committed without a rebuild is caught only for the
    canonical-free stages, which CI re-runs and diffs (validate.yml).

Inputs are listed in config/build_inputs.json (configuration lives in
config/, never in a tool). Each pattern is a pathlib glob from the repository
root and must match at least one file, so a manifest that has gone stale fails
loudly instead of silently covering less.

Digest: sha256 over the sorted lines "<sha256 of file>  <posix path>\\n", where
each file's hash is taken after CRLF is normalized to LF. A Windows checkout
and a Linux runner therefore agree; a line-ending change is not a content
change.

Usage:
    python tools/build_stamp.py --write    # stage 24 of ./build.sh
    python tools/build_stamp.py --check    # CI: exit 0 current, 1 stale, 2 no stamp
    python tools/build_stamp.py --check --root DIR
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomicio import write_json  # noqa: E402

MANIFEST = Path("config") / "build_inputs.json"
STAMP = Path("config") / "build_stamp.json"
STAMP_POSIX = STAMP.as_posix()


class ManifestError(Exception):
    pass


def resolve_inputs(root: Path) -> list[str]:
    """Posix relative paths of every file the manifest names, sorted."""
    try:
        manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ManifestError(f"{MANIFEST.as_posix()} not found under {root}")
    excludes = list(manifest.get("exclude", [])) + [STAMP_POSIX]
    found = set()
    for pattern in manifest["include"]:
        matched = [p.relative_to(root).as_posix() for p in root.glob(pattern) if p.is_file()]
        if not matched:
            raise ManifestError(f"manifest pattern {pattern!r} matches nothing - "
                                f"update {MANIFEST.as_posix()}")
        found.update(matched)
    return sorted(p for p in found
                  if not any(fnmatch.fnmatchcase(p, ex) for ex in excludes))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def digest(root: Path) -> tuple[str, int]:
    paths = resolve_inputs(root)
    h = hashlib.sha256()
    for rel in paths:
        h.update(f"{file_sha256(root / rel)}  {rel}\n".encode("utf-8"))
    return h.hexdigest(), len(paths)


def write(root: Path) -> int:
    stamp = root / STAMP
    if stamp.exists():
        os.remove(stamp)  # remove prior output first; idempotence by construction
    inputs, n = digest(root)
    write_json(str(stamp), {
        "$comment": "Digest of the tracked build inputs (config/build_inputs.json) the "
                    "committed output was built from. Written by ./build.sh stage 24; "
                    "CI runs tools/build_stamp.py --check. No timestamp, so two builds "
                    "over the same inputs write the same bytes.",
        "schema_version": "1.0",
        "inputs_sha256": inputs,
        "files": n,
    })
    print(f"    {n} input file(s), inputs_sha256 {inputs[:12]}")
    return 0


def check(root: Path) -> int:
    stamp = root / STAMP
    if not stamp.exists():
        print(f"no build stamp at {STAMP_POSIX}. Run ./build.sh and commit its output.",
              file=sys.stderr)
        return 2
    old = json.loads(stamp.read_text(encoding="utf-8"))["inputs_sha256"]
    new, n = digest(root)
    if old != new:
        print(f"build output is stale: inputs changed since the last ./build.sh "
              f"(stamp {old[:12]} != inputs {new[:12]}). Run ./build.sh and commit its output.",
              file=sys.stderr)
        return 1
    print(f"build stamp current: {n} input file(s), {new[:12]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write config/build_stamp.json")
    mode.add_argument("--check", action="store_true", help="compare the stamp with the inputs")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent),
                    help="repository root (default: this tool's repository)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    try:
        return write(root) if args.write else check(root)
    except ManifestError as exc:
        print(f"build_stamp: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
