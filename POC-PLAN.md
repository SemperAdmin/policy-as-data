# POC plan - GOATS by Semper Admin

Date: 2026-08-08. Owner: Stephen. Author role: senior developer, per `CLAUDE.md`.
Status: **proposed, not adopted.** Three blocking questions in section 11.

---

## 0. First, a disagreement

**I would not rebuild this.** The word "rebuild" appeared in the tasking and it
does not survive contact with the measured state.

What already works, measured rather than asserted:

```
56 canonical documents, 20,178 provisions
56 exports, ALL VALID against usmc-issuance-2.0.xsd
77 pages, 870 internal links, 0 dead, 0 orphans
362 authority edges, 85 revision-drift findings
verify_authority PASS   check_site PASS   idempotent, proven by hashing
```

Plus a defect register in `SESSION_HANDOFF.md` section 10 recording roughly
twenty traps already paid for: reference (a) being deleted by `HDR_RX`,
signature blocks parsing as provisions, chain short-circuiting on absolute tier,
torn records on interrupt, corrections arrays counting builds instead of
changes. A rebuild discards that register and re-finds every one of them.

**What is actually unproven** is one layer up. The project's claim is that the
encoding is faithful and addressable. It has proven that. It has not proven the
encoding is **useful** - that anything worth having can be computed from it that
could not be computed from the PDFs.

That gap is where the POC belongs. Everything below scopes to it.

If "rebuild" meant something else - a different corpus, a different runtime, a
service rather than a static site - say which, because the plan changes
completely and none of the reasoning below applies.

---

## 1. Evidence state

### Confirmed

- The encoding, the schema, the identifier grammar, and the build are working
  and idempotent. Sources: `SESSION_HANDOFF.md` section 3, `BUILD.md`.
- A rules layer exists for exactly **two** documents:
  `data/maradmin-051-23.rules.json` (5 rules, all VERIFIED, each cited to
  paragraph) and `data/dodi-1327.06.rules.json` (1 rule, UNVERIFIED).
- `tools/evaluate.py` computes MPLP decisions where every output line carries a
  citation, values come only from `rules.json`, questions beyond the encoded
  rules are **refused by name**, and any UNVERIFIED input downgrades the whole
  result visibly. That discipline is the project's most valuable asset and it is
  correct.
- The same entitlement is stated at two tiers in two units: DoDI 1327.06 says
  **12 weeks**, MARADMIN 051/23 says **84 days**. They agree numerically. The
  agreement is currently invisible to any tool.
- 85 of 362 edges are revision-drift findings, produced by extraction.

### Assumptions

- The audience for a decision is a Marine, an S-1, or an IPAC clerk who today
  reads the MARADMIN and counts days by hand. **Unvalidated.** No user research
  is recorded anywhere in the tree.
- "Digital-ready" in the charter means machine-checkable, not merely machine-
  readable. The whole plan below rests on this reading.

### Unknowns

- Whether any real user would trust a computed entitlement without a human
  signature. This determines whether the output is a decision or a worksheet.
- Whether the DoDI section bodies can be obtained and transcribed. `REFERENCES.md`
  records acquisition as human-in-the-loop and marks `dodd/5124.02` and the ASN
  MPLP guidance as blocked.
- Reuse terms of the repository's own artifacts. No `LICENSE` exists.

### Technical implications

`evaluate.py` reads five rule IDs by literal string in `main()`
(`MAX_PARENTAL_LEAVE_DAYS`, `ENTITLEMENT_WINDOW_DAYS`, `MIN_INCREMENT_DAYS`,
`MAX_INCREMENTS`, `EVENT_PROXIMITY_MERGE_HOURS`) and encodes the logic in Python
around them. `rules.json` carries **values, not logic**. That is a defensible
split, and it means "generalize the evaluator" is not a refactor. It is a
decision about whether policy logic becomes data.

---

## 2. Recommendation

**Recommendation.** Build a cross-tier **rule reconciliation** POC. For a named
rule concept, collect the value stated at every tier of the authority ladder,
normalize units, and report whether the tiers **agree**, **diverge**, or whether
a tier is **not held**. Every value cited to the paragraph that states it. Any
UNVERIFIED input downgrades the finding on its face.

The question it answers, in one line: **does the Marine Corps implementation
match the authority it claims to implement?**

