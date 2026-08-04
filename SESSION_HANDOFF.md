# Session handoff - policy-as-data

Written 2026-08-04 for a session starting with no prior context. Read this
first, then the four documents in section 2. Everything below is measured
against `D:\Coding\policy-as-data` as it stands on disk, not asserted from a
tool's own report of what it wrote.

---

## 1. What this project is

Marine Corps policy, recast as structured data, the way Congress publishes
statute as USLM XML.

The product is **the encoding itself**: a faithful, addressable representation
of an issuance where every provision has a stable identifier, and where the
authority a policy rests on can be walked one cited link at a time up to the
Department of Defense instruction or the statute behind it.

Two claims sit underneath and both are testable:

- **Chapter and verse.** A message can cite paragraph 2.d of another message
  and the citation resolves to that paragraph, not to the document. MARADMIN
  2021-388 to MARADMIN 2021-360 is the worked example the site is built around.
- **The chain is walkable.** Statute to DoD instruction to service directive to
  message, each step read from the text that states it, with the paragraph that
  states it named.

It is a standalone project. It carries its own corpus, its own tooling, and its
own build. Nothing else needs to be present.

---

## 2. Read these before touching anything

| file | what it settles |
|---|---|
| `DATA_CONTRACT.md` | the read-only mandate. Read it first, every time. |
| `BUILD.md` | build state, the fifteen stages, what needs a decision |
| `NAMESPACES.md` | the identifier register and the period ruling |
| `conformance-matrix.md` | verdicts against every standard, with the text each turns on |

Then, as needed: `MOVED.md` (how the project was extracted and what stayed
behind), `HANDOFF.md` (the line between this and GunnyBot), `VERIFICATION.md`
(does the demo actually work, and the defects found proving it),
`schema/README.md`, `REFERENCES.md`.

---

## 3. Where it stands, measured

```
canonical/          56 documents, 20,178 provisions
data/exports/       56 issuance.xml, ALL VALID against usmc-issuance-2.0.xsd
docs/               77 pages, 870 internal links, 0 dead, 0 orphans
                    ~11 MB, plus a 76 MB _to_delete_t awaiting your delete
authority edges     362 - 57 held, 85 revision-drift, 220 named-not-held
citations           286 provision-level, 384 items classified, 174 unparsed
search              56 documents indexed, 7,831 tokens, 558 shards, 0 dead ends
verify_authority    PASS
check_site          PASS
idempotent          56 records and every docs/ file byte-identical on a re-run
```

Twenty-three tools, six config files, two schemas, two namespaces.

### The site

Twenty non-policy pages plus 56 integrated policy pages, one per document:

    index  how-it-works  search  sources  connections  accessibility
    authority-index + five spine pages (leave, promotion, mos, fitness, pes)
    six type indexes (DODI MARADMIN MCO NAVMC SECNAV USC)
    mos-manual-intro  mos-manual-lineage

Every policy page answers three questions on one page: **where it sits** (the
authority ladder above it, one tier at a time), **what came before** (four
version-history signals, each row naming which signal produced it), and **what
it says** (full text, with reference-list entries rendered as links to the
policy they name).

### The five spines

| spine | seed | tiers reached | edges |
|---|---|---|---|
| leave | MARADMIN-2023-129 | T0 T1 T3 T5 | 46 |
| promotion | MCO-1400.31D | T0 T1 T3 | 36 |
| mos | MARADMIN-2026-221 | T0 T3 T4 T5 | 50 |
| fitness | MARADMIN-2021-404 | T1 T3 T5 | 43 |
| pes | MARADMIN-2026-073 | T1 T3 T5 | 119 |

Tier ladder: T0 statute, T1 DoD, T2 DON, T3 service directive, T4 service
manual, T5 message, TX other. A tier the corpus does not hold is printed as a
stated gap, never skipped and never inferred.

### The headline findings, which fell out of the extraction

- **Three current MCOs cite DoDI 1308.3, cancelled March 2022.** Not compiled
  by hand - the drift report produced it.
- **MCO 1050.3J cites a 2005 DoDI two editions behind.**
- **The MOS spine names no DoD authority at all.** Stated as a gap.
- 85 of 362 edges are revision-drift findings. That is a currency report the
  corpus generates about itself.

