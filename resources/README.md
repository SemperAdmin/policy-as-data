# Resource reviews

Dates: 2026-08-08, rows 17 to 24. 2026-08-20, rows 25 to 30. 2026-09-11, row 31. Owner: Stephen.
Status: draft, pending merge into `conformance-matrix.md`.

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

Rows for these sources are appended to `Web_resources.csv` in the same commit.
When these reviews are merged into `conformance-matrix.md` they become sections
17 through 30. Section 16 in that file is the exporter rebuild, not a
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
- **EVALUATE** - a live candidate whose adoption turns on a decision not yet made. Rows 24, 28, and 29. The decision and its trigger are named in the review. **Changed 2026-08-20.** The 2026-08-08 pass restricted this state to row 24. Rows 28 and 29 meet the same test, a real candidate held on a decision that is named and not yet taken, so the restriction is lifted rather than worked around.

A sixth state applies to two rows in this pass and is not a verdict:

- **UNCONFIRMED** - the source could not be reached from this environment, so
  no verdict is recorded. The row states what blocked it and what would
  discharge it. Nothing is inferred from the URL.

## Summary

### 2026-08-08

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

### 2026-08-20, the ontology pass

| # | Resource | Verdict | One line |
|---|---|---|---|
| 25 | SEP, Ontology and Information Systems | NOT APPLICABLE | The definitional citation for this project's use of the word ontology. |
| 26 | Ontology Talk, Taming Digital Volatility | NOT APPLICABLE | Orientation media. Title confirmed, content unverified after HTTP 429. |
| 27 | Adam Pease, papers and site | NOT APPLICABLE | Bibliography index. Supplied as .org, resolves to .com. Third NPS entry point in the register. |
| 28 | SUMO and the Ontology Portal | EVALUATE | A world model with a prover behind it, complementing LegalRuleML. Licensing unresolved. |
| 29 | SigmaKEE | EVALUATE, blocked by 28 | Read Law.kif in the hosted browser first. Never a dev build in a pipeline. |
| 30 | Ontology Talk channel | NOT APPLICABLE | Media index. |

### 2026-09-11

| # | Resource | Verdict | One line |
|---|---|---|---|
| 31 | Genişel and Pease, SUMO for COLREGs and ROE | ADAPTED | Four mechanisms adopted without the formalism: attested absence, binding kind, a claims table with negatives, derivation steps. Row 28 EVALUATE unchanged, trigger sharpened. |

Three findings from this pass sit above the individual rows.

1. **The set is not independent.** All six sources trace to one author. Four are his own properties and two are projects he leads. Nothing here is disqualifying, and SEP entries are refereed, but the register now holds **no third-party assessment of SUMO**. One independent evaluation is required before any adoption decision, with BFO under ISO/IEC 21838-2 as the comparison baseline.
2. **SUMO's licensing is contradictory at the source.** The portal states IEEE ownership with GPL extensions. The repository header states GNU Public License over a repository holding both. Resolve in writing with the licensor before adoption.
3. **This pass does not displace the standing recommendation.** `conformance-matrix.md` section 13 names LegalRuleML as the closest fit in the register. SUMO is a complement to it, not a replacement, and section 12's ruling stands unchanged. Correct tool, not yet needed, do not adopt early.

One GAP surfaced in the 2026-08-08 pass, at row 20, and it is open. Two rows carry no
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
- `25-sep-ontology-and-information-systems.md`
- `26-ontology-talk-intro-video.md`
- `27-adam-pease-papers.md`
- `28-sumo-ontology-portal.md`
- `29-sigmakee-dev.md`
- `30-ontology-talk-channel.md`
- `31-oceans-sumo-roe-paper.md`
- `index.json`

## Research method

Primary sources only, matching the standing rule. Specification and portal text
is quoted verbatim where a verdict turns on it. Every retrieval carries an
access date in `index.json`. Where a source refused retrieval, the row says so
rather than reporting a summary obtained some other way.
