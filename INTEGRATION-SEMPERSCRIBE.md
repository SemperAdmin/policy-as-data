# SemperScribe integration - design

Date: 2026-08-08. Owner: Stephen. Status: **proposed. Not adopted, and it is not
in the POC.** Scope decision required, section 9.

Supersedes nothing. Extends the Option A / Option B choice recorded open in
`SESSION_HANDOFF.md` section 7.3.

---

## 1. The workflow as described

> Policy is built in SemperScribe, which needs to reference existing policies in
> policy-as-data. The finally approved product is exported from SemperScribe and
> then added to policy-as-data.

Two separate integrations wearing one sentence. They have different consumers,
different failure modes, different data, and different risk. Build them
separately and in this order.

```
  READ                                          WRITE
  author needs to cite an existing policy       approved product enters the corpus

  SemperScribe  <---- reference index ----      ???
                                                SemperScribe ---- NLDP ----> staging ---> canonical/
```

The `???` is deliberate. Section 3 shows the read direction cannot be served by
this repository, and naming the right source is the first decision.

---

## 2. Evidence state

### Confirmed

- Option A is already the recommended shape: `tools/nldp_to_canonical.py`, a
  bridge in this pipeline reading SemperScribe's Naval Letter Data Package JSON
  and emitting a canonical record. Zero changes to SemperScribe, keeps XSD logic
  in one place. Option B is native TypeScript export in SemperScribe, better
  long-term, duplicates the logic. **Neither is built.** Source:
  `SESSION_HANDOFF.md` 7.3.
- SemperScribe implements MCO 5215.1K structure: Situation, Mission, Execution,
  Cancellation. Source: `MOVED.md`.
- `canonical/` is the store of record and read-only to tooling. Contact masking
  happens at the export boundary. Source: `DATA_CONTRACT.md`, `README.md`.
- The corpus here is **56 documents**. GunnyBot holds **17,514**.
  `config/revision_index.json` holds 17,514 identifiers, **identifiers only, no
  titles, no text, no contacts**. Source: `SESSION_HANDOFF.md` sections 3 and 9.
- The identifier grammar, the period ruling, and every allocated token live in
  `NAMESPACES.md` and nowhere else.

### Assumptions

- SemperScribe holds a reference list per document and an author picks entries
  into it. **Unvalidated.** If references are free text today, the read
  integration is a bigger change than this document assumes.
- An approved product means signed and promulgated, not merely routed. Section 6
  depends on this.

### Unknowns, and none of these may be guessed

- **The NLDP schema.** Its fields, whether provisions are structured or a text
  blob, how enclosures and references are represented, whether paragraph
  numbering survives. Everything in section 5 is a requirement list, not a
  mapping, because the mapping cannot be written without it.
- Whether SemperScribe can emit at all today, or needs the exporter written.
- Whether SemperScribe holds any record of the signed artifact, or only the
  authored content.
- Whether an approved SemperScribe product is the **issuance of record** or a
  draft of it. Section 4 turns on this.

---

## 3. The read direction, and why it does not point here

**A reference lookup pointed at policy-as-data would fail for roughly 99.7% of
real lookups.** 56 documents against a Marine Corps universe of 17,514. An
author searching for the MCO they need finds nothing and concludes the tool is
broken.

That is not a hypothetical. It is a defect this project already found and fixed
at a different layer, recorded in `SESSION_HANDOFF.md` section 10:

> Search indexed the wrong corpus. 17,507 documents against 57 pages... roughly
> 99.7% of every result set was a link to nothing. A search box that mostly
> dead-ends teaches a visitor the library is broken rather than that it is small.

Wiring SemperScribe to this repository's corpus re-runs that defect at the
integration layer, with an author instead of a visitor. **I would not do it.**

### What to point it at instead

| Option | Coverage | Problem |
|---|---|---|
| policy-as-data corpus | 56 | Fails 99.7% of lookups. Reject. |
| `config/revision_index.json` | 17,514 | Identifiers only. An author picking a reference needs a title and a date to recognise it. Not sufficient alone. |
| **A reference index emitted by GunnyBot** | 17,514 | **Recommended.** Identifier, title, issuance date, lifecycle, superseded-by. Nothing else. |

**Recommendation.** GunnyBot emits a flat reference index - identifier, title,
date, lifecycle, superseded-by, and nothing more. SemperScribe consumes that
file. policy-as-data consumes the same file to replace
`config/revision_index.json`, which currently answers the supersession question
with identifiers alone.

