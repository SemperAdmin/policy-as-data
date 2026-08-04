# Policy as Data - Build State

Date: 2026-08-03. Owner: Stephen. Store of record: UNTOUCHED.
Everything below lands in `canonical_staging` and awaits one owner ruling.

---

## What exists

A Marine can open a July 2026 promotion message and walk up to the statute
behind it, one cited link at a time, with every gap in the chain stated rather
than closed.

    demo_site/index.html                the hub
    demo_site/policy-index.html         every document, one page each
    demo_site/policy-<ID>.html          54 integrated policy pages
    demo_site/authority-index.html      tier coverage across five spines
    demo_site/authority-leave.html      statute to clarification message
    demo_site/authority-promotion.html
    demo_site/authority-mos.html
    demo_site/authority-fitness.html
    demo_site/authority-pes.html
    demo_site/connections.html          the whole network as one picture
    demo_site/type-<TYPE>.html          6 indexes, one per issuance type
    demo_site/sources.html              what this was built from
    demo_site/mos-manual-lineage.html   the 25-year worked example

82 pages in all.

### Every policy carries its full text

Each policy page now renders the complete document, every section in order,
not a sample. A section the parser refused - a table, a flattened extraction -
renders as source text, labelled, rather than being dropped. Silently omitting
the sections that would not parse is how a library ends up showing the
parseable part of a policy and calling it the policy.

The MOS Manual page carries 13,595 addressable paragraphs across 967 sections
and weighs 3.5 MB. That is a 975-page manual. It sits inside a collapsed
disclosure so nothing renders until a reader asks for it.

### The connections view

`connections.html` answers the question no single document page can: what does
the corpus look like as a whole, and where is it thin.

54 documents on a tier axis - statute at the top, messages at the bottom -
joined by 351 cited references. 57 join two documents inside the set. 74 name
an edition the store no longer holds. 128 name a document it never held, drawn
as dashed stubs running off the edge of what was collected. Seven documents
have no cited connection to any other in the set, which is a statement about
the demonstration set rather than about the policies.

Drawn as inline SVG with no script and no external dependency, so it works
from a file:// URL and prints. Tier is the vertical axis rather than a physics
simulation, because the one thing a reader needs from the picture is which
level issued a document. Node size is connection count, so the hubs are
visible without reading a title.

An SVG network is invisible to a screen reader however well it is labelled, so
every connection in the figure is also emitted as a table below it.

### The integrated policy page

Until now the library answered each question on a different page. What does
this order say, what governs it, and what came before it are not three
questions to a reader holding one. Each policy now opens on a single page
carrying all three:

    WHERE IT SITS      the authority ladder above, one tier at a time, with
                       stated gaps; and the traffic below that names it
    WHAT CAME BEFORE   editions, change packages, supersession, and reverse
                       drift, each row saying which signal produced it
    WHAT IT SAYS       the reference list where every item is a LINK to the
                       policy it names, then the provision tree

The third section is where the concepts join. Clicking reference (h) in
MCO 1050.3J lands on the DoD instruction that governs leave. The document, its
place in the hierarchy, and its history, addressable to the paragraph.

Across the 54 pages: 1 curated family, 5 with multiple editions or change
packages, 10 with supersession, 8 cited as an edition the store no longer
holds.

### Version history comes from four signals, not one

There is no field that answers "what came before this," because the corpus
holds one edition of most policies - a superseded edition is usually gone from
the publisher's site before a scraper reaches it. So the timeline is assembled
from four independent sources, and every row states which one produced it:

    1 CURATED FAMILY    a manifest declaring documents under different
                        identifiers are one policy. The MOS Manual changed
                        identifier scheme three times in 25 years, so nothing
                        derivable could ever link its 32 editions.
    2 CHANGE PACKAGES   separate records for one edition. MCO P1400.32D
                        carries CH-1 and CH-2.
    3 SUPERSESSION      supersedes and superseded_by, each with its basis.
    4 REVERSE DRIFT     documents citing an edition the store no longer holds.
                        Nobody records this anywhere. It falls out of the
                        authority extraction, and it is often the only
                        surviving evidence an earlier edition existed.

The record's own corrections array is carried as a fifth track and kept
separate, because the history of the DATA is not the history of the POLICY.

### The sources page

`sources.html` states what the concept was built from and what was taken from
each: 18 sources in six groups, including the ones considered and set aside
with their reasons. A provenance page that lists only the influences that
worked is a marketing page. Its corpus counts are read from the store at
generation time so the page cannot drift from what the corpus holds.

| Spine | Chain | Tiers held | Edges |
|---|---:|---|---:|
| Parental Leave | 6 | T0 T1 T3 T5 | 46 |
| Officer Promotion | 3 | T0 T1 T3 | 36 |
| Occupational Classification | 4 | T0 T3 T4 T5 | 50 |
| Physical Fitness | 4 | T1 T3 T5 | 43 |
| Performance Evaluation | 3 | T1 T3 T5 | 119 |

Across the set: 54 documents, 351 cited edges, 149 resolving in store,
74 revision drift, 128 named but not held. Verification passes.

