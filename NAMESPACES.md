# Namespace Register

Date: 2026-08-03. Owner: Stephen. Status: in force for the canonical store.
Companion to `conformance-matrix.md` and the N3.1 deliverable named in
`hhq-alignment-plan.md`.

This register exists because **GPO reserves nothing**. USLM defines `usc`,
`pl`, and `stat` in prose, uses `act` heavily in production without documenting
it anywhere, and operates no registry, no allocation procedure, and no
collision-resolution mechanism. Extending the `/us/...` space is therefore
neither permitted nor prohibited - it is undefined. Undefined means the burden
of documenting the extension falls on whoever makes it.

---

## 1. The identifier grammar in force

    /us / <department> / <service> / <doctype> / <number> [ / <provision-path> ]

Rules, each with its source:

| Rule | Statement | Basis |
|---|---|---|
| N1 | The first segment is always `us`, the ISO 3166-1 alpha-2 jurisdiction code, lowercase. | USLM: "The highest level of the hierarchy is always the jurisdiction code, specified using the ISO 3166-1 country code." |
| N2 | Every segment is lowercase. | USLM referencing nomenclature is case-insensitive; we normalize down for a single canonical form. |
| N3 | **No segment contains a period.** Periods in a directive number become underscores. | USLM reserves the period for the manifestation suffix. See section 3. |
| N4 | Permitted characters in a segment are `a-z`, `0-9`, `-`, `_`. | RFC 3986 section 2.3 unreserved set, minus the period per N3 and minus `~` as needless. |
| N5 | A provision path appends to the document identifier, one segment per level. | USLM: "append the reference to the document with '/' + the level designators." |
| N6 | Depth-0 numbered paragraphs take the `pN` form; deeper levels are the bare designator. | Matches the repo's hand-built corpus and USLM's small-level convention of bare designators. |
| N7 | Reference and enclosure lists occupy reserved first segments `ref` and `encl` in the provision space. | Local rule. The prefix carries the role, so no schema change was needed. |
| N8 | The identifier is a machine name. Document ids, native numbers, titles, and displayed text keep their periods. | A Marine writes MCO 1050.3J. The identifier is not shown to a reader. |

## 2. Allocated tokens

Every token below is allocated by this register and by nothing else. None is
reserved by GPO.

| Path | Tier | Doc types | Example |
|---|---|---|---|
| `/us/usc/t{N}` | T0 | USC | `/us/usc/t10` |
| `/us/usc/t{N}/s{section}` | T0 | USC | `/us/usc/t10/s701` |
| `/us/eop/eo/{number}` | TX | EO | `/us/eop/eo/14168` |
| `/us/dod/dodi/{number}` | T1 | DODI | `/us/dod/dodi/1327_06` |
| `/us/dod/dodd/{number}` | T1 | DODD | `/us/dod/dodd/4500_54` |
| `/us/dod/dodm/{number}` | T1 | DODM | |
| `/us/dod/dtm/{number}` | T1 | DTM | `/us/dod/dtm/23-001` |
| `/us/dod/reg/{number}` | T1 | DODREG | `/us/dod/reg/4515_13-r` |
| `/us/dod/fmr[/v{volume}]` | T1 | DODFMR | `/us/dod/fmr/v7a` |
| `/us/dod/cjcs/cjcsi/{number}` | T1 | CJCSI | |
| `/us/dod/don/secnavinst/{number}` | T2 | SECNAV | `/us/dod/don/secnavinst/1400_1d` |
| `/us/dod/don/secnavm/{number}` | T2 | SECNAVM | |
| `/us/dod/don/secnavnote/{number}` | T2 | SECNAVNOTE | |
| `/us/dod/don/opnavinst/{number}` | T2 | OPNAVINST | |
| `/us/dod/don/bumedinst/{number}` | T2 | BUMEDINST | |
| `/us/dod/don/navso/{number}` | T2 | NAVSO | |
| `/us/dod/don/usmc/mco/{number}` | T3 | MCO | `/us/dod/don/usmc/mco/1050_3j` |
| `/us/dod/don/usmc/mcbul/{number}` | T3 | MCBUL | |
| `/us/dod/don/usmc/navmc/{number}` | T4 | NAVMC | `/us/dod/don/usmc/navmc/1200_1l` |
| `/us/dod/don/usmc/mcrp\|mctp\|mcwp\|mcdp/{number}` | T4 | doctrine | |
| `/us/dod/don/usmc/maradmin/{year}/{seq}` | T5 | MARADMIN | `/us/dod/don/usmc/maradmin/2023/051` |
| `/us/dod/don/usmc/almar/{year}/{seq}` | T5 | ALMAR | |
| `/us/dod/don/usmc/alnav/{year}/{seq}` | T5 | ALNAV | |

