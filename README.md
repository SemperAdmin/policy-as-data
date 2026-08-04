# policy-as-data

Recasting Marine Corps policy as structured data, the way Congress publishes
statute as [USLM](https://github.com/usgpo/uslm) XML.

The product is the **encoding itself**: a faithful, addressable representation
of an issuance where every provision has a stable identifier, and where the
authority a policy rests on can be walked, one cited link at a time, up to the
Department of Defense instruction or the statute behind it.

This is a standalone project. It carries its own corpus, its own tooling, and
its own build. Nothing else needs to be present.

```
./build.sh
```

Fifteen stages, every one idempotent. Running it twice leaves all 56 records
and every rendered file byte-identical, because each stage removes its own
prior output before writing. That is measured by hashing, not asserted from
matching counts.

---

## What is here

```
canonical/          56 documents, the corpus of record for this project
config/             spine definitions, the curated MOS family, the id indexes
schema/             the JSON contract and the published XSD
tools/              the pipeline, 23 scripts
prototypes/         editor.html, retired 2026-07-19, kept as a reference sketch
branding/           the style guide and emblem, mirrored from SemperAdminPortal
data/               the VERIFIED tier, hand-encoded (see Two tiers)
data/exports/       the UNVERIFIED tier, machine-produced XML
docs/               the rendered site, served by GitHub Pages
viewer/             the read-only document viewer
```

`canonical/` is not published. Those records carry contact details
transcribed from the source issuances, and masking happens at the export
boundary rather than in the store, so the store stays a faithful record and the
repository stays free of personal contact data. A clone therefore carries the
standard, the schema, the tooling, and the masked exports, but not the store the
exports were produced from. That is a stated gap, not an oversight.

## Two tiers, and why they are kept apart

`data/` holds documents encoded **by hand and confirmed against the source**.
`data/dodi-1327.06.uslm.xml` carries 51 provisions marked VERIFIED. That file
is better than anything a pipeline produces for the same document, and nothing
here overwrites it.

`data/exports/` holds **machine output**, every provision stamped UNVERIFIED
because no human has confirmed it line by line. Promotion from one tier to the
other is explicit and recorded. It is never silent, and it never happens by a
tool running.

The two tiers use different namespaces, on purpose:

| | namespace | schema |
|---|---|---|
| `data/` | `https://policy.usmc.mil/ns/uslm/1.0` | `usmc-issuance-1.0.xsd` |
| `data/exports/` | `https://policy.usmc.mil/ns/usmc-issuance/2.0` | `usmc-issuance-2.0.xsd` |

2.0 exists because 1.0 asked one `@status` attribute to carry two unrelated
facts. It wrote `UNVERIFIED` on the root element while the companion authority
graph wrote `active` for the same document, so two published artifacts
contradicted each other. 2.0 separates `@lifecycle` (is the policy in force)
from `@verification` (has a human confirmed the extraction). A document can be
active and UNVERIFIED. Most are.

## What the site shows

`docs/index.html` is the entry point. Every policy opens on one page carrying
all three of the questions a reader actually has:

- **Where it sits** — the authority ladder above it, one tier at a time, and
  the traffic below that names it. A tier the corpus does not hold is printed
  as a stated gap rather than skipped.
- **What came before** — editions, change packages, supersession, and reverse
  drift, with every row naming which of the four signals produced it.
- **What it says** — the full text, and a reference list where each entry is a
  **link to the policy it names**, not a string.

Alongside those: five authority chain pages tracing a spine from statute to
message, a connection network showing all 56 documents and 362 cited
references, six indexes by issuance type, and a sources page recording what the
concept was built from and what was taken from each.

## The disciplines this repository holds itself to

**Cited and inferred are never conflated.** Every relationship carries its
basis. `cited` means the source text states the link. `inferred` means
resolution or hierarchy derived it. No edge is written without naming the
paragraph it was read from.

**A gap is stated, never closed.** Where the corpus does not hold a tier, the
page says so and says why. Nothing is inferred from subject matter or from
numbering proximity.

**A cited edition is never silently upgraded.** When a document names an
issuance that has since been superseded, the edge keeps pointing at the
edition the text names and reports the drift. 85 of the 362 edges are drift
findings — a currency report that falls out of the extraction rather than
being compiled by hand.

**Machine output is UNVERIFIED until a human says otherwise.** Verification is
a promotion, and it is recorded.

**The identifier excludes the period.** USLM reserves it for the file-format
suffix, so `/us/dod/don/usmc/mco/1050.3j` would resolve as document
`mco/1050` in format `3j`. Machine identifiers use `mco/1050_3j`; a reader
still sees MCO 1050.3J everywhere. `NAMESPACES.md` is the register and the
ruling.

## What this repository does not claim

**Not USLM conformance.** USLM's own scope statement is that it "is not
intended to model executive branch or judicial branch documents," and since
version 2.1 a USLM document may not carry foreign-namespace elements. The XML
here is a **sibling** vocabulary in its own namespace. The correct phrasing is
"follows United States Legislative Markup conventions, extended to service
issuances."

**Not NIEM conformance.** The NIEM Naming and Design Rules foreclose it
outright: only namespaces, schema documents, models, and messages can conform,
never a system. `conformance-matrix.md` section 6 carries the documented
"consider NIEM first" assessment that DoDI 8320.07 requires.

**Not an official reference.** The issuing authority's copy governs. Statute
and Department of Defense records here are metadata-grade — identity, dates,
supersession, and reference lists transcribed from the authoritative source,
with section text not ingested. Every one of them says so on its face.

## Documentation

**Start here if you are new to the project.** `SESSION_HANDOFF.md` is the
context transfer: what this is, where it stands measured rather than asserted,
the constraints that are not yours to relax, the decisions still open, and a
register of every defect already found so none of them is re-found.

| | |
|---|---|
| `SESSION_HANDOFF.md` | the whole project in one read, for a reader with no context |
| `BUILD.md` | build state, what each stage does, what needs a decision |
| `conformance-matrix.md` | verdicts against every standard and issuance, with the text each turns on |
| `NAMESPACES.md` | the identifier register, the allocated tokens, the period ruling |
| `DATA_CONTRACT.md` | the read-only mandate for anyone touching the encoding |
| `MOVED.md` | how this project was extracted from its parent, and what stayed behind |
| `HANDOFF.md` | the line between this project and GunnyBot, and the one forked tool |
| `VERIFICATION.md` | whether the demo actually works, and the defects found proving it |
| `schema/README.md` | schema design, identifier scheme, verification semantics |

## Provenance

This project was extracted from GunnyBot, a policy ingestion pipeline holding
roughly 17,500 documents. GunnyBot keeps the factory — acquisition, extraction,
and the full corpus. This project owns the standard, the schema, the renderers,
the demonstration corpus, and the site.

`config/revision_index.json` is the one artifact that still reflects the larger
corpus: an index of document identifiers known to exist. It is used for exactly
one purpose, deciding whether a cited edition has been superseded. Whether an
edition is current is a fact about the world, not about how many documents this
project happens to hold, and without the index a 56-document project would
report nearly every drift finding as "never held" and lose it.
