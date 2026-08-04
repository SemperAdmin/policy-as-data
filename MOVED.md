# What moved into policy-as-data, and what deliberately did not

Date: 2026-08-04. Source `E:\GunnyBot`. Destination `D:\Coding\policy-as-data`.

Nothing was overwritten in the hand-encoded verified tier. Nothing was deleted -
retired files were moved to `_to_delete/` folders because the tooling reaching
your disk cannot delete, and you should be the one to confirm.

---

## The finding that shaped the move

The repo already carries a hand-encoded VERIFIED tier in `data/`, and it
overlaps the demo set almost exactly:

    data/dodi-1327.06.uslm.xml     51 provisions VERIFIED, 1 UNVERIFIED
    data/mco-1050-3J.uslm.xml
    data/usc-10-701.uslm.xml
    data/dtm-23-001.uslm.xml
    data/maradmin-051-23.uslm.xml
    data/maradmin-129-23.uslm.xml

The whole leave spine is in there, hand-confirmed, with section and paragraph
structure taken from the source document.

**Those files are better than what the pipeline produces for the same
documents.** My DoDI 1327.06 record is metadata-grade - identity, dates,
supersession, and the reference list, with no section text. The repo's is
hand-verified against the issuance. Overwriting it with machine output would
have been a straight downgrade.

So the two-tier split the repo analysis called for is now physical:

    data/                 the VERIFIED tier. Hand-encoded, 1.0 namespace.
                          Untouched by this move.
    data/exports/         the UNVERIFIED tier. Machine-produced, 2.0
                          namespace. Replaced by this move.

---

## Moved in

### tools/ - 18 files

The pipeline, in run order.

    provisions.py             provision parser (reference-list and signature fixes)
    profile_readability.py    document category classification
    reparse_provisions.py     rebuild provision trees from stored section text
    ingest_authority_tiers.py mint the statute and DoD records
    authority.py              citation grammar, 24 issuance forms
    extract_authority.py      write cited edges from reference blocks
    normalize_identifiers.py  remove the period USLM reserves
    backfill_subjects.py      recover Subj: from naval letter front matter
    find_implementers.py      find implementing messages by reading REF/NARR/AMPN
    lineage.py                assemble version history from four signals
    render_authority_chain.py the five spine pages
    render_policy.py          integrated policy pages and type indexes
    render_connections.py     the network view
    render_sources.py         the provenance page
    export_issuance.py        usmc-issuance 2.0 XML
    emit_dcat.py              DCAT-US 3.0 catalog
    verify_authority.py       adversarial check
    promotion_report.py       the identity-change adjudication sheet

### schema/

    usmc-issuance-2.0.xsd        the published vocabulary the exports validate against
    policy_document.schema.json  the canonical store contract, 0.5.0

### config/

    spines.json               spine definitions, seeds, gap statements, preferences
    spine_set.txt             the 43 documents in scope
    mos-family-manifest.json  the curated MOS Manual family, 32 editions

### data/exports/ - 9 files, all schema-valid

Replaces the stale `.uslm.xml` set, which predated the provision parser and
carried no provision tree at all.

    DODI-1327.06  DODI-1327.6  USC-T10-S701  MCO-1050.3J
    MARADMIN-2023-051  MARADMIN-2023-129
    MARADMIN-2018-011  MARADMIN-CANX-2018-011  MARADMIN-2018-161

The first four plus the two 2023 messages form a complete authority chain,
statute to message, every link cited to the paragraph that states it.

### docs/ - 75 pages, 9.8 MB

The demonstration site. 54 integrated policy pages, 6 type indexes, 5 authority
chain pages plus their index, the connections network, the sources page, the
policy index, and the updated home and how-it-works pages.

### Root

    conformance-matrix.md   verdicts against every reference, with the text each turns on
    NAMESPACES.md           the identifier register and the period ruling
    BUILD.md                build state, how to run it, what needs a decision
    build.sh                thirteen stages in the only order that works
    docs/data.json          the DCAT-US 3.0 catalog record