**Why.**

1. It is the compliance failure the Rules as Code source names directly:
   "Multiple implementations of identical regulations create compliance risks.
   The Dutch pension age rule is referenced 100+ times... but likely
   reimplemented differently in numerous systems"
   (`resources/17-rules-as-code.md`). Nobody can check that today at any scale.
2. It cannot be done without this encoding. A search index over PDFs cannot
   answer it. That makes it a real proof of the concept rather than a
   demonstration of a feature.
3. It reuses three proven assets - the authority chain, the citation discipline,
   the drift report - and adds one small new thing.
4. It extends the project's existing strength. The drift report already answers
   "is this citation pointing at a current edition." Reconciliation answers "and
   does the thing it points at say the same number." Same shape, one level
   deeper.
5. The 12-weeks / 84-days pair is a **working example already in the repository**
   that no tool currently notices. A POC with a live example on day one is worth
   more than one that needs a corpus built first.

**Risks.**

- **The critical path is transcription, not code.** Reconciliation needs at
  least two tiers carrying values for the same concept. Today the DoD tier
  carries one UNVERIFIED value whose own note says "the section body is not yet
  encoded, so the exact value and source line are not yet confirmed." Until
  DoDI 1327.06 para 3.11.c is encoded and verified, the POC has one honest
  comparison and it is half-unverified. **This is the highest risk in the plan
  and it is not a software risk.**
- **Agreement is a weak result.** If every tier agrees, the report says nothing
  interesting and a reviewer asks what it bought. Mitigation: the report must
  make **not held** and **not comparable** first-class results, because the
  absence of an encoded DoD tier under a service rule is itself a finding.
- **Unit normalization invites false precision.** 12 weeks equals 84 days only
  if a week is 7 days in that context. Convert only through an explicit,
  reviewable table and refuse anything not in it.
- **Concept identity is the hard part.** Deciding that
  `CURRENT_DOD_PARENTAL_LEAVE_WEEKS` and `MAX_PARENTAL_LEAVE_DAYS` describe the
  same concept is a human judgement. Make it explicit data, never an inference
  from name similarity. Name-matching here would be exactly the "gap closed by
  numbering proximity" the project forbids.

**Alternatives considered.**

| Option | What it proves | Why not first |
|---|---|---|
| **B. Generalize `evaluate.py` to a second domain** | the decision engine is not a one-off | Real value, but it proves engineering generality rather than the concept. Also the larger build: a second domain needs its own logic, and the P0 question "does policy logic become data" is a months-long question, not a POC. |
| **C. Whole-of-government portability - encode a civilian agency** | the identifier grammar generalizes | Low information. `/us/<department>/<service>/<doctype>/` is department-agnostic by construction per `NAMESPACES.md`, so this mostly confirms a design property. It is transcription labour carrying little technical risk. It becomes valuable **after** something works, as the scaling proof. |
| **D. SemperScribe integration, the DRPM upstream thesis** | structure at authoring time removes extraction | Strongest long-term play, and `resources/18` says so. Depends on a second codebase and an open owner decision (`SESSION_HANDOFF.md` section 7.3). Too many dependencies for a POC. |

**Next step.** Answer the three blocking questions in section 11. Then Milestone
0, which is transcription and takes no code.

---

## 3. Project discovery

**1. Objective.** Make it machine-checkable whether a service-level issuance
faithfully implements the DoD or statutory authority it cites, with every claim
traceable to a paragraph.

**2. Target users.** Primary for the POC: the policy sponsor or action officer
who owns an issuance and must answer "is this still right." Secondary: the
reviewer or inspector who must verify it independently. Not the individual
Marine. A consumer-facing entitlement calculator is a different product with a
different liability profile, and mixing them is how the scope dies.

**3. Current process.** A human opens the MARADMIN, opens the DoDI it cites,
finds the corresponding paragraph, compares the numbers, and does it again next
year. Nothing records that it was done. Nothing notices when the DoDI reissues.

**4. Proposed process.** Values are encoded once, at the paragraph that states
them, with a concept label. A tool walks the authority chain, compares by
concept, and publishes a report. Reissuance changes an input and the report
changes with it.