---

## 4. Non-negotiable. Do not relax these without the owner saying so.

1. **`E:\GunnyBot\canonical` is the store of record and stays untouched.**
   17,514 documents. Results land in `canonical_staging`. Promotion out of
   staging is an owner decision under `[ID2]` and has not been made.
2. **`publication.publishable == false` records are never exported, rendered,
   or ingested.** Seven Statement C records are quarantined in the parent
   corpus. `export_issuance.py` reports `quarantined 0` here because none of
   the seven is in this 56-document set - that is not permission to relax the
   gate.
3. **Contact masking defaults ON in every export.**
4. **Every machine-produced value is stamped `UNVERIFIED`.** Verification is an
   explicit recorded promotion, never a default and never a side effect of a
   tool running.
5. **`cited` and `inferred` are never conflated.** `cited` means the source
   text states the link. Every edge names the paragraph it was read from. No
   edge is written without one.
6. **A gap is stated, never closed.** Nothing is inferred from subject matter
   or numbering proximity.
7. **A cited edition is never silently upgraded.** When a document names an
   issuance since superseded, the edge keeps pointing at the edition the text
   names and reports the drift.
8. **`data/` is hand-encoded and verified. Nothing overwrites it.**
   `data/dodi-1327.06.uslm.xml` carries 51 provisions marked VERIFIED and is
   better than anything the pipeline produces for that document. The two tiers
   use different namespaces on purpose:

   | | namespace | schema |
   |---|---|---|
   | `data/` | `.../ns/uslm/1.0` | `usmc-issuance-1.0.xsd` |
   | `data/exports/` | `.../ns/usmc-issuance/2.0` | `usmc-issuance-2.0.xsd` |

   2.0 exists because 1.0 asked one `@status` attribute to carry two unrelated
   facts - it wrote `UNVERIFIED` on the root while the companion authority
   graph wrote `active` for the same document. 2.0 separates `@lifecycle` from
   `@verification`. A document can be active and UNVERIFIED. Most are.

---

## 5. What this project does not claim

**Not USLM conformance.** USLM's own scope statement is that it "is not
intended to model executive branch or judicial branch documents," and since
2.1 a USLM document may not carry foreign-namespace elements. The XML here is a
**sibling** vocabulary in its own namespace. Correct phrasing: "follows United
States Legislative Markup conventions, extended to service issuances."

**Not NIEM conformance.** The NIEM Naming and Design Rules foreclose it - only
namespaces, schema documents, models, and messages can conform, never a system.
`conformance-matrix.md` section 6 carries the documented "consider NIEM first"
assessment DoDI 8320.07 requires. It is discharged; do not redo it.

**Not an official reference.** The issuing authority's copy governs. Statute
and DoD records here are metadata-grade - identity, dates, supersession, and
reference lists transcribed from the authoritative source, section text not
ingested. Every one says so on its face.

---

## 6. Run it

```
cd D:\Coding\policy-as-data
./build.sh
```

Fifteen stages, roughly 56 seconds. Order is load-bearing in one place: stage 2
`reparse_provisions` strips the minted tier records back to zero provisions
because they carry metadata rather than text, and stage 3
`ingest_authority_tiers` re-mints them. Reversing those two loses the statute
and DoD provisions silently.

Stage 14 `verify_authority` must report PASS before anything is shown. It
checks four things against the record rather than against the tool that wrote
it: does every provision's text appear in its section, does every edge name a
real source paragraph containing the target's number, does every edge resolve
as marked, is every edge cited rather than inferred.

**Prove idempotency by hashing, not by counts.** Counts matched for weeks while
the corpus changed underneath them.

```
find canonical -name '*.json' | sort | xargs md5sum > /tmp/a
./build.sh
find canonical -name '*.json' | sort | xargs md5sum > /tmp/b
cmp /tmp/a /tmp/b
```

### Opening the site

Served, for everything:

```
cd D:\Coding\policy-as-data\docs
python -m http.server 8000
```

From the folder, if that is all there is: every page, link, diagram, chain,
network, and full policy text works. Only search needs the server, and it says
so rather than hanging - browsers refuse `fetch()` for `file:` URLs.

---

## 7. Open decisions - the owner's, not yours