**Why this is the right shape.** It respects the line in `HANDOFF.md`: GunnyBot
owns the corpus at scale, this project owns the standard and the encoding. A
reference index is a corpus fact, so it belongs to GunnyBot. It also converts an
existing deliberate coupling into a documented interface, which is an
improvement to something already open in `SESSION_HANDOFF.md` section 9.

**Explicitly excluded from that index:** provision text, contact details, and
anything from a record whose `publication.publishable` is false. Seven Statement
C records are quarantined in the parent corpus and the gate does not relax
because the consumer changed.

**Risk.** This makes SemperScribe depend on a GunnyBot artifact. If GunnyBot
stops emitting, the picker goes stale silently. Mitigation: the index carries a
generation date and SemperScribe shows it. A stale date visible beats a stale
list invisible.

---

## 4. The write direction, and the question it forces

An approved product exported from SemperScribe is **not an extraction**. It was
never a PDF that a parser had to read. It arrives already structured, from the
system that authored it.

The whole two-tier VERIFIED / UNVERIFIED model exists because machine extraction
from a PDF is unreliable and a human must confirm it line by line. That
rationale does not apply to a record that was never extracted. Stamping an
authored record UNVERIFIED would be technically consistent and substantively
wrong, because it would say "a human has not confirmed this matches the source"
about a record that **is** the source.

**Three ways to resolve it. I recommend the third.**

| | Approach | Assessment |
|---|---|---|
| 1 | Stamp UNVERIFIED like any machine output | Consistent, and misleading. Also creates a permanent verification backlog for documents that need none. |
| 2 | Stamp VERIFIED on arrival | **Reject.** Verification means confirmed against the issuing authority's copy. An unsigned export is not that, and this would let a draft enter as authoritative. |
| 3 | **Add a third verification state, `AUTHORED`**, meaning the record came from the authoring system of record rather than from extraction, and carry the signed artifact's hash alongside it | Honest. Says exactly what happened. Promotion to VERIFIED then has a precise, machine-checkable meaning: the authored content matches the signed artifact. |

Option 3 makes verification computable for the first time in this project.
Everywhere else it is a human reading a PDF. Here it becomes: does the NLDP
content match the signed document that was promulgated. That is a test, not a
judgement.

**This is a schema change** to `usmc-issuance-2.0.xsd`'s `@verification` and to
the JSON contract. It is the largest single consequence of this integration and
it should not be made casually. It is also the strongest argument that this
integration is worth doing.

---

## 5. What the NLDP contract must carry

The mapping cannot be written until the schema is known. This is the requirement
list to check it against, and every gap is a conversation with SemperScribe
rather than an assumption to fill in.

| # | Required | Why |
|---|---|---|
| R1 | Document identity: type, number, edition, date | Without it the record cannot be identified or an identifier minted |
| R2 | **Structured provisions with their native designators**, in order and nested | The product is the encoding. A text blob means the parser runs anyway and the integration bought nothing. **This is the load-bearing requirement.** |
| R3 | The reference list as structured entries, each naming the issuance it cites | Edges are `cited` only when the source states the link. A prose reference list degrades every edge to unparsed. |
| R4 | Enclosures, distinguished from body | `ref/` and `encl/` are separate reserved namespaces per `NAMESPACES.md` N7 |
| R5 | Lifecycle: draft, routed, signed, promulgated, cancelled | Section 6. Only one of these may ingest. |
| R6 | Signature and promulgation date | The event that makes it an issuance |
| R7 | A hash or copy of the signed artifact | Makes the AUTHORED-to-VERIFIED promotion in section 4 computable |
| R8 | Contact fields flagged as such | The store is faithful and masking is at the export boundary, so contacts must be identifiable to be masked |
| R9 | Cancellation and supersession statements | Feeds the drift and lineage reporting that already exists |

**If R2 is not met, stop.** An NLDP carrying unstructured text is a slightly
better PDF, and the bridge should not be built until it carries structure. Say
this plainly to whoever owns SemperScribe, because it is the requirement that
decides whether the integration is worth anything.

---

## 6. Ingest path

```
SemperScribe  --NLDP.json-->  incoming/  --nldp_to_canonical.py-->  staging/
                                                                      |
                                                    owner review + explicit promotion
                                                                      |
                                                                  canonical/
```

**Rules, each traceable to an existing constraint.**

1. **Nothing writes `canonical/` directly.** `DATA_CONTRACT.md`. Ingest writes
   `staging/`, mirroring GunnyBot's `canonical_staging` and the `[ID2]`
   promotion pattern already established.
2. **Promotion is explicit, human, and recorded.** Never a side effect of a tool
   running. `CLAUDE.md` section 2.3.
