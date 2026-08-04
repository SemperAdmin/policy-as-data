"""Rebuild the site search index from this project's corpus.

The inherited index carried 17,507 documents from the parent corpus while
this project publishes 54 pages, so roughly 99.7 percent of every result set
was a link to a page that does not exist. A search box that mostly dead-ends
is worse than no search box: it teaches a visitor that the library is broken.

The index is now generated from `canonical/`, so it can only ever offer what
the site actually renders.

Format, matching what the existing search.html expects:

    search/docs.json     [{id, t, y, s}, ...]           the display rows
    search/t/<pp>.json   {token: "docIdx:tf,docIdx:tf"} postings, sharded on
                         the token's first two characters

Term frequency is always written explicitly. The inherited shards omitted it
when it was 1, which made the client parse `undefined` and score that document
NaN - it still appeared in results, but ranked by accident.
"""

import argparse
import json
import os
import re
from collections import defaultdict

TOKEN_RX = re.compile(r"[a-z0-9][a-z0-9./-]*")
STOP = set("""a an and are as at be by for from has have in is it its of on or
that the this to was were will with shall may must not all any""".split())
MAX_TOKENS_PER_DOC = 4000


def tokenize(text):
    for t in TOKEN_RX.findall((text or "").lower()):
        t = t.strip("./-")
        if len(t) < 2 or t in STOP:
            continue
        yield t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="canonical")
    ap.add_argument("--out", default="docs/search")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.out, "t"), exist_ok=True)
    docs, postings = [], defaultdict(lambda: defaultdict(int))

    names = sorted(f for f in os.listdir(args.src) if f.endswith(".json"))
    for idx, name in enumerate(names):
        with open(os.path.join(args.src, name), encoding="utf-8") as fh:
            rec = json.load(fh)
        if not rec.get("publication", {}).get("publishable", True):
            continue                       # the gate holds in every output
        docs.append({"id": rec["id"],
                     "t": (rec.get("subject") or rec.get("title") or "")[:160],
                     "y": rec.get("doc_type") or "",
                     "s": rec.get("status") or "unknown"})
        i = len(docs) - 1

        parts = [rec["id"], rec.get("title") or "", rec.get("subject") or "",
                 rec.get("native_number") or ""]
        for sec in rec.get("sections", []):
            parts.append(sec.get("heading") or "")
            for p in sec.get("provisions") or []:
                parts.append(p.get("text") or "")
        seen = 0
        for tok in tokenize(" ".join(parts)):
            postings[tok][i] += 1
            seen += 1
            if seen >= MAX_TOKENS_PER_DOC:
                break

    with open(os.path.join(args.out, "docs.json"), "w", encoding="utf-8") as fh:
        json.dump(docs, fh, ensure_ascii=False)

    shards = defaultdict(dict)
    for tok, hits in postings.items():
        prefix = re.sub(r"[^a-z0-9]", "_", tok[:2])
        shards[prefix][tok] = ",".join(f"{i}:{n}" for i, n in sorted(hits.items()))

    for prefix, table in shards.items():
        with open(os.path.join(args.out, "t", f"{prefix}.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(table, fh, ensure_ascii=False)

    print(f"docs.json      {len(docs)} document(s)")
    print(f"tokens         {len(postings)}")
    print(f"shards         {len(shards)} file(s) in {args.out}/t")


if __name__ == "__main__":
    main()
