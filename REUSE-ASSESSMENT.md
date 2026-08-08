# Reuse assessment

Date: 2026-08-08. Owner: Stephen. Scope: build-versus-reuse for the POC in
`POC-PLAN.md` and the layers after it.

---

## 1. The principle, and where I would sharpen it

The principle as stated - use or modify existing solutions rather than build
from scratch - is correct, and this repository has already been following it.
What it needs is a boundary, because applied without one it produces the
opposite of what it intends.

**Sharpened form, and I recommend adopting this wording:**

> Reuse **standards and vocabularies** aggressively. Reuse **designs** freely.
> Reuse **code** only when it clears a licence check, does not break the
> standalone-clone property, and would take longer to write than to integrate.

Three reasons the sharpening matters here specifically.

**You already reuse at the standards layer, and it is the reason the project is
defensible.** `conformance-matrix.md` is a reuse assessment under a different
name: USLM conventions adopted and extended, DCAT-US 3.0 emitted for OMB
M-25-05, JSON-LD for the authority graph, S1000D's fragment-addressing model
independently converged on, NIEM assessed and documented under DoDI 8320.07.
Fifteen sources evaluated, five adopted or adapted, and every rejection carries
its reason. Nothing about the current approach is build-everything.

**The standalone-clone property is load-bearing and a dependency spends it.**
`README.md`: "This is a standalone project. It carries its own corpus, its own
tooling, and its own build. Nothing else needs to be present." `CLAUDE.md`
section 11 restates it as a coding constraint. That property is why the
extraction from GunnyBot was worth doing. Every third-party runtime dependency
is a withdrawal from it, and the withdrawal has to buy something.

**There is no `LICENSE`.** Importing third-party code into a repository with no
stated terms is the worst ordering available. It converts an open housekeeping
item into a licence-compatibility problem with someone else's rights attached.
This is now the blocking item for any code reuse, and it is already recorded as
open in `resources/20-nist-code-portal.md`.

**Guard against retroactive application.** Read literally, the principle says
you should have used Akoma Ntoso instead of building a USLM sibling vocabulary.
That decision is made, documented in `conformance-matrix.md` section 1 with the
text it turns on, and reopening it is not a reuse decision but a rewrite. The
principle applies forward, to work not yet built.

---

## 2. What the EU catalogue actually yields

`resources/23-eu-oss-catalogue.md` carries the full review. The short version:
1,076 solutions, and **none targeting legislation markup, legal-rule encoding,
or decision automation**. The taxonomy runs to content management, workflow,
identity, and document management. Its useful contributions are a metadata
schema for a solutions register, a second federal-scale precedent for the
aggregate-do-not-host pattern, and a development-status field this project could
adopt for its own tools.

It is worth checking. For the core problem it is empty, and the candidates worth
assessing come from outside it.

---

## 3. Candidates, assessed against the POC

The POC in `POC-PLAN.md` is cross-tier rule reconciliation: read `rules.json`
files, group values by concept, normalize units, emit four verdicts with
citations. Roughly 200 to 300 lines of standard-library Python over files that
already exist.

| Candidate | What it is | Verdict | Reason |
|---|---|---|---|
| **OpenFisca** | Python rules-as-code framework. Country packages, variables, formulas, periods, entities, parameters. The exemplar named in `resources/17`. | **ADOPT THE DESIGN, REJECT THE RUNTIME** | Its parameter model - dated values with legislative references, separate from formula code - is the closest existing thing to `rules.json` and should be read before the concept register is finalized. Its runtime is a microsimulation engine sized for national tax-benefit systems, which is not the problem. Its licence is reported as AGPL-family and is **UNCONFIRMED**; if that is right it is decisive on its own for a federal public-domain target. Check before any import. |
| **Catala** | Inria research language for literate legal specification. Annotates each line of legal text with its meaning as code. Apache-2.0, OCaml. | **ADOPT THE IDEA, REJECT THE TOOL** | The idea - code bound to the specific passage it implements - is what `rules.json` citations already do, and Catala is independent confirmation the approach is sound. The tool is a research compiler its own repository describes as unstable and missing features, written in OCaml. An OCaml toolchain in the build path ends the standalone-clone property outright. |
| **DMN 1.3 plus FEEL** | OMG standard for decision tables and a decision expression language. Mature, multi-vendor, tool-supported. | **DEFER, then adopt as notation** | This is the strongest genuine reuse in the whole list, and it is not for this POC. If the P2 question - does policy logic become data - is ever answered yes, DMN is the answer, and inventing a private rule syntax instead would be the mistake the principle exists to prevent. Reconciliation compares values and needs no decision logic, so pulling DMN in now buys nothing. Revisit trigger: the first requirement for a conditional rule that cannot be expressed as a value. |
| **Akoma Ntoso / OASIS LegalDocML** | The international standard sibling of USLM. | **ALREADY DECIDED** | Assessed in substance by `conformance-matrix.md` section 1. Relevant again only if non-US interoperability becomes a requirement. Not a POC input. Worth its own matrix row for completeness. |
| **Drools, Camunda, and JVM rule engines** | Production rule engines with DMN support. | **REJECT** | A JVM in the build path for a static-site project of 56 documents. Wrong scale by two orders of magnitude. |
| **JSONLogic, CEL** | Small portable predicate expression formats. | **CANDIDATE, P2** | Genuinely light. Becomes relevant at the same trigger as DMN and is the cheaper of the two if the predicates stay simple. Not needed to compare two numbers. |
| **pySHACL / SHACL** | W3C shape validation for RDF graphs. | **CANDIDATE, P2** | You publish JSON-LD authority graphs and carry `schema/authority-ontology.ttl`. SHACL could replace hand-written graph checks with declared constraints. `verify_authority` already reports PASS, so this buys rigour rather than capability. Revisit if graph invariants multiply. |
| **EU OSS Catalogue** | The catalogue itself. | **SOURCE, NOT DEPENDENCY** | See `resources/23`. |