---

## Second pass, 2026-08-04 - the last three folders

You named six folders as holding demo detail: `schema`, `repo_push`, `editor`,
`canonical_staging`, `briefing_visuals`, `branding`. Three were already
accounted for. Three were not, and are now.

### `branding/` - moved in, with its ownership stated

    branding/SEMPER-STYLE-GUIDE.md   the v1.2 token set
    branding/semper-logo.jpg         the emblem
    branding/README.md               new

This project does **not** own the visual system. The guide states its own
provenance on line 3: the source of truth is `src/app/globals.css` in the
SemperAdminPortal repo, and this file is a mirror. Treat it as read-only, or
the two drift and neither is authoritative.

Two files the guide names are not here and were not in the folder it came from:
`semper-tokens.css` and `semper-tokens.json`. Stated in the README rather than
reconstructed from the tables, because a third copy with no authority behind it
is worse than a missing one.

`docs/semper-logo.jpg` is the deployed copy and is byte-identical
(`1895252971f8265ca10e67b736f1035e`). Replacing the emblem means replacing
both.

### `prototypes/editor.html` - moved in as a reference sketch, not as a page

`editor.html` is a working single-page editor that generates every paragraph
path, printed label, and citation number from position - the drafter never
types a number. **It was retired on 2026-07-19** and the ruling is explicit in
`semperscribe-integration.md`: "Keep it only as a reference sketch; do not
develop it further."

SemperScribe supersedes it and does the same job properly - MCO 5215.1K
numbering including the 4-digit chapter mapping, directive templates with
mandatory Situation / Mission / Execution / Cancellation paragraphs,
mandatory-paragraph locking, portion marking, DOCX and PDF export, 51 test
suites.

So it goes to `prototypes/`, **not** `docs/`. Shipping a retired prototype as a
live site page would misrepresent what this project offers, and its header
links resolve only as siblings of `index.html` anyway. It also calls
`confirm()`, which no page under `docs/` does.

What it proved does carry forward: SemperScribe level N and this pipeline's
depth N-1 are the same SECNAV correspondence ladder, arrived at independently.
That is the hardest thing to get right in directive XML, and it means the seam
between authoring and this project is one export module -
`tools/nldp_to_canonical.py`, still unbuilt.

### `briefing_visuals/` - already here, nothing to move

All five SVGs are byte-identical to `docs/visuals/`. Verified rather than
assumed:

    01-paragraph-as-data.svg   02-identifier-anatomy.svg
    03-chapter-and-verse.svg   04-pipeline-and-gates.svg
    05-authoring-loop.svg

A second copy would be a second thing to keep in step. Recorded here so the
absence reads as a decision rather than an oversight.

### What stayed on the GunnyBot side, and why

`E:\GunnyBot\tools\render_site.py` reads `briefing_visuals/` at line 821 and
picks up a brand asset from `branding/` at line 668. Both folders are live
dependencies of GunnyBot's own site renderer, so the originals stay where they
are. Copies here, nothing removed there - the same line the rest of the
extraction holds.

---

## Retired, not deleted

    tools/_to_delete/export_uslm.py        superseded by export_issuance.py
    data/exports/_to_delete/  14 files     the stale .uslm.xml and .authority.jsonld set

Delete those two folders yourself once you have looked.

---

## Deliberately NOT moved

**`data/*.uslm.xml`, the verified tier.** Untouched, for the reason above.

**The canonical store and `canonical_staging`.** That is GunnyBot's internal
format. The repo consumes XML, and shipping 54 JSON records including a 9 MB
MOS Manual would put the factory's working state into a repository that exists
to publish the product.

**`store_ids.json` and `implementers.json`.** Build state describing the
private corpus - a 17,517-entry id list and a scan cursor. Neither is a
deliverable and neither belongs in a public repository.