1. **The `[ID2]` promotion.** `E:\GunnyBot\promotion_report.md` is the sheet:
   16 records with moved provision paths, 21,315 rewritten identifiers, 11 new
   top-tier records. None of it is in `E:\GunnyBot\canonical`. Approving brings
   GunnyBot's store into line with what this project publishes. Declining is
   legitimate but makes this corpus the only place the corrected records exist,
   and that should be a decision rather than a drift.

2. **The period ruling, in the verified tier.** The machine tier is fixed:
   `/us/dod/don/usmc/mco/1050_3j`, because USLM reserves the period for the
   manifestation suffix and `mco/1050.3j` resolves as document `mco/1050` in
   format `3j`. The hand-encoded tier still uses periods, including inside
   provision paths (`/us/dod/dodi/1327.06/s1/1.1`). Applying the ruling there
   means rewriting hand-verified files. `tools/normalize_identifiers.py` does
   it and writes a dated corrections entry, but it is not a scripted call.
   Until then the two tiers use different identifier grammars, which is stated
   rather than hidden.

3. **SemperScribe integration.** Option A - `tools/nldp_to_canonical.py`, a
   bridge in this pipeline that reads SemperScribe's Naval Letter Data Package
   JSON and emits a canonical record. Zero changes to SemperScribe, fastest,
   keeps XSD logic in one place. Option B is native TypeScript export in
   SemperScribe, better long-term, duplicates the logic. A is recommended
   first. Neither is built.

4. **Delete seven folders.** The bridge that reaches the disk can move files
   but cannot remove them.

   ```
   D:\Coding\policy-as-data\.git\_to_delete\             a stale index.lock  <- first
   D:\Coding\policy-as-data\docs\search\_to_delete_t\    76 MB, 1,332 stale shards
   D:\Coding\policy-as-data\docs\_to_delete\             7 superseded pages
   D:\Coding\policy-as-data\tools\_to_delete\            3 retired tools
   D:\Coding\policy-as-data\data\exports\_to_delete\     14 stale .uslm.xml
   E:\GunnyBot\demo_site\_to_delete\                     3 scratch files
   E:\GunnyBot\repo_push\data\exports\_to_delete\
   ```

   The `.git` one first: a stale `index.lock` makes the next git command fail
   with "Another git process seems to be running."

---

## 8. Before the first commit

`git status` reports dozens of modified files nobody touched, including the
whole hand-encoded verified tier. It is line endings. The working tree is CRLF,
`core.autocrlf` is unset, files written from a Linux environment arrive with
LF. Proof:

```
git diff --ignore-cr-at-eol -- data/dodi-1327.06.uslm.xml README.md
```

returns nothing. A `.gitattributes` is in place. Sequence:

```
rmdir /s .git\_to_delete
git checkout -b authority-chain
git add .gitattributes
git commit -m "Settle line endings"
git add --renormalize .
git add -A
git commit -m "..."
```

Commit `.gitattributes` and renormalize **first**, or the real change arrives
buried in phantom whitespace and becomes unreviewable. Review the diff from
Windows git, not through a Linux view.

---

## 9. Known and unfixed

**Page weight.** `policy-NAVMC-1200.1L.html` is 3.5 MB - a 975-page manual with
13,595 addressable paragraphs. The text sits inside a collapsed disclosure so
nothing draws until asked. It is heavy on a phone.

**Two round-trip weld artifacts.** MCO 1050.3J `p-1-4` and NAVMC 1200.1L
`p-3-36` carry a paragraph whose text spans a page break, so it does not appear
contiguously in the source. Both reproduce identically under the previous
parser, so they are extraction artifacts rather than something this work
introduced. The verifier reports them as **warnings rather than failures**,
deliberately, so they stay visible without masking a real one.

**174 of 384 reference items unparsed.** The citation grammar covers ~24
issuance forms. The remainder are mostly prose references and forms not yet in
the grammar. They are counted and reported, not silently dropped.

**Fourteen documents carry no outbound edges.** Ten are statute or DoD records,
which is expected - they are the top of the ladder. `MARADMIN-2021-388`,
`MARADMIN-2022-408`, `MARADMIN-2025-166`, `MARADMIN-2026-074` are messages
whose references did not parse. Worth a look if edge coverage is the next
question.