Machine outputs: 54 XML exports, all valid against the published XSD, carrying
20,088 provisions, 286 provision-level citations, and 367 authority edges. One
DCAT-US 3.0 catalog record.

---

## Run it

    ./build.sh

Fifteen stages, in the only order that works.

     1  refresh store_ids        the local id index, 56 records
     2  reparse_provisions       rebuild provision trees from section text
     3  ingest_authority_tiers   mint the 11 statute and DoD records
     4  extract_authority        write cited edges from reference blocks
     5  normalize_identifiers    remove the period USLM reserves
     6  backfill_subjects        recover the Subj: field from front matter
     7  render_authority_chain   five spine pages plus the index
     8  render_policy            56 integrated policy pages plus the index
     9  render_connections       the whole network as one picture
    10  render_sources           the provenance page
    11  export_issuance          usmc-issuance 2.0 XML, schema-validated
    12  emit_dcat                DCAT-US 3.0 catalog record
    13  build_search             the search index, from this corpus
    14  verify_authority         adversarial check, must report PASS
    15  check_site               every link lands, every page reachable

Stage 3 must follow stage 2 and precede stage 4. Reparse rebuilds provision
paths from stored section text and strips the minted tier records back to zero
provisions, because they carry metadata rather than text; stage 3 re-mints
them. Reversing the two loses the statute and DoD provisions silently.

Stage 14 must PASS before anything is shown. It checks four things against the
record rather than against the tool that wrote it: does every provision's text
appear in its section, does every edge name a real source paragraph containing
the target's number, does every edge resolve as marked, and is every edge
cited rather than inferred.

### Idempotent, and now actually proved

Running the build twice leaves all 56 records and every rendered file
byte-identical. That claim used to be asserted from matching counts. It is now
measured:

    find canonical -name '*.json' | sort | xargs md5sum > /tmp/a
    ./build.sh
    find canonical -name '*.json' | sort | xargs md5sum > /tmp/b
    cmp /tmp/a /tmp/b

Matching counts hid two defects that only a hash comparison finds, both fixed
on 2026-08-04 and both described under Standing items.

---

## The one decision that is yours

`promotion_report.md` is the sheet. 16 records have moved provision paths and
21,315 identifiers have been rewritten. Both are identity changes under
`[ID2]`, and nothing has entered the store of record.

Three causes, all corrections rather than preferences:

1. **Reference lists left the body tree.** They were parenting body paragraphs,
   so `1. Situation` was landing at path `a/p1`. They now live under `ref/` and
   `encl/`.
2. **Signature blocks stopped parsing as paragraphs.** `K. M. IIAMS` scanned as
   a lettered marker and everything after it nested underneath.
3. **Periods left the identifiers.** USLM reserves the period for the file
   format suffix, so `mco/1050.3j` resolved as work `mco/1050` in format `3j`.

If you approve, the sequence is in section 7 of the report. Back up `canonical`
first, then propagate supersession, then wire MCPEL status, then verify. Steps
3 and 4 are not optional - skipping them leaves statuses incomplete.

---

## What the build proves, in one line each

**Fitness.** MCO 6100.13A, MCO 6100.14, and MCO 6110.3A all cite DoD
Instruction 1308.3. It was cancelled in March 2022 by DoDI 1308.03. Three
current Marine Corps orders point at an issuance that has not existed for four
years, and the chain shows both editions with the cancellation between them.

**Leave.** MCO 1050.3J cites the 2005 edition of DoDI 1327.6. The current
1327.06, effective August 2025, absorbed DTM 23-001 - the memorandum MARADMIN
051/23 implements. The chain terminates at 10 U.S.C. 701, whose subsection (h)
is the statutory root of the parental leave program.

**Occupational Classification.** No document on this spine names any Department
of Defense authority anywhere in its printed reference lists. The MOS Manual
carries a DoD occupational conversion report requirement that names no issuance
number, so no edge is drawn. The page states the gap.

**Revision drift.** 74 edges cite an edition the store does not hold while
holding a different revision of the same base number. MCO 1400.31D cites
SECNAVINST 1421.3M; the store holds 1421.3N. That is a currency report the
corpus could not produce before.

---

## Conformance posture

Full matrix in `conformance-matrix.md`, namespace register in `NAMESPACES.md`.
Three sentences to get right in any briefing:

- **Never say "USLM conformant."** USLM's Objective annotation states it does
  not model executive branch documents. Say "follows United States Legislative
  Markup conventions, extended to service issuances."
- **Never say the system is "NIEM conformant."** NDR 6.0 forecloses it: only
  namespaces, schema documents, models, and messages can conform.
- **The DSPO Digital Standards Strategy is not a mandate.** "The guidance in
  the strategy is not intended to be prescriptive." Cite it as direction.

The argument that does hold, and it is the strongest one available: DoD
requires structured XML for technical manuals and DSPO has committed to
converting standards to XML, while policy issuances are still governed by Word
templates and a mandated Courier New 12. DoWI 5025.01 was reissued 20 January
2026, eight days after that strategy, with no machine-readability provision at
all. That inconsistency is stated in the Department's own documents.

---

## Standing items