3. **Only `signed` or `promulgated` documents ingest.** A draft in the corpus of
   record would be the worst possible defect this project could ship, because
   the site presents its contents as policy. Drafts are rejected with a named
   reason, not silently skipped.
4. **Identifiers are minted here, not in SemperScribe.** SemperScribe may
   propose one; this repository mints the authoritative form. Two
   implementations of the period ruling in two codebases is precisely the
   "multiple implementations of identical regulations" risk in
   `resources/17-rules-as-code.md`. One implementation, in the repository that
   owns `NAMESPACES.md`.
5. **File-based and asynchronous. No network call, no live API.** `README.md`
   requires `./build.sh` to succeed on a fresh clone with nothing else present.
   A service dependency ends that. A file that is absent is simply an ingest
   with nothing to do.
6. **Ingest is idempotent.** Re-ingesting the same NLDP produces a
   byte-identical staging record. Proven by hashing.
7. **Every ingested provision records its origin** as the NLDP and its
   generation, so an authored record is never confused with an extracted one.

---

## 7. Security and privacy

- **Contact data.** Naval correspondence carries a drafter, phone, and email by
  construction. Those enter `canonical/`, which is correct and is why
  `canonical/` is unpublished, but the ingest path must flag them (R8) so
  `tools/contact_guard.py` can mask at export. An ingest path that loses the
  flag publishes a phone number.
- **Draft leakage is the top risk.** Pre-decisional policy drafts are more
  sensitive than the signed product. Rule 3 in section 6 is the control, and it
  belongs at ingest rather than at render, because by render time the draft is
  already in the store.
- **Provenance of the incoming file.** Nothing in a JSON file proves
  SemperScribe wrote it. For the POC this is an accepted shortcut and must be
  named as one. Before production the file needs signing or an authenticated
  transfer, or the corpus of record accepts anonymous input.
- **The quarantine gate does not relax.** `publication.publishable == false` is
  never exported, rendered, or ingested, and a new ingest direction does not
  create an exception.

---

## 8. What I would not build

- **A live API between the two systems.** Ends the standalone property, adds
  auth, and buys nothing a file does not.
- **A shared database.** Two systems, one store, and no clear owner is how the
  read-only mandate dies.
- **Round-tripping.** policy-as-data writing back into SemperScribe. It creates
  two masters for one document and the reconciliation problem this project was
  built to detect.
- **Reference-picker UI inside this repository.** The picker belongs in
  SemperScribe. This side supplies the standard and, through GunnyBot, the
  index.

---

## 9. The scope decision, and it is yours

**This is not in the POC, and adding it silently would break the plan.**
`POC-PLAN.md` puts SemperScribe integration at P1 and section 10 names it out of
scope. That was deliberate: it depends on a second codebase, an unknown schema,
and an owner decision that is still open.

Three honest options.

| | Option | Assessment |
|---|---|---|
| **A** | **Keep reconciliation as the POC. Treat this document as the design for the next phase.** | **Recommended.** Reconciliation needs nothing outside this repository and can be finished. This integration cannot start until the NLDP schema is known, which is not a thing you control today. |
| **B** | Replace the POC with the authoring loop | Defensible. It is the DRPM thesis and the charter's strongest claim, and section 4 shows it makes verification computable. Costs: a schema you do not have, a second codebase, and a `@verification` schema change. Higher value, much higher risk, and the plan should be rewritten rather than amended. |
| **C** | Run both | **Reject.** Two POCs is no POC. This is the P2-creep the plan exists to stop. |

**Recommendation: A.** Do one thing that finishes.

**What to do now regardless of the choice, because both need it and neither
starts without it:**

1. Get the NLDP schema, or confirm no exporter exists yet. Everything in
   sections 4, 5, and 6 is provisional until then.
2. Ask whoever owns SemperScribe whether R2, structured provisions with native
   designators, is met. If it is not, this integration is not worth building
   yet, and knowing that costs one conversation.
3. Decide whether an approved SemperScribe product is the issuance of record or
   a draft of it. Section 4 does not resolve without it.

---

## 10. Confidence

0.85 on the analysis of the read direction. The corpus counts and the
prior search defect are quoted from `SESSION_HANDOFF.md`, and the arithmetic is
the same arithmetic that produced the original defect.

0.5 on the write direction, and section 2's unknowns are why. The NLDP schema is
unknown, so section 5 is a requirement list rather than a mapping and section 6
is a shape rather than a design. Nothing here should be built against it until
R1 through R9 have been checked against the real schema.

The `AUTHORED` proposal in section 4 is the one idea worth arguing about even if
the rest is deferred. It is a schema change, it is the largest consequence of
this integration, and it is also the first time verification in this project
becomes a computable test rather than a human judgement.