**`config/revision_index.json` is a deliberate coupling.** 17,514 identifiers
derived from GunnyBot's corpus, **identifiers only** - no titles, no text, no
contacts. It exists for one purpose: deciding whether a cited edition has been
superseded. Judged against 56 records, drift collapsed to 17 findings
and the headline currency finding all but vanished. Judged against the index it
is 85 and correct. Regenerate when GunnyBot's corpus changes:

```
python -c "import os,json; json.dump(sorted(f[:-5] for f in os.listdir('canonical') if f.endswith('.json')), open('D:/Coding/policy-as-data/config/revision_index.json','w'))"
```

Dropping `--revision-index` from the build is the alternative. The tooling
handles its absence by reporting less rather than guessing, which is the right
failure.

---

## 10. Defect register - traps that already cost time

Do not re-find these. Each is fixed; each explains why a piece of code looks
the way it does.

### Parser

- **Reference (a) was being deleted.** `HDR_RX` matched `Ref:` and dropped the
  whole line, losing the first and often governing reference. `Ref:`/`Encl:`
  are now handled as region labels before `HDR_RX`.
- **Reference letters were parenting body paragraphs.** No scope reset, so
  `1. Situation` landed at `a/p1`. Separate `ref/` and `encl/` namespaces.
- **215 of 515 MCOs read as reference-free.** `Ref: See enclosure (1)`, with
  the list under a bare "References" heading. `REF_HEADING_RX`, gated on the
  items reading as citations.
- **Signature blocks parsed as provisions.** `K. M. IIAMS` scanned as an upper
  marker. `SIGNATURE_RX` - and the skip must **break the paragraph**, not just
  continue, or the text welds.
- **"designated in references:" opened a region mid-chapter** in NAVMC 1200.1L.
  `Reference`/`References` are deliberately NOT in `LABEL_RX`; only `Ref` is.
- **OCR `(l)` read as `(1)`**, colliding with genuine numbered items. Homoglyph
  repair, applied only when it matches the expected next letter, and recorded.

### Authority resolution

- **Chain short-circuiting.** Ranking on absolute tier let `Title 10, U.S.
  Code` jump T3 to T0 and hide the DoD instruction between them. Climb one tier
  at a time; smallest ascent wins.
- **Lateral step at the wrong tier.** DoDI 1320.14 to DoDI 1300.19 consumed the
  clarification allowance. Lateral is restricted to T5.
- **Change package misread as drift.** Citing `MCO 6110.3A` when the store
  holds `MCO-6110.3A-CH4` is not drift. Strict suffix match.
- **HELD vs DRIFT are judged against different sets.** HELD against
  `store_ids` - what this project actually has. DRIFT against
  `known_revisions` - what exists in the world. Conflating them was what
  collapsed drift from 82 to 17 after extraction.

### Output

- **XML attribute values were unsanitized.** A form feed in a distribution
  statement produced an unparseable file. `attr()` runs `XMLSAFE_RX` on every
  value.
- **The extractor was not idempotent** - it appended to its own prior output.
  Every stage now removes its own prior output before writing.
- **Curated family prefix false positive.** MCO 1200.18 folded into the MOS
  Manual family by prefix match. `_scheme_ids()` reconstructs exact ids from
  the manifest.
- **SVG letterboxing.** viewBox plus `width:100%` plus a fixed `height`
  attribute. Drop the height.

### The site

- **Search indexed the wrong corpus.** 17,507 documents against 57 pages, links
  built as `doc.id + ".html"` - roughly 99.7% of every result set was a link to
  nothing. A search box that mostly dead-ends teaches a visitor the library is
  broken rather than that it is small. `build_search.py` now generates from
  this corpus and builds `policy-<ID>.html`.
- **Inherited shards omitted term frequency when it was 1**, so the client
  parsed `undefined` and scored `NaN`. Frequency is always written explicitly.
- **Search hung forever on `file://`.** Browsers refuse `fetch()` for file URLs
  and there was no `.catch`, so the promise rejected into silence. A hang reads
  as a broken site; a message reads as a missing server. It now detects the
  protocol and says so.