**Fixed 2026-08-04, and worth knowing why they survived so long.** Three
defects, all of the same shape: a build that reported success while quietly
changing something it should not have.

*Torn records on interrupt.* Every tool that wrote a record wrote it in place,
so a build stopped part-way left a truncated JSON file. That is exactly what
happened to `NAVMC-1200.1L.json`: 1,318,799 of 9,173,894 bytes, a valid-looking
file that would not parse. `tools/atomicio.py` now writes to a temporary file
in the same directory, fsyncs, and renames over the target. Rename is atomic on
both filesystems, so an interrupted build leaves the previous record intact
rather than a fragment. It catches `BaseException` rather than `Exception`
deliberately - `KeyboardInterrupt` is the case the function exists for, and it
does not inherit from `Exception`.

*Corrections arrays that counted builds, not changes.* Three tools appended a
`corrections` entry every run. The corpus had accumulated **361**
`normalize_identifiers.py` entries across 42 records - one per build, all
identical, none describing a distinct change. Anyone reading a record to
adjudicate the `[ID2]` promotion would have been counting builds and calling
them changes. `tools/corrections.py` now replaces a tool's own prior entry
instead of appending, keyed on the `"<tool>.py - "` prefix the first change
line already carried, so no schema change and no migration was needed. The
count is back to 43, which is 42 records plus one. Hand-written entries and
entries from other tools keep their place.

*Eleven top-tier records rewritten by the clock.* `ingest_authority_tiers.py`
stamped `extracted_at` and `converted_at` with `datetime.now()` on every mint.
Those fields say when the metadata was hand-entered, which is a fact about the
entry and not about when the build ran. Every build therefore rewrote the
statute and DoD spine - precisely the records a reader checks for provenance -
and a diff of two identical builds showed eleven changed files with no changed
content. The stamp is now the literal `ENTERED = "2026-08-03T00:00:00+00:00"`,
bumped by hand when the `RECORDS` table is edited and only then.

None of the three changed a single published fact. All three made the build
dishonest about what it had done, which is the more expensive kind of defect
here, because this project's whole claim is that its provenance can be trusted.

**Needs a repo commit.** `repo_push/PUSH_NOTES.md` is rewritten for the
exporter rename. The nine-document curated set is exported and schema-valid at
`repo_push/data/exports/`. Stale `.uslm.xml` and `.authority.jsonld` files are
moved to `repo_push/data/exports/_to_delete/` - the device bridge cannot
delete, so remove that folder yourself.

**Needs reading before building.** LegalRuleML Core 1.0 is an OASIS Standard
with deontic operators, temporal validity, and provenance back to the
authoritative source text. That last property is the discipline this corpus
already practices. Read it before `rules.json` generalizes past parental leave.

**Worth considering.** S1000D carries an `infoCode` - a controlled vocabulary
of information KINDS, not subjects. A vocabulary of provision kinds
(requirement, definition, responsibility, procedure, exception) would make the
corpus queryable in a way subject keywords never will.

**Coverage.** The implementer scan covered the 6,000 newest messages of 14,018.
Resume with the same command; the state file continues where it stopped. The
build is scope-agnostic - widening past the five spines changes only
`spine_set.txt` and `spines.json`.

**Known and unfixed.** Two pre-existing round-trip weld artifacts remain, in
MCO 1050.3J p-1-4 and NAVMC 1200.1L p-3-36, where a page break joined text
across a boundary. Both reproduce identically under the old parser. They are
extraction defects, not authority defects, and the verifier reports them as
warnings rather than failures so they stay visible without masking a real one.

---

## Files

Added 2026-08-04: `tools/atomicio.py` (crash-safe record writes),
`tools/corrections.py` (a tool replaces its own correction entry rather than
appending), `tools/check_site.py` (link, asset, anchor, and orphan check),
`tools/build_search.py` (index built from this project's own corpus),
`branding/` (the mirrored style guide and the emblem, with a README recording
that SemperAdminPortal owns the tokens), `prototypes/editor.html` (the retired
authoring proof of concept, kept as a reference sketch and deliberately not in
`docs/`).

New tools this build: `authority.py`, `extract_authority.py`,
`ingest_authority_tiers.py`, `reparse_provisions.py`,
`render_authority_chain.py`, `verify_authority.py`, `find_implementers.py`,
`promotion_report.py`, `normalize_identifiers.py`, `emit_dcat.py`,
`export_issuance.py`, `backfill_subjects.py`, `lineage.py`,
`render_policy.py`, `render_sources.py`.

Changed: `provisions.py` (backup `.pre-p3-2026-08-03.bak`), the JSON schema at
0.5.0 (backup `.0.4.0.bak`), `demo_site/index.html`,
`demo_site/how-it-works.html`, `repo_push/PUSH_NOTES.md`.

Retired: `export_uslm.py` and the `.uslm.xml` extension.

Config as data: `spines.json`, `spine_set.txt`, `store_ids.json`,
`implementers.json`.

Documents: `conformance-matrix.md`, `NAMESPACES.md`, `promotion_report.md`,
`authority_report.json`, `top-down-linkage-baseline.md`,
`AUTHORITY_CHAIN_HANDOFF.md`.