**5. Pain points.** Silent divergence after a reissuance. No record that a check
was performed. No way to ask the question across more than a handful of
documents. Three current MCOs already cite a DoDI cancelled in March 2022 and
that was found by the drift report rather than by anyone reading them.

**6. Requirements.** Section 4.

**7. Constraints.**

- Python 3, standard library first. The standalone-clone property depends on a
  thin dependency surface (`CLAUDE.md` section 11).
- Static output. No server, no database, no auth. `docs/` is served by GitHub
  Pages and cloud.gov.
- `canonical/` is read-only to tooling. Contact masking at the export boundary.
- Every new build stage must be idempotent and remove its own prior output.
- Acquisition is human-in-the-loop. The environment cannot fetch marines.mil,
  DoD, or GPO sources.
- The device bridge has a 45-second command cap and `build.sh` takes ~56
  seconds. Run stages individually or run natively on Windows.
- No `LICENSE`. Distribution is blocked until that is fixed.

**8. Success criteria.** Section 9.

---

## 4. Requirements, prioritized

### P0 - required to prove the concept

| # | Requirement | Note |
|---|---|---|
| P0.1 | A **rule concept register** in `config/`: a controlled vocabulary of concepts, each with an id, a definition, and a canonical unit. | The missing primitive. Rule ids today are per-document strings. Concepts are what make two tiers comparable. |
| P0.2 | `rules.json` gains a `concept` field per rule, referencing the register. Existing files migrate. No other schema change. | Additive. Keeps `id`, `value`, `unit`, `status`, `citation`, `note`, `corrections` exactly as they are. |
| P0.3 | An explicit unit conversion table, in `config/`, reviewable, with refusal as the default for anything absent from it. | `weeks -> days` at 7. Nothing implicit. |
| P0.4 | `tools/reconcile.py`: for each concept, walk the authority chain, gather every tier's value, normalize, and emit `AGREE` / `DIVERGE` / `NOT_HELD` / `NOT_COMPARABLE`. | One tool, one job. |
| P0.5 | Every emitted line carries the citing identifier and paragraph label for each tier. | Non-negotiable. Same discipline as `evaluate.py`. |
| P0.6 | Any `UNVERIFIED` input downgrades the finding visibly, and the downgrade names which rule caused it. | Mirrors `evaluate.py`'s confidence line. |
| P0.7 | A refusal register: concepts present but not comparable, and why. | An engine that answers beyond its data is the failure mode this project exists to prevent. |
| P0.8 | DoDI 1327.06 para 3.11.c encoded and promoted to VERIFIED, so one comparison is real end to end. | **Transcription, not code. Critical path.** |
| P0.9 | Output rendered as one page in `docs/`, linked from the leave spine. | Reuses the existing renderer pattern. |
| P0.10 | The stage is idempotent and proven by hashing. | `CLAUDE.md` section 2.8. |

### P1 - needed for a usable MVP

- A second spine reconciled, to test that the design is not shaped around leave.
- `reconcile` findings surfaced on each policy page, not only on a report page.
- `verify_authority` extended to fail the build on a malformed concept reference.
- `LICENSE` and `NOTICE`. Already P0 in `CLAUDE.md` for distribution; P1 here
  because the POC can be evaluated internally without it.

### P2 - useful, and not now

- Generalizing `evaluate.py` past MPLP.
- Provision-kind controlled vocabulary, from the S1000D `infoCode` idea in
  `conformance-matrix.md` section 9.
- Reconciliation across editions of the same document, not only across tiers.

### P3 - future

- Civilian-agency corpus and the whole-of-government claim.
- SemperScribe authoring integration.
- Any API, service, database, or authenticated surface.

**Guard.** If a proposal needs a database, a queue, a web framework, or an
account system, it is P3 by definition for this POC. Say so and move on.

---

## 5. Architecture

No new components. One new tool, two new config files, one new page.

```
config/rule_concepts.json     NEW   the concept register
config/units.json             NEW   the conversion table, explicit
data/*.rules.json             EDIT  add `concept` per rule
tools/reconcile.py            NEW   walk chain, compare, emit findings
tools/render_*.py             EDIT  one report page + per-policy surfacing
docs/reconciliation.html      NEW   the report
```

Data flow:

```
authority chain (built)  +  rules.json per tier  +  concept register
                              |
                        tools/reconcile.py
                              |
              findings JSON  ->  renderer  ->  docs/
```

