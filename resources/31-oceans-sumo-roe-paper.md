# 31. Genişel and Pease, Formal Ontology for Maritime Operations in SUMO - ADAPTED

Source: O. O. Genişel and A. Pease, "Formal Ontology for Maritime Operations in
SUMO: From Collision Avoidance to Rules of Engagement," Naval Postgraduate
School, Monterey. Supplied by the owner as a PDF on 2026-09-11. 7 pages,
113,474 bytes, SHA-256 `51fcaa983d5811679223d55ca3220e0a32584d00513cd2f97718605d223b999e`.
Venue and publication state **UNCONFIRMED**: the filename says OCEANS, the
paper itself names no venue, and no URL was supplied. Companion code is stated
at `github.com/ontologyportal/sumo/tree/master/tests/ROE`, not retrieved.

**Independence.** Same author as rows 27 to 30. The register still holds no
third-party assessment of SUMO, and this row does not change that.

## What the paper does, confirmed

Two formalizations in SUO-KIF over SUMO, run through the Vampire prover via
SigmaKEE. COLREGs (prior work, 288 scenarios, 99.4% on classification) and
Rules of Engagement (this paper, 24 measures across five series of the Newport
ROE Handbook). Eleven validation queries, seven expecting a proof and four
expecting none. Nine returned as expected; two negatives ran to the resource
bound without a proof or a completed saturation, and the paper reports them as
open rather than as passes.

Five design moves carry the paper. Each is measured against this repository
below.

| Paper | Mechanism | This repository today |
|---|---|---|
| Measures point at defined action classes; coverage is **derived** by subsumption, not stipulated by tokens | `measureAuthorizes`, `subclass`, `measureSubsumes` | `config/rule_concepts.json`: concept identity is a recorded human judgement with a prose definition. Nothing derives from it. Deliberate: `CLAUDE.md` section 2.5. |
| A catalog measure is not binding. An **activation** by competent authority puts it in force for an operation and supplies the value the clause leaves open | `ROEActivation`, `activationParameter`, template versus complete measures | Not modelled. `reconcile.py` treats every tier's value as a fixed statement. A DoDI that delegates a value to the Military Departments and a DoDI that fixes it read the same. |
| Three outcomes derived independently: authorized, prohibited, permissible. The **restrictive default is derived explicitly**, never from a failed proof | `actionUnauthorized` as a positive derivation | `evaluate.py` refuses by name and `reconcile.py` emits `NOT_HELD` as a verdict. Aligned in spirit. But `NOT_HELD` conflates "the authority states no value" with "nobody has transcribed the authority yet". |
| Negative facts are **asserted, not inferred**. Closure is over the authoritative message, which is complete by construction, and never over the state of the world | `closureConflict` as a derived predicate rather than an inconsistency | Practised, not stated. Cited edges come only from `Ref:` lists, which are complete. `config/revision_index.json` is the open world. `verify_status.py` reports `INVALIDATED` as a finding rather than failing. |
| Every determination carries a **derivation** from facts through rules to conclusion | the prover's proof object | Every output line carries one citation. Depth one. The arithmetic between a cited value and a computed answer is in Python and is not printed, which is exactly where `verification/findings-forfeiture-window.md` found a defect. |

## What transfers

Four things, none of which needs SUMO, a prover, or a new dependency.

**1. Attested absence.** The paper's sharpest point is that failure to derive
authorization does not prove an action is unauthorized. `reconcile.py` makes
that mistake by vocabulary: `NOT_HELD` is emitted both when a tier was read and
states nothing and when a tier was never read. Split it. `NOT_ENCODED` when no
rule file carries the concept at that tier. `SILENT` only when the ledger holds
an attestation of kind `absence`, meaning a named verifier read the tier and
recorded that it states no value for the concept. The MOS spine "names no DoD
authority" is the same ambiguity one layer up. Code change is small; the
attestation kind is new and goes through `verification/README.md`.

**2. Binding kind at the authority tier.** The template-versus-complete
distinction is the reconciliation question restated. A concept at the DoD tier
is one of `fixed`, `floor`, `ceiling`, or `delegated`. Then `DIVERGE` has
direction and consequence: a service value below a floor is a finding, a
service value differing from a delegated value is conforming variation and
must not read as a finding. Today the tool cannot tell them apart, and
`POC-PLAN.md` section 7 already names a bare verdict as the most damaging
thing this project could ship. Data field on `config/rule_concepts.json`, a
few lines in `reconcile.py`.

**3. A claims table, with negatives.** The paper's Table I lists the claim,
the query, the expected result, and the actual result, with a dash where the
answer is open. `ACTION-REGISTER.md` item 1.3 records that all four `reconcile`
paths were tested and nothing in the tree carries that test. CI runs
`validate.py` only. Adopt the table as data: one row per claim, positive and
negative, run by a stdlib script in `validate.yml`. Negative rows are the ones
that matter here: `reconcile` never emits `AGREE` from an unverified input,
`units.json` never converts years, `evaluate.py` never answers past the encoded
rules. The project's own rule is that counts are not evidence. A claims table
is.

**4. Derivation steps in the evaluator.** `evaluate.py` cites the rule and
hides the arithmetic. Print the steps: inputs, operation, basis. A unit
conversion cites its `units.json` entry. A date shift names whether it is a
day count or a calendar year. The forfeiture-window finding was a hidden
derivation step, `1 year` to `365 days`, presented as a citation. Inspectable
steps make that class of defect visible on the page instead of in a
post-mortem.

Two documentation items. State the closed-world ruling in `README.md`: a
reference list is closed, the world is open. And record in `CHARTER.md` that
the attestation ledger is the answer to the paper's own open problem, that a
language-model translation of text into rules "would produce a well-founded
proof of the wrong thing": here, machine-read values are `UNVERIFIED` by
construction and a named person promotes them.

## What does not transfer

**The formalism.** Row 28's ruling stands and this paper does not move it. The
trigger was "when `rules.json` generalizes past parental leave to two or more
interacting orders." Sharpen it: the trigger fires when a rule's value is a
**class** rather than a number. Promotion eligibility at M5 is the first place
that happens. Subsumption buys nothing for 12 weeks against 84 days.

Four reasons not to adopt now, in order of weight.

1. Dependency surface. SigmaKEE is Java with a 16 GB requirement per row 29,
   Vampire is a separate binary, and `CLAUDE.md` section 2.10 requires
   `./build.sh` to succeed on a fresh clone with stdlib Python.
2. The paper's own results. Two of four negative queries did not complete
   against the full knowledge base under the resource bound. A verdict that
   is "open at this scale" is not a verdict this project can publish.
3. Licensing. The IEEE-versus-GPL contradiction from row 28 is unresolved and
   the paper does not address it.
4. Independence. Fifth source, same author.

**The critical path.** The paper closes over the ROE implementation message
because that message is authoritative and complete. This project's DoD tier is
not yet transcribed (B3, `ACTION-REGISTER.md` section 0). No technique in the
paper substitutes for reading the issuance.

## Verdict

**ADAPTED.** Four mechanisms adopted in this project's own vocabulary and
stdlib tooling. The formalism stays at row 28's EVALUATE with a sharper
trigger. Nothing here reopens the encoding, the schema, the identifier grammar,
or the build.

Confidence 0.85 on the reading of the paper, which was read in full. 0.7 on
the venue, which is inferred from a filename and recorded as UNCONFIRMED.
