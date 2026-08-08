# Resource reviews

Date: 2026-08-08. Owner: Stephen. Status: draft, pending merge into
`conformance-matrix.md`.

This directory holds the per-source review for external resources added after
the 2026-08-03 conformance pass. One file per source, plus `index.json` as the
machine-readable register.

**This is not `REFERENCES.md`.** That file is the backlog of *issuances the
corpus cites* and their encoding state. This directory covers *external
standards, tools, and literature the project is measured against*. The two
never overlap: nothing here is ever encoded into `canonical/`.

## Relationship to the existing artifacts

| Artifact | Holds |
|---|---|
| `Web_resources.csv` | the flat register of external resources, title, description, link |
| `conformance-matrix.md` | the verdict for each register row, with the text the verdict turns on |
| `resources/*.md` | this pass, one file per source, same verdict scale |
| `resources/index.json` | the machine-readable register, consumable by tooling |

Rows for these six sources are appended to `Web_resources.csv` in the same
commit. When these reviews are merged into `conformance-matrix.md` they become
sections 17 through 24. Section 16 in that file is the exporter rebuild, not a
reference, so the reference numbering there stops at 15 and resumes at 17.

## Verdict scale

Unchanged from `conformance-matrix.md`.

**Provenance note, 2026-08-08.** `conformance-matrix.md` sources this scale from
`hhq-alignment-plan.md` N0.2, and that document is **not in this repository**. The
scale as stated below is quoted from `conformance-matrix.md` itself, which is
here and is sufficient. Resolve the dangling citation per `ACTION-REGISTER.md`
item 0.7.

- **CONFORMANT** - the stack meets the requirement as written.
- **ADAPTED** - same intent, modern or different form, rationale stated.
- **NOT APPLICABLE** - out of scope, rationale stated.
- **GAP** - a real shortfall. Every GAP names its fix and its state.
- **EVALUATE** - a live candidate whose adoption turns on a decision not yet made. Row 24 only. The decision and its trigger are named in the review.

A sixth state applies to two rows in this pass and is not a verdict:

- **UNCONFIRMED** - the source could not be reached from this environment, so
  no verdict is recorded. The row states what blocked it and what would
  discharge it. Nothing is inferred from the URL.

## Summary

| # | Resource | Verdict | One line |
|---|---|---|---|
| 17 | Rules as Code, Interoperable Europe | ADAPTED | Same socio-technical model, reached from the legislative side. Two ideas worth adopting. |
| 18 | Digital-Ready Policymaking, Interoperable Europe | ADAPTED, no obligation attaches | EU public-sector instrument. The method transfers, the law does not. |
| 19 | NIST `usnistgov/ocr-pipeline` | NOT APPLICABLE to this repository | Acquisition and extraction belong to GunnyBot. Stack is also dead: Python 2.7, Ocropy. |
| 20 | NIST Software Portal, code.nist.gov | ADAPTED, and it surfaces a GAP | The federal release pattern is directly copyable. This repository ships no LICENSE. |
| 21 | NPS FAST, fast.mfr.nps.edu | UNCONFIRMED | Host refuses automated retrieval. No public documentation names the tool. |
| 22 | Books24x7 title via UMGC EZproxy | UNCONFIRMED | Authenticated proxy link. Title and author not recoverable from the URL. |
| 23 | EU Open Source Solutions Catalogue | ADAPTED as a source, REJECTED as a dependency | 1,076 solutions and none for legal-rule encoding. Surfaces a copyleft-versus-public-domain trap. |
| 24 | LEOS, Legislation Editing Open Software | EVALUATE | Stable EU drafting platform emitting Akoma Ntoso. Models EU legal acts, not naval correspondence. |

One GAP surfaced this pass, at row 20, and it is open. Two rows carry no
verdict because their sources could not be confirmed. Row 23 was added the same
day and its build-versus-reuse consequences are worked out in
`REUSE-ASSESSMENT.md`.

## Files

- `17-rules-as-code.md`
- `18-digital-ready-policymaking.md`
- `19-nist-ocr-pipeline.md`
- `20-nist-code-portal.md`
- `21-nps-fast.md`
- `22-books24x7-umgc.md`
- `23-eu-oss-catalogue.md`
- `24-leos.md`
- `index.json`

## Research method

Primary sources only, matching the standing rule. Specification and portal text
is quoted verbatim where a verdict turns on it. Every retrieval carries an
access date in `index.json`. Where a source refused retrieval, the row says so
rather than reporting a summary obtained some other way.
