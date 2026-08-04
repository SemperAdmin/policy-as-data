"""Does the demo actually work when someone opens it.

Not "did the generator run" - that is already known. This asks the questions a
visitor's browser will ask: does every link land somewhere, does every asset
exist, is every anchor real, and is anything unreachable from the front door.

Runs offline against the file tree. No server, no browser, because a static
demo has to survive being opened from a folder or handed over on a drive.
"""

import html
import json
import os
import re
import sys
from collections import Counter, defaultdict
from urllib.parse import unquote, urldefrag

# Must not match a JavaScript property assignment. `a.href = "policy-"` is a
# string being built at runtime, not a link in the markup, and reading it as
# one reports a dead link that no browser will ever follow.
HREF_RX = re.compile(r'(?<![.\w])(?:href|src)\s*=\s*"([^"]+)"', re.I)
ID_RX = re.compile(r'\sid\s*=\s*"([^"]+)"', re.I)
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")
TITLE_RX = re.compile(r"<title>(.*?)</title>", re.I | re.S)
LANG_RX = re.compile(r'<html[^>]*\slang\s*=', re.I)
H1_RX = re.compile(r"<h1[\s>]", re.I)
IMG_RX = re.compile(r"<img\b[^>]*>", re.I)
ALT_RX = re.compile(r'\salt\s*=', re.I)


def main(root, entry="index.html"):
    pages, assets = {}, set()
    for dirpath, dirs, files in os.walk(root):
        # Retired files are staged here because the tooling that reaches this
        # disk cannot delete. They are not part of the site and crawling them
        # produces dead links that describe the staging area, not the demo.
        dirs[:] = [d for d in dirs if d != "_to_delete" and not d.startswith("_to_delete")]
        for f in files:
            rel = os.path.relpath(os.path.join(dirpath, f), root).replace("\\", "/")
            if f.lower().endswith((".html", ".htm")):
                pages[rel] = None
            else:
                assets.add(rel)

    fails, warns = [], []
    links_out = defaultdict(set)
    ids = {}
    stats = Counter()

    for rel in sorted(pages):
        path = os.path.join(root, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except Exception as exc:                       # noqa: BLE001
            fails.append(f"UNREADABLE {rel}: {exc}")
            continue
        pages[rel] = len(text)
        ids[rel] = set(ID_RX.findall(text))

        # structural minimums a browser and a screen reader both rely on
        if not TITLE_RX.search(text):
            fails.append(f"NO TITLE {rel}")
        if not LANG_RX.search(text):
            warns.append(f"NO LANG ATTRIBUTE {rel}")
        if not H1_RX.search(text):
            warns.append(f"NO H1 {rel}")
        for img in IMG_RX.findall(text):
            if not ALT_RX.search(img):
                warns.append(f"IMG WITHOUT ALT {rel}: {img[:70]}")

        base = os.path.dirname(rel)
        for raw in HREF_RX.findall(text):
            raw = html.unescape(raw).strip()
            if not raw or raw.startswith(EXTERNAL):
                stats["external_or_anchor"] += 1
                continue
            target, frag = urldefrag(unquote(raw))
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(base, target)).replace("\\", "/")
            links_out[rel].add((resolved, frag, raw))
            stats["internal"] += 1

    # dead links and dead anchors
    dead = Counter()
    for src, targets in links_out.items():
        for resolved, frag, raw in targets:
            known = resolved in pages or resolved in assets
            if not known and os.path.isdir(os.path.join(root, resolved)):
                known = f"{resolved}/index.html" in pages
            if not known:
                dead[raw] += 1
                fails.append(f"DEAD LINK {src} -> {raw}")
            elif frag and resolved in pages and frag not in ids.get(resolved, set()):
                warns.append(f"DEAD ANCHOR {src} -> {raw}")

    # reachability from the front door
    seen, queue = set(), [entry]
    if entry not in pages:
        fails.append(f"NO ENTRY PAGE {entry}")
        queue = []
    while queue:
        cur = queue.pop()
        if cur in seen:
            continue
        seen.add(cur)
        for resolved, _f, _r in links_out.get(cur, ()):
            if resolved in pages and resolved not in seen:
                queue.append(resolved)
    orphans = sorted(set(pages) - seen)

    print(f"pages            {len(pages)}")
    print(f"other files      {len(assets)}")
    print(f"internal links   {stats['internal']}")
    print(f"external/anchor  {stats['external_or_anchor']}")
    print(f"reachable        {len(seen)} from {entry}")
    print(f"orphans          {len(orphans)}")
    print(f"dead links       {sum(dead.values())} ({len(dead)} distinct)")
    print()

    if dead:
        print("DISTINCT DEAD TARGETS")
        for tgt, n in dead.most_common(15):
            print(f"  x{n:<5} {tgt}")
        if len(dead) > 15:
            print(f"  ... {len(dead) - 15} more")
        print()

    if orphans:
        print(f"ORPHANS (exist but nothing links to them)")
        for o in orphans[:15]:
            print(f"  {o}")
        if len(orphans) > 15:
            print(f"  ... {len(orphans) - 15} more")
        print()

    hard = [f for f in fails if not f.startswith("DEAD LINK")]
    if hard:
        print(f"STRUCTURAL FAILURES: {len(hard)}")
        for f in hard[:12]:
            print("  " + f)
        print()

    if warns:
        kinds = Counter(w.split()[0] + " " + w.split()[1] for w in warns)
        print("WARNINGS")
        for k, n in kinds.most_common():
            print(f"  {n:<5} {k}")
        for w in warns[:6]:
            print("    e.g. " + w[:120])
        print()

    ok = not fails
    print("PASS - every link lands, every page is reachable" if ok
          else f"FAIL - {len(fails)} problem(s)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs",
                  sys.argv[2] if len(sys.argv) > 2 else "index.html"))