**Interfaces.** `reconcile.py` reads only committed files and writes one
findings artifact plus its rendered page. It never writes `canonical/`, never
writes `data/`, and never promotes a status.

**Storage.** Files. No database. At 56 documents and a handful of concepts the
working set is kilobytes.

**Authentication and authorization.** None. Nothing in the POC is
user-specific, and there is no write path from a browser. If a future version
accepts user input, that is the moment auth becomes a requirement, not before.

**Error handling.** Missing rule file, unknown concept, unknown unit, and
unresolvable chain each produce a named finding, never a crash and never a
silent skip. A concept present at one tier and absent at another is `NOT_HELD`,
which is a result, not an error.

**Deployment.** Unchanged. A stage in `build.sh`, output into `docs/`.

---

## 6. Data requirements

The concept register is the only genuinely new data structure. Proposed shape,
deliberately thin:

```json
{
  "concepts": [
    {
      "id": "PARENTAL_LEAVE_MAX_DURATION",
      "label": "Maximum parental leave authorized for a qualifying event",
      "canonical_unit": "days",
      "definition": "The total parental leave a member may use arising from a single qualifying event.",
      "established": "2026-08-08",
      "basis": "Owner assignment. Concept identity is a human judgement and is recorded, never inferred."
    }
  ]
}
```

Then `MAX_PARENTAL_LEAVE_DAYS` (84 days, VERIFIED, MARADMIN 051/23 para 11.d)
and `CURRENT_DOD_PARENTAL_LEAVE_WEEKS` (12 weeks, UNVERIFIED, DoDI 1327.06 para
3.11.c) both carry `"concept": "PARENTAL_LEAVE_MAX_DURATION"`, and the tool has
something to compare.

**Two rulings this needs, and I recommend both.**

1. **Concept assignment is `cited`-grade or it does not exist.** A concept is
   attached by a human who read both paragraphs. It is never inferred from rule
   id similarity, unit compatibility, or subject proximity. Same rule as edges.
2. **A concept with one tier is still published**, as `NOT_HELD` against the
   tiers the chain names. The absence of an encoded DoD authority under a
   service rule is the finding, exactly as the MOS spine naming no DoD authority
   is a finding today.

---

## 7. Security and privacy

- **No new exposure surface.** No user input, no network listener, no
  credentials. The POC reads committed files and writes static output.
- **Contact masking is untouched**, because `reconcile.py` reads `data/` and
  `config/`, not `canonical/`. If any future version reads the store, it needs
  `tools/contact_guard.py` in its path.
- **The real risk here is not technical, it is publication risk.** A page that
  says "the Marine Corps implementation diverges from DoD authority" is a
  compliance assertion about a live issuance. Two controls, both required:
  the page must state that it compares **encoded values**, not the issuances
  themselves; and every DIVERGE finding must print both paragraphs in full so a
  reader adjudicates rather than trusts. Publishing a bare verdict would be the
  most damaging thing this project could ship.
- **Still open, inherited:** no `LICENSE`, no `NOTICE`, and exported XML carries
  no authority statement.

---

## 8. Milestones

**M0 - transcription. No code.** Encode DoDI 1327.06 para 3.11.c and 3.11.d
from the authoritative text, promote to VERIFIED, record the promotion. Without
this the POC has no real comparison. Blocked on you having the source text.

**M1 - the register.** `config/rule_concepts.json` and `config/units.json`, with
one concept and one conversion. Add `concept` to the six existing rules.
Deliverable: two files and a migration of two rules files.

**M2 - the tool.** `tools/reconcile.py`, one concept, two tiers, four verdicts,
citations on every line, refusal register. CLI first, JSON out. No rendering.
Deliverable: a findings artifact you can read.

**M3 - the gate.** Idempotence proven by hashing. Malformed concept references
fail the build. Deliverable: a build stage.

**M4 - the page.** Render into `docs/`, link from the leave spine, both
paragraphs printed for any DIVERGE. Deliverable: a page a reviewer can be shown.

**M5 - the generality test.** Second spine, second concept family. This is the
milestone that decides whether the design was shaped around leave. Deliverable:
an honest answer, including "no" if that is the answer.