**`promotion_report.md` and `authority_report.json`.** They describe pending
changes to the GunnyBot store, not to this repo. They live where the decision
lives.

---

## Read this before you run git

Two things happened because git was run through the bridge's Linux view of a
Windows working tree. Both are handled, but you should know.

**A stale `.git/index.lock` was created and is now moved to
`.git/_to_delete/`.** Git leaves that lock when a command is interrupted, and
the bridge could not unlink it. Had it stayed, your next Windows git command
would have failed with "Another git process seems to be running." Delete
`.git/_to_delete/` and you are clear.

**`git status` reports 57 modified files that nobody touched**, including the
whole hand-encoded verified tier. It is line endings, not content. The working
tree is CRLF, `core.autocrlf` is unset, and files written from a Linux
environment arrive with LF, so every line reads as changed. Proof:

    git diff --ignore-cr-at-eol -- data/dodi-1327.06.uslm.xml README.md

returns nothing. The content is byte-identical apart from the terminator.

A `.gitattributes` is now in place setting `* text=auto` with explicit `eol=lf`
for every format in the repo, which settles this permanently. After you commit
it, run

    git add --renormalize .

once, so the index and the working tree agree and the phantom diffs stop.

Review the diff from Windows git rather than through any Linux view, and use
`--ignore-cr-at-eol` while the renormalize is still pending.

---

## Three things to settle before you commit

### 1. The identifier period, in the verified tier

`NAMESPACES.md` records the ruling that USLM reserves the period for the
file-format suffix, so `/us/dod/dodi/1327.06` is ambiguous - it reads as
document `/us/dod/dodi/1327` in format `06`. The machine tier is fixed.

**The hand-encoded tier is not.** It uses periods throughout, including inside
provision paths:

    identifier="/us/dod/dodi/1327.06/s1/1.1"

Applying the ruling there means rewriting hand-verified files, which is your
call and not a scripted one. `tools/normalize_identifiers.py` does the work if
you want it, and it writes a dated corrections entry for every record it
touches. Until then the two tiers use different identifier grammars, and that
inconsistency should be stated in the README rather than left to be found.

### 2. Two namespaces coexist

    data/          https://policy.usmc.mil/ns/uslm/1.0        usmc-issuance-1.0.xsd
    data/exports/  https://policy.usmc.mil/ns/usmc-issuance/2.0  usmc-issuance-2.0.xsd

2.0 exists because 1.0 asked one `@status` attribute to carry two orthogonal
facts - it wrote `UNVERIFIED` on the root while the companion authority graph
wrote `active` for the same document. 2.0 separates `@lifecycle` from
`@verification`. Keep `usmc-issuance-1.0.xsd` regardless; deleting it orphans
every file already published against it. Mark it superseded in
`schema/README.md` rather than removing it.

Note the 1.0 namespace string contains `uslm`. Given that USLM excludes
executive branch documents by design, that string invites the conformance claim
`conformance-matrix.md` shows is not available. 2.0 drops it.

### 3. `docs/search` is 78 MB and already tracked

935 files, pre-existing, nothing to do with this move. Worth knowing before you
push, because it dominates the repository.

---

## Suggested commit

    cd D:\Coding\policy-as-data
    rmdir /s .git\_to_delete
    git checkout -b authority-chain
    git add .gitattributes
    git commit -m "Settle line endings"
    git add --renormalize .
    git add -A
    git commit -m "usmc-issuance 2.0: provision trees, cited authority edges, statute-to-message chain, integrated site"

Commit `.gitattributes` first and renormalize before anything else, or the
addition arrives buried in 57 files of phantom whitespace and the real change
becomes unreviewable.

Then look at the three `_to_delete/` folders - `tools/`, `data/exports/`, and
`.git/` - and remove them in a separate commit, so the retirement is legible in
history rather than mixed into the addition.
