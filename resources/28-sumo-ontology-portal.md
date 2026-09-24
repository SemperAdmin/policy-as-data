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

## Addendum 2026-09-24: the method, read from the primary literature

Rows 27 to 31 were written without the papers. On 2026-09-24 every paper file
linked from the author's site was retrieved (78 files, row 27) and the method
was read from the papers themselves. The files are held in a local reference
library outside this repository because they are third-party copyright; the
filenames below are the author's own and resolve at <https://www.adampease.com/>.

**Independence is unchanged.** All of this is one research group. The
independent evaluation required above is still owed.

### What the papers confirm

| Claim | Stated in |
|---|---|
| Size: 106,633 axioms and 16,541 symbols with every domain file loaded; `Merge.kif` alone is 5,477 axioms. Earlier papers give 20,000 terms and 70,000 to 80,000 axioms. | `Sigma-rs.pdf`, `IKBETSigma-journal.pdf`, `PeaseFLAIRS2022.pdf` |
| Reasoning runs only after translation to first-order TPTP (FOF or TFF). "All the strictly higher-order content in SUMO is lost in translation to first-order." Predicate variables range only over predicates in the knowledge base; row variables are macro-expanded to arity 7. | arXiv 2303.04148, `pe_sch_sigma.pdf` |
| At full size the prover needs relevance filtering. Handing Vampire the whole knowledge base solved 18 of 39 test problems at 60 s; the Rust build with SInE pre-selection solved 39 of 39 at about 2 s each. | `Sigma-rs.pdf` |
| Consistency cannot be certified. One check produced a contradiction with a 120-step proof; the authors report "a few each year" and a regression suite of about 50 tests. | `ontocheck.pdf`, `PeaseFLAIRS2022.pdf` |
| The deontic operators (`modalAttribute` with Obligation, Permission, Prohibition; `confersNorm`, `holdsObligation`) are exercised only in hand-written THF test problems. The automated SUO-KIF to THF translator is unfinished. Universal conjectures fail under system D; a contrary-to-duty case yields a wrong refutation the authors are still investigating. THF carries no arithmetic. | `FEENER-ARQNL.pdf`, `PeaseCrouchFest.pdf` |
| The working rule system, COLREG, uses plain first-order predicates (`giveWayVessel`, `standOnVessel`), not the deontic operators. Rules were hand-encoded. Exceptions are hand-written guards on each rule. 171 of 172 refutations correct over 288 scenarios, 0.531 s mean. | `TimberPeaseCOLREG-CSCI2025.pdf` |
| Calendar arithmetic is axiomatized in typed first-order logic with integers. Vampire proved all 200 benchmark conjectures and Z3 validated them. It needs 47 hand-proved anchor facts tailored to the benchmark, and it is not yet integrated with SUMO. | `CalendarLogic.pdf` |
| The English-to-logic pipeline was tested on 100 sentences from an unnamed policy corpus: 59 to 62 percent of outputs were both syntactically valid and used only SUMO terms. **Whether the meaning is correct was not measured.** The prover checks consistency, not faithfulness. | `NESY_Conference_Paper.pdf`, `Edinburgh25.pdf` |
| No paper names a license. They say "open source" and "free". The contradiction recorded above is not resolved by the literature. | all |

### What changes in this row

Nothing in the verdict. **EVALUATE** stands, and the reading strengthens the
argument against early adoption on three new grounds.

1. **The part a policy domain needs most is the least mature part.** Deontic
   operators, embedded formulas, and temporal validity are exactly the content
   the first-order translation drops or the THF route handles experimentally.
   Defeasibility, norm conflict, precedence, and the in-force interval of a
   norm (effective date, cancellation, supersession) are not addressed in any
   paper. LegalRuleML addresses all four.
2. **No paper computes an entitlement quantity.** A prover answers proof or
   timeout. `evaluate.py` answers "84 days, cited" or refuses by name. A timeout
   is not a verdict this project can publish.
3. **Automated translation does not reduce the verification burden.** At the
   authors' own best, four in ten outputs fail a well-formedness check and the
   six that pass are unchecked for meaning. Every rule would still need a
   person to read the paragraph, which is the step `UNVERIFIED` already forces.

And one ground **for**, stated plainly: SUMO is the only candidate in the
register with a world model the rules could quantify over, and the proof
object is a derivation from facts to conclusion, which is the "show its work"
half of `CONCEPT.md` section 1 done at depth.

### Trigger, restated

Unchanged from row 31: the trigger fires when a rule's value is a **class**
rather than a number, or when two or more encoded orders interact. M5
promotion eligibility is the first candidate. Then run SUMO plus Sigma and
LegalRuleML plus SHACL on that one worked example and decide once.

### Actions from this pass

| # | Action | Priority | State |
|---|---|---|---|
| 28.1 | Port the CalendarLogic benchmark shape (leap years, month ends, Nth weekday, offsets across year boundaries) into positive and negative claims for the date arithmetic in `evaluate.py`. Stdlib only. Targets the forfeiture-window defect class. | P1 | OPEN |
| 28.2 | Optional `sumo_term` cross-reference on `config/rule_concepts.json`, assigned by a person, never used to derive anything. Held until the license contradiction is resolved in writing. | P2 | HELD |
| 28.3 | Independent evaluation: one third-party source on SUMO, with BFO under ISO/IEC 21838-2 as the baseline. | before adoption | OPEN |
| 28.4 | Rejected for now: a prover in the build path, SUMO deontic operators as the rule format, automated English-to-logic translation. | - | REJECTED |
