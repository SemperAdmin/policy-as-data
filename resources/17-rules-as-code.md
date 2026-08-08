# 17. Rules as Code - ADAPTED

Source: Interoperable Europe Portal, EUGovTech collection, "Rules as Code (RaC)".
<https://interoperable-europe.ec.europa.eu/collection/eugovtech/news/rules-code-rac>
Retrieved 2026-08-08. Publisher: European Commission, DG DIGIT.

## The definition that governs

> "Rules as Code (RaC) is a trend in which official law and regulations are
> interpreted or defined and published in a machine-consumable form."

That is the whole of this project's thesis, arrived at from the European side.
The convergence is the finding, the same way S1000D was in section 9.

## Where this project already sits inside the RaC model

The source sets out a three-step pathway. Measure the repository against it
rather than against the aspiration.

| RaC step | This project | State |
|---|---|---|
| 1. Identify and publish all public knowledge agreements | `canonical/`, 56 documents, rendered to `docs/` | done for the demonstration corpus, not the 17,500-document universe |
| 2. Analyse and integrate through cross-referencing and standardisation | 362 cited edges, `cited` versus `inferred` recorded on every one | done, and stricter than the source asks for |
| 3. Formalise and codify for operationalisable implementation | `data/dodi-1327.06.rules.json`, `data/maradmin-051-23.rules.json`, `tools/evaluate.py` | two documents only. This is where the project is thin. |

Step 2 is the strongest column. The source treats cross-referencing as an
integration activity. This repository treats it as an evidentiary one: no edge
is written without naming the paragraph it was read from, and a cited edition is
never silently upgraded. RaC literature does not require that. It should.

## The finding that transfers directly

The source names the failure mode this project's drift reporting was built to
catch:

> Multiple implementations of identical regulations create compliance risks.
> The Dutch pension age rule is referenced 100+ times across legislation but
> likely reimplemented differently in numerous systems.

That is the same defect as an edge pointing at a superseded edition, one layer
up. This repository reports 85 drift findings out of 362 edges, produced by
extraction rather than compiled by hand. The Dutch case is the argument for why
that number matters: the count of reimplementations is the compliance exposure.

**Use it.** The drift report currently reads as a housekeeping artifact. Framed
as RaC frames it, it is a risk register. That is a documentation change, not a
code change.

## Two ideas worth adopting

1. **The five service processes.** The source names service definition,
   operational decisions, incident management, change management, and risk
   management as processes that "require ongoing interaction with affected
   stakeholders and cannot be fully automated." This repository has change
   management (the two-tier promotion) and nothing else. Verification is
   currently a data state. It is really an incident-and-change process, and
   naming it that way would give `VERIFICATION.md` a spine it lacks.

2. **The single knowledge source rule.** The source insists on "real-time data
   sources connected to single knowledge sources (not static datasets)."
   `config/revision_index.json` is a static snapshot of the GunnyBot corpus used
   to decide supersession. That is a stated dependency in `README.md`, and by
   this source's standard it is the one place the architecture is weakest.
   Nothing to fix today. Worth naming as a known limit.

## What is deliberately not adopted

**The semantic web stack.** The source assumes RDF, Turtle, SHACL, OWL, and
RIF, and proposes Answer Set Programming over RIF-CASPD for rule interchange.
This repository publishes JSON-LD authority graphs and carries one Turtle
ontology at `schema/authority-ontology.ttl`. Section 12 of the conformance
matrix already recorded the ruling: the graph is JSON-LD, not OWL. Nothing here
reopens it. RIF is a W3C Recommendation from 2013 with no live tooling
ecosystem worth the migration.

**The EU vocabularies.** CPSV-AP, CCCEV, and ELI are EU public-service and
legislation vocabularies. ELI is the closest analogue to the identifier scheme
in `NAMESPACES.md`, and it is a genuinely better-governed one, because ELI has a
registry and GPO does not. It is still the wrong register: ELI identifies
European legislation, and nothing in it addresses a MARADMIN. The register
stands.

**Symbolic over statistical.** The source argues RaC "combines symbolic AI
(knowledge-driven) with human decision-making processes rather than relying
solely on data-driven approaches like Large Language Models." That is already
this project's position, expressed as UNVERIFIED-until-a-human-says-otherwise.
No change.

## Verdict

**ADAPTED.** Same intent, reached independently from the US legislative-markup
side rather than the EU public-service side. The repository already satisfies
RaC steps 1 and 2 for its corpus and is thin at step 3. Two ideas are worth
adopting and are named above. Nothing in this source creates an obligation,
because nothing in it binds a US Department of Defense component.

## Confidence

0.85. The source is a signed opinion piece on an official Commission portal,
not a specification. Its own status is advocacy, and the author's promised
CPSV-AP/RIF-CASPD publication (stated as end-2024, via GitLab) is UNCONFIRMED -
no artifact was located. Treat the definition as quotable and the
implementation pathway as one author's proposal, not as Commission guidance.
