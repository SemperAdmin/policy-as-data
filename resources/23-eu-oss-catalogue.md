# 23. EU Open Source Solutions Catalogue - ADAPTED as a source, REJECTED as a dependency

Source: <https://interoperable-europe.ec.europa.eu/eu-oss-catalogue/solutions>
Retrieved 2026-08-08. Publisher: European Commission, DG DIGIT.

## What it is

A searchable catalogue of "Solutions created by and for European Public
Services," aggregated from national platforms rather than hosted centrally.

| Measure | Value at retrieval |
|---|---|
| Solutions indexed | 1,076 across 54 pages |
| Largest contributors | Developers Italia 531, Open Code (Germany) 396 |
| Development status | Stable 782, Development 122, Beta 106, Concept 23, Obsolete 10 |
| Category tags | 200+, including compliance-management (30) and workflow-management (76) |
| Audience tags | 40+ |
| Software types | 19 |
| Per-entry metadata | version, description, categories, licence, follower and rating counts |

Legal basis is the Interoperable Europe Act, the same instrument behind
`resources/18`.

## The finding that governs

**Nothing in the catalogue targets legislation markup, legal-rule encoding, or
decision automation.** The category taxonomy runs to content management,
collaboration, document management, identity management, data analytics, and
workflow. The two closest tags, compliance-management and workflow-management,
hold process tooling rather than anything that encodes a legal provision.

That is a real result, not a search failure. It means the catalogue's yield for
this project's **core problem** is close to zero, and its yield for the
**programme's portal ambitions** in `CHARTER.md` is meaningful. Do not conflate
the two when citing it.

## Where it is useful

1. **The aggregate-do-not-host pattern.** The catalogue indexes solutions living
   on twelve-plus national platforms and refreshes from them. That is the same
   pattern `resources/20` recorded from the NIST portal, now with a second
   independent instance. Two federal-scale precedents for the same architecture
   is enough to cite it as established practice rather than as a choice.
2. **The metadata set.** Version, description, categories, audience, software
   type, development status, licence. That is a serviceable minimum schema for
   any GOATS-side solutions register, and it costs nothing to match it.
3. **Development status as a first-class field.** Stable, Development, Beta,
   Concept, Obsolete, published per entry. This project already distinguishes
   VERIFIED from UNVERIFIED for records. It publishes nothing equivalent for its
   own tools, and `prototypes/editor.html` is retired while `tools/evaluate.py`
   is a working single-domain engine, with nothing on either saying so.

## Where it is not useful

**As a dependency source for the encoding or the rules layer.** No candidate
exists in it for either. Anything reusable in this space comes from outside the
catalogue: OpenFisca, Catala, DMN, Akoma Ntoso, SHACL. Those are assessed in
`REUSE-ASSESSMENT.md`, not here.

## The licence trap, and it is the sharpest item on this page

European public-sector open source is dominated by the **European Union Public
Licence**. EUPL is a **copyleft** licence with reciprocity obligations and a
defined compatibility list.

This repository is a candidate US Government work whose intended terms are the
17 U.S.C. 105 public-domain position recorded in `resources/20`. Those two are
not compatible in the direction that matters:

- You **cannot** place a derivative of EUPL-covered code into the public domain.
  Importing EUPL source into this tree would subject the combined work to EUPL
  reciprocity and would defeat the licensing model you have not yet adopted.
- The repository currently ships **no `LICENSE` at all**, so there is no stated
  position for a compatibility analysis to run against. Importing any
  third-party code before that gap is closed makes the licence question harder,
  not easier.

**Ruling: no code from this catalogue enters this repository until a `LICENSE`
exists and the specific candidate's terms have been cleared against it.**
Reading a catalogue entry for design ideas carries no such constraint and is
encouraged.

Whether a given entry is EUPL is per-entry and **UNCONFIRMED** at the catalogue
level. Check the entry, not the platform.

## Verdict

**ADAPTED as a source, REJECTED as a dependency.** The catalogue is a good place
to look and, for this project's core problem, an empty one. Its metadata schema
and its aggregate-do-not-host pattern transfer. Its code does not, until the
licensing gap in `resources/20` is closed.

## Confidence

0.75. The catalogue landing view was retrieved and its counts, taxonomy, and
per-entry metadata quoted. The absence of legal-rule solutions is drawn from the
category taxonomy and the visible result set, not from an exhaustive walk of all
54 pages, and is marked accordingly. The EUPL dominance claim is a
characterisation of European public-sector practice rather than a count taken
from this catalogue; the incompatibility reasoning holds regardless, because it
turns on copyleft in general and not on EUPL specifically.