Change and volume suffixes ride on the number segment with a hyphen:
`/us/dod/don/usmc/mco/6100_13a-ch5`.

## 3. Ruling - the period is not usable in a path segment

USLM User Guide section 12.2 composes a reference as
`[item][work][lang][portion][temporal][manifestation]` and defines the last
part:

> manifestation (". " prefix) - identifies the format as a simple file
> extension (".xml" for the XML file, ".htm" for HTML, and ".pdf" for the PDF).

Directive numbers carry periods natively, so the naive rendering produced

    /us/dod/don/usmc/mco/1050.3j

which a resolver following the published grammar reads as the work
`/us/dod/don/usmc/mco/1050` in the manifestation `3j`.

RULING: periods become underscores inside every path segment. The underscore is
in the RFC 3986 section 2.3 unreserved set, which the USLM 2.1 Review Guide
already requires for version strings, so the substitute is drawn from the
vocabulary the specification uses rather than invented.

Applied by `tools/normalize_identifiers.py`. 18,417 identifiers across the
spine set. This is an identity change under `[ID2]` and holds in staging until
adjudicated.

## 4. Ruling on rooting - `/us/dod/...` rather than `/us-dod/...`

Two defensible options existed.

- `/us/dod/don/usmc/...` treats the department as a level under the US
  jurisdiction. It reads as one hierarchy with `/us/usc/...`, so a single
  resolver can walk a citation from a Marine Corps order to a statute without
  crossing a root boundary. It risks collision with a future GPO-defined `dod`
  token.
- `/us-dod/...` uses the documented sub-jurisdiction slot - "ISO 3166-1 country
  code and optionally followed by a dash and a lower level jurisdiction code" -
  and removes collision risk entirely. It costs the visual continuity with
  statute citations and misuses a slot meant for states and territories, not
  departments.

RULING: keep `/us/dod/...`. The authority chain is the product, and it runs
from a message to a statute in one unbroken path. Collision risk is real but
low, `dod` is not currently used by GPO, and this register is the precedence
record if it ever matters.

## 5. What our extension does NOT claim

- **It is not USLM conformance.** USLM's Objective annotation states the schema
  "is not intended to model executive branch or judicial branch documents." We
  are outside declared scope. That is not a violation - there is no conformance
  authority to violate - but it means GPO will not consider this use case when
  evolving the schema and will not fix breakage we hit.
- **Schema validity proves nothing here.** USLM types `@identifier` as a string
  of at most 1024 characters, with no pattern and no Schematron. Any string
  validates. Every rule in section 1 is enforced by our tooling or by nothing.
- **The XML export is a sibling vocabulary, not USLM.** It emits root
  `<issuance>` in `https://policy.usmc.mil/ns/uslm/1.0`. USLM 2.1 forbids
  foreign-namespace content except inside `<foreign>`, so a sibling namespace is
  the conformant path rather than a compromise.
- **Nothing resolves these identifiers.** USLM User Guide section 12.6:
  "A preferred resolver does not currently exist for USLM." Any resolution
  behavior is ours to build and operate.

## 6. Change procedure

1. A new token is allocated only by adding a row to section 2 with a dated note.
2. An allocated token is never reused for a different meaning. Retirement is
   recorded, not deleted, following the DON XML NDR continuity mechanism the
   contract already adopts for deleted rules.
3. A change to sections 1 or 3 is a breaking identity change requiring a schema
   major version and an owner ruling under `[ID2]`.
4. If GPO ever defines a conflicting token, this register is the precedence
   record and the migration is planned from it.
