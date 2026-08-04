# Does the demo actually work

Date: 2026-08-04. Checked against `D:\Coding\policy-as-data\docs` as it stands
on disk, not against the generator's own report of what it wrote.

## Result

```
pages            77
other files      408
internal links   870
reachable        77 from index.html
orphans          0
dead links       0
```

Twelve pages rendered in a headless browser: no console errors, no page errors,
no broken images, no failed requests, no horizontal overflow. Search returns
correct results and every indexed document has a page to land on.

`tools/check_site.py` and `tools/build_search.py` are now stages 15 and 13 of
`build.sh`, so this cannot silently regress.

---

## Five real defects found, all fixed

### 1. The logo was missing on every page

`semper-logo.jpg` was referenced ten times and did not exist. Every page
rendered with the alt text "Semper Admin emblem" where the emblem should be.
Copied in.

### 2. Search was linked from every page and did not exist

`search.html` was in the navigation of ten pages, and the file had not moved
across. Copied in.

### 3. Search pointed at pages that no longer existed, across an index of the
wrong corpus

The inherited index carried **17,507 documents** while the site publishes 57
pages, and the client built its links as `doc.id + ".html"` - a naming the
integrated pages no longer use. Roughly 99.7 percent of every result set was a
link to nothing.

A search box that mostly dead-ends is worse than no search box, because it
teaches a visitor that the library is broken rather than that it is small.

`tools/build_search.py` now generates the index from this project's own
corpus, and the client builds `policy-<ID>.html`. Verified: 56 indexed
documents, **0 with no page**. Queries return sensible ranked results -
"parental leave" puts MARADMIN 051/23 first at 186, its clarification second
at 27.

While rebuilding it I found the inherited shards omitted term frequency when
it was 1, which made the client parse `undefined` and score that document
`NaN`. It still appeared in results, ranked by accident. Frequency is now
always written explicitly.

### 4. The chapter-and-verse showcase had been stranded

`MARADMIN-2021-360` and `-388` are the CPIB pair - 388 cites paragraph 2.d of
360, which is the provision-grade citation the whole concept is built to
demonstrate, and which `how-it-works.html` describes at length.

Neither was in the extracted corpus. Their old pages survived the move but
nothing linked to them, so the demo's central example was reachable only by
typing the filename. Both records are now in `canonical/` and both have full
integrated pages.

### 5. Search hung forever when the folder was opened directly

This is the one worth reading twice.

Browsers refuse `fetch()` for `file:` URLs. Someone who unzips the demo and
double-clicks `index.html` gets a site where **everything works except search,
which sits on "Searching…" and never resolves**. There was no `.catch`, so the
promise rejected into silence.

A hang reads as a broken site. A message reads as a missing server. The page
now detects the protocol and says:

> Search needs this folder served over HTTP. Everything else on this site works
> offline. Run: `python -m http.server 8000` in this folder, then open
> http://localhost:8000/search.html

Confirmed in both transports: `file://` shows the message, `http://` returns
2 results for "parental".

---

## Two false alarms, worth recording so they are not re-found

**The checker reported a dead link to `policy-`.** It was matching the
JavaScript assignment `a.href = "policy-" + doc.id + ".html"` as though it were
an HTML attribute. The regex now refuses a match preceded by a dot or a word
character. No such link exists in the markup.

**Seven pages reported as orphans after the fix.** They were the retired
duplicates sitting in `docs/_to_delete/`. The checker now skips those folders -
they are a staging area for files the bridge cannot delete, not part of the
site.

---

## How the demo should be opened

**Served, for everything:**

```
cd D:\Coding\policy-as-data\docs
python -m http.server 8000
```
then `http://localhost:8000/`.

**From the folder, if that is all that is available:** every page, link,
diagram, chain, network, and full policy text works. Only search needs the
server, and it now says so rather than hanging.

---

## What is still true and unfixed

**Page weight.** `policy-NAVMC-1200.1L.html` is 3.5 MB - a 975-page manual with
13,595 addressable paragraphs. It renders, and the text sits inside a collapsed
disclosure so nothing draws until asked. It is heavy on a phone.

**One round-trip warning.** `NAVMC-1200.1L` section `p-3-36` carries a
paragraph whose text spans a page break, so it does not appear contiguously in
the source. It reproduces identically under the previous parser, so it is an
extraction artifact rather than something this work introduced. The verifier
reports it as a warning rather than a failure, deliberately, so it stays
visible without masking a real one.

**`docs/search/_to_delete_t`** holds the 1,332 stale shards from the inherited
index, and `docs/_to_delete` holds the seven superseded pages. Both are waiting
on your delete - the bridge can move files but cannot remove them.

---

## Addendum, 2026-08-04 - the build was not idempotent, and said it was

The claim "every stage is idempotent, running twice produces identical counts"
was true and useless. Counts matched while the corpus changed underneath them.
Measuring hashes instead of counts found two defects in about a minute:

```
find canonical -name '*.json' | sort | xargs md5sum > /tmp/a
<full build>
find canonical -name '*.json' | sort | xargs md5sum > /tmp/b
cmp /tmp/a /tmp/b     ->  DIVERGED
```

**Every build appended a duplicate corrections entry.** The corpus had
accumulated 361 identical `normalize_identifiers.py` entries across 42 records.
Each said the period had been replaced. None described a distinct change; they
were a count of how many times the build had run, written into the field a
reader would use to adjudicate the `[ID2]` promotion. `tools/corrections.py`
now replaces a tool's own prior entry rather than appending. One cleanup run
took 361 to 43 - 42 records plus one.

**Every build rewrote the statute and DoD spine.** `ingest_authority_tiers.py`
stamped `extracted_at` and `converted_at` from the clock, so eleven top-tier
records changed on every run with no changed content. Those fields state when
the metadata was hand-entered. They are now a literal, bumped when the table is
edited and not otherwise.

After both fixes:

```
56 records          byte-identical across two full passes
every docs/ file    byte-identical across two full renders
verify_authority    PASS
check_site          77 pages, 870 links, 0 dead, 0 orphans
export_issuance     56 written, 0 quarantined, ALL VALID against the XSD
```

## The atomic write proved itself by accident

Mid-verification, a build was killed part-way through stage 11 by a 45-second
transport timeout. Before `tools/atomicio.py` that is precisely the event that
truncated `NAVMC-1200.1L.json` to 1.3 MB of 9.2 MB. This time:

```
temp files left behind   none
unparseable records      none  (56 of 56 load)
```

The kill landed between a temporary file and its rename, which is the only
place it can land now.