- **The CPIB pair was stranded.** MARADMIN-2021-360/388 - the chapter-and-verse
  showcase `how-it-works.html` describes at length - were not in the extracted
  corpus. Both are in now.
- **Checker false alarms.** It matched the JavaScript assignment
  `a.href = "policy-"` as an HTML attribute; the regex now refuses a match
  preceded by a dot or word character. And it reported `_to_delete` files as
  orphans; those folders are skipped.

### Integrity, fixed 2026-08-04

Three defects of the same shape - a build reporting success while quietly
changing what it should not.

- **Torn records on interrupt.** Records were written in place, so an
  interrupted build left truncated JSON. `NAVMC-1200.1L.json` was found at
  1,318,799 of 9,173,894 bytes - a valid-looking file that would not parse.
  `tools/atomicio.py` writes to a temp file in the same directory, fsyncs, and
  renames over the target. It catches `BaseException` rather than `Exception`
  deliberately: `KeyboardInterrupt` is the case it exists for and does not
  inherit from `Exception`.
- **Corrections arrays counted builds, not changes.** Three tools appended an
  entry every run; the corpus had accumulated **361** identical
  `normalize_identifiers.py` entries across 42 records. That is the field a
  reader uses to adjudicate the `[ID2]` promotion. `tools/corrections.py` now
  replaces a tool's own prior entry, keyed on the `"<tool>.py - "` prefix the
  first change line already carried, so no schema change and no migration.
  Count is 43 - 42 records plus one.
- **Eleven top-tier records rewritten by the clock.**
  `ingest_authority_tiers.py` stamped `extracted_at` and `converted_at` from
  `datetime.now()`, so the statute and DoD spine changed on every build with no
  changed content. The stamp is now the literal
  `ENTERED = "2026-08-03T00:00:00+00:00"`, bumped by hand when the `RECORDS`
  table is edited and only then.

None changed a published fact. All three made the build dishonest about what it
had done, which is the more expensive kind of defect here, because the whole
claim of this project is that its provenance can be trusted.

---

## 11. Environment - the bridge to the user's disk

The session reaching `D:` and `E:` runs in a cloud container. The user's disk
is reached through a device bridge with hard limits, all of which have already
bitten:

- **45-second cap per command.** `build.sh` takes ~56 seconds and cannot run as
  one invocation through the bridge. Run the stages individually, or run it
  natively on Windows.
- **Background jobs do not survive.** `setsid nohup ... &` is killed when the
  call returns. Confirmed twice.
- **The bridge cannot delete.** `rm` fails with "Operation not permitted". Move
  to a `_to_delete/` subfolder and tell the user.
- **Staging can serve a stale cached copy** after an edit. Verify with `grep`
  or `md5sum`, or copy to a new filename.
- **Running git through the bridge leaves a `.git/index.lock`** it cannot
  unlink.
- **`device_commit_files` needs the real Windows path** (`D:\Coding\...`), not
  the Linux mount path.

---

## 12. The line with GunnyBot

**GunnyBot is the factory** - acquisition, extraction, the corpus at scale.
`E:\GunnyBot`, ~17,500 documents. Nothing was removed from it.

**policy-as-data is the standard and the product** - the schema, the
vocabulary, the encoding disciplines, the renderers, the demonstration corpus,
the site.

A tool belongs to whichever side owns the question it answers. "How do I turn a
PDF into a record" is GunnyBot's. "What does a record mean, and how is it
rendered, exported, and verified" is this project's. For the tools this project
owns, change them **here** and copy back, not the reverse.

**One tool is forked on purpose.** `build_search.py` exists on both sides and
they are not the same tool. GunnyBot's indexes 17,514 documents; this one
indexes 56 and builds links as `policy-<ID>.html`. Copying either over the
other breaks search on that side.

**Two tools were deliberately left behind.** `find_implementers.py` and
`promotion_report.py` are meaningless against 56 documents.

**`prototypes/editor.html` is retired, not in progress.** Ruling of 2026-07-19:
"Keep it only as a reference sketch; do not develop it further." SemperScribe
supersedes it. It is deliberately not in `docs/`.

**`branding/` is inherited, not owned.** The source of truth is
`src/app/globals.css` in the SemperAdminPortal repo. Read-only here.
