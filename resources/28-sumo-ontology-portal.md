# 28. SUMO and the Ontology Portal - EVALUATE, do not adopt yet

Sources: <https://ontologyportal.org/>, <https://github.com/ontologyportal/sumo>,
<https://github.com/ontologyportal/sumo/blob/master/Law.kif>. Retrieved
2026-08-20. Maintainer: the Ontology Portal project, led by Adam Pease.

## What it is, confirmed

| | |
|---|---|
| Artifact | Suggested Upper Merged Ontology, stated by its publisher as the largest formal public ontology in existence |
| Size | ~25,000 terms and ~80,000 axioms with all domain ontologies combined |
| Language | SUO-KIF, first-order logic with some higher-order extension |
| Lexical mapping | mapped to the whole of WordNet, a property no other formal ontology claims |
| Exports | TPTP for theorem provers, OWL, Neo4j graph dumps |
| Repository | 3,850 commits, 264 stars, 84 forks, 1 tagged release |
| Domain coverage | includes Government, Law, Military, Communications, Finance, Geography, Transportation, Medicine |

## The licensing contradiction, unresolved

Two statements about the same artifact, from the two authoritative surfaces.

- ontologyportal.org: "SUMO is free and owned by the IEEE. The ontologies that extend SUMO are available under GNU General Public License."
- github.com/ontologyportal/sumo, repository header: **GNU Public License**, applied to a repository holding both the core and the extensions.

Ownership by a standards body and GPL over the same files answer different
questions and one of them is wrong at the boundary. **Resolve this in writing
before any adoption.** GPL over a knowledge base merged into a government
corpus is a distribution question with a real answer, not a formality, and the
answer has to come from the licensor, not from a reading of the README.

No IEEE standard number for SUMO was confirmed this pass. The claim traces to
the former IEEE Standard Upper Ontology working group. Recorded as
**UNCONFIRMED**, not as fact.

## Law.kif, measured

507 lines, 425 lines of code, 17.3 KB. It defines `permits`, `prohibits`,
`confersRight`, `confersObligation`, `confersNorm`, `deprivesNorm`,
`holdsRight`, `holdsObligation`, plus legal roles and evidence relations. It
does **not** define statute, regulation, or jurisdiction as primary concepts.

Read that number honestly. 507 lines is a sketch of deontic vocabulary, not a
legal drafting formalism, and the gap between it and what MCO issuance
structure needs is the whole distance this project has already walked.

## The argument for

`conformance-matrix.md` section 13 names LegalRuleML as the closest fit in the
register, and it is. LegalRuleML gives deontic operators, defeasibility,
temporal validity, and isomorphism back to source text, and gives no model of
the world the rules are about. SUMO is the opposite shape. A leave rule that
turns on whether a Marine is a reservist performing inactive duty training
needs a world model to say what those things are.

SUMO also brings a theorem prover behind it, which no other register entry
does. Consistency checking across orders is a real future need for
`data/*.rules.json`.

## The argument against

Three points, and they carry more weight today.

1. The corpus's live problem is provenance, not inference. 85 drift findings and 220 references naming documents the store never held are a collection problem. A first-order reasoner over 56 documents answers a question nobody is asking yet.
2. Section 12 already ruled this exact question for OWL and Protégé. Correct tool, not yet needed, do not adopt early. Nothing in SUMO changes that reasoning, and reversing it for a heavier formalism than OWL requires more evidence, not less.
3. SUO-KIF sits outside every interchange path the consumers use. NIEM, USLM, DCAT, and OWL or RDF are what a downstream government consumer reads. SUMO's OWL export is the only branch of it a consumer would touch, and that export is lossy against the axioms, which are the point.

## The decision this turns on

**Does `data/*.rules.json` need cross-document consistency checking, and does
that check require a model of the entities the rules quantify over.**

Trigger: when `rules.json` generalizes past parental leave to two or more
orders whose provisions interact. At that point, evaluate SUMO plus Sigma
against LegalRuleML plus SHACL as a pair, on one worked example, and decide
once. Not before, and not on the strength of the ontology's size.

## Independence gap

Every source in this pass traces to one author. This register now holds no
third-party assessment of SUMO. **Before any adoption decision, one independent
evaluation is required**, and the leading candidates are the FOIS and Applied
Ontology literature and any comparison against BFO, which is the upper ontology
already carrying a US federal footprint through ISO/IEC 21838-2.

## Verdict

**EVALUATE.** A live candidate whose adoption turns on a decision not yet made,
same state as row 24. This extends EVALUATE past the single row the 2026-08-08
pass restricted it to, which is a deliberate change, recorded here and in
`resources/README.md`.

Confidence 0.8. Sizes, license strings, repository counts, and the Law.kif
measurement were read directly. The IEEE ownership claim was not resolved and is
carried as unconfirmed.