Stop after M4 and evaluate. Do not start M5 until M4 has been shown to someone
who did not build it.

---

## 9. Success criteria

Measurable, and the POC fails if these are not met.

| # | Criterion | Measure |
|---|---|---|
| S1 | A real cross-tier comparison exists end to end | At least one concept with a VERIFIED value at two tiers, both cited to paragraph |
| S2 | Findings are traceable | 100% of emitted lines carry an identifier and a paragraph label. Zero uncited claims. |
| S3 | The tool refuses rather than guesses | Every non-comparable concept appears in the refusal register with a reason. Zero silent skips. |
| S4 | Unverified inputs are visible | Any finding using an UNVERIFIED rule is downgraded and names the rule |
| S5 | It is idempotent | Two runs, hashed, byte-identical |
| S6 | It finds something a human did not already know | At least one `DIVERGE` or `NOT_HELD` finding that was not on anyone's list beforehand. **If this is zero across two spines, the concept is not proven, and say so.** |
| S7 | It survives a second domain | M5 completes without a redesign of the concept register or the tool interface |

S6 is the one that matters. S1 through S5 prove the machinery works. S6 proves
the machinery was worth building.

---

## 10. Explicitly out of scope

Named so they cannot creep back in as "small additions."

- Any database, message queue, container orchestration, or web framework.
- Any authenticated or user-specific surface.
- Any LLM or statistical component in the decision path. The project's position
  is symbolic and human-confirmed, and `resources/17` records that this matches
  the Rules as Code position.
- Generalizing `evaluate.py`.
- Civilian-agency documents.
- SemperScribe.
- Reopening the period ruling in the verified tier (`SESSION_HANDOFF.md` 7.2),
  the `[ID2]` promotion (7.1), or the namespace split.
- Any claim of whole-of-government capability. `CHARTER.md` section 5 governs.

---

## 11. Questions

### Blocking - answer before M1

**B1. May a finding be published from an UNVERIFIED value at all?**
`evaluate.py` today emits with a downgrade banner. For an entitlement affecting
a Marine's leave, I would argue the opposite: refuse, and print only what is
missing. A downgraded number still gets screenshotted and forwarded without the
banner. My recommendation is **refuse for values, downgrade for structure** -
say "DoD tier not verified" rather than "DoD says 12 weeks, unverified." Your
call, and it shapes the tool's core behaviour.

**B2. Which second spine for M5?** Not MOS - `SESSION_HANDOFF.md` records that
the MOS spine names no DoD authority at all, so it has no tier to reconcile
against. Promotion reaches T0/T1/T3 and fitness reaches T1/T3/T5. **I recommend
promotion**, because it reaches statute and a cross-tier test that touches T0 is
a stronger proof than one that stops at DoD.

**B3. Can you get DoDI 1327.06 para 3.11.c and 3.11.d text?** M0 depends on it
entirely. If it is not obtainable, the POC needs a different concept where two
tiers are already encodable, and I would want to pick that before writing any
code rather than after.

### Important - affect design, not blocking

**I1.** Is the reconciliation report a **published page** or an **internal
artifact**? Publishing a divergence finding about a live issuance is a
different risk posture, and section 7 assumes published with both paragraphs
printed.

**I2.** Does a concept get an identifier in the `/us/...` space, or does it live
outside it? I recommend outside. Concepts are this project's analytical
vocabulary, not jurisdiction facts, and putting them in the identifier space
implies an authority that does not exist.

**I3.** How many concepts for the POC? I recommend **one**, extended to three
only at M5. A register of thirty concepts before the tool exists is scope
inflation wearing a data-modelling costume.

### Optional - later

**O1.** Should reconciliation also run across editions of the same document?
That is a different question with the same machinery, and it is P2.

**O2.** Does the concept register want a `superseded_by` field for when a
concept splits? Not until one splits.

---

## 12. Confidence

0.8 on the analysis. Every state figure is quoted from a file in the tree, and
the 12-weeks / 84-days pair was read directly from the two `rules.json` files.

0.6 on the recommendation, and B1 through B3 are why. If DoDI 1327.06's section
bodies are not obtainable, the critical path breaks and option B or C becomes
the better first move. The user assumption in section 1 is also unvalidated,
and a POC built for a user who does not exist is the most expensive kind of
correct engineering.