---

## 4. Recommendation for the POC

**Recommendation.** Build `tools/reconcile.py` from the standard library. Reuse
**designs** from OpenFisca's parameter model and Catala's text-binding
discipline. Import **no third-party code**.

**Why.** The POC is a grouping, a unit conversion, and a comparison over files
you already own. Every framework listed above is larger than the problem. The
integration cost of any of them - dependency, licence clearance, build change,
a second way to express a rule - exceeds writing 250 lines. Reuse is supposed to
save effort, and here it would spend it.

**Risks of this recommendation.** The honest one: writing it yourself risks
inventing a private rule vocabulary that later has to be migrated to DMN. The
mitigation is cheap and I recommend taking it now - keep the concept register to
**values with units and citations only**, with no conditions, no operators, and
no expressions. A value register migrates into DMN cleanly. A half-invented
expression syntax does not.

**Alternative if you disagree.** Build the POC directly as a DMN decision table
with an off-the-shelf evaluator. You would get a standard notation from day one
and pay for it with a runtime dependency, a licence clearance, and a
representation mismatch, since reconciliation compares stated values across
documents rather than deciding an outcome from inputs. I would not take that
trade for a POC, and I would take it seriously the moment logic enters.

**Next step.** Unchanged from `POC-PLAN.md`: answer B1, B2, B3, then M0
transcription. Add one item to M1 - read OpenFisca's parameters documentation
before finalizing `config/rule_concepts.json`, so the register borrows a proven
shape rather than a new one.

---

## 5. Where reuse genuinely should win

Building this yourself would be wrong in four places, and none is the POC.

1. **The expression language, if logic ever becomes data.** DMN plus FEEL.
   Inventing a rule syntax is the classic failure and the principle is right.
2. **Graph validation, if invariants multiply.** SHACL over hand-written checks.
3. **A solutions register, if GOATS builds one.** Match the EU catalogue's
   metadata schema and the NIST portal's aggregate-do-not-host pattern rather
   than designing a third.
4. **OCR and document acquisition.** Already ruled NOT APPLICABLE here because
   it belongs to GunnyBot (`resources/19`), and when GunnyBot needs it the answer
   is Tesseract 5 or a current document-understanding model, never a bespoke
   pipeline.

## 6. Standing gate

Adopt this as the test for any future proposal to add a dependency. All five
must pass.

1. **Licence.** Compatible with this repository's stated terms. **Blocked until
   a `LICENSE` exists.**
2. **Standalone.** `./build.sh` still succeeds on a fresh clone with a normal
   Python install.
3. **Scale.** The dependency is not larger than the problem it solves.
4. **Substitution.** It replaces code, rather than sitting beside code that
   still has to be written.
5. **Exit.** There is a stated way out if the project is abandoned. Catala's own
   repository calling its compiler unstable is the shape of the risk.

A candidate failing any one is recorded with its reason, in
`conformance-matrix.md` or `resources/`, so it is not re-proposed.

## 7. Confidence

0.85 on the assessment. Catala's licence, language, maturity statement, and
text-binding design were read from its repository. The EU catalogue counts and
taxonomy were retrieved. DMN's standing as an OMG standard is a matter of
record.

0.6 on OpenFisca specifically, because its licence and the exact granularity of
its variable `reference` attribute were not confirmed from primary documentation
in this pass. Both are UNCONFIRMED and both are material, since the licence
alone could be decisive. Confirm before M1.
