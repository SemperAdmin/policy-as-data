# What we are trying to do, and what is wrong with what we built

Date: 2026-09-15. Owner: Stephen. Status: **proposed. Nothing here is decided.**

Written at the owner's request after five sources were logged in
`CONCEPT-EVIDENCE.md` and building was put on hold. Every claim traces to a
source in that file or to a measurement in this repository. Where it is my
inference rather than someone's words, it says so.

This file states a concept and names what is wrong with the application built
against the old one. It does not change `POC-PLAN.md`, `SITE-PLAN.md`, or
`ACTION-REGISTER.md`. When the owner settles the concept, whichever of those is
wrong gets corrected rather than quietly abandoned.

---

## 1. The objective, in one sentence

> **Policy is written to be read one document at a time. Every question anyone
> actually has crosses documents.**

That is the problem. The objective follows from it:

> **Make policy answerable to questions that span more than one document, and
> make every answer show its work.**

This is not a new framing. It is the one already present in five sources, said
five ways by four people.

| Who | Their words | The crossing |
|---|---|---|
| Shorter, S2 | "right now we do it in like 17,000 different ways" | Everyone re-derives the crossing by hand, and differently |
| Chiofalo, S2 | "what other documents does this affect?" | One document, outward |
| Gannon to GPO, S4 | "the time we spend doing this administrative stuff is the time we're not focused on warfighting" | The cost of re-deriving it by hand, every time, by everyone |
| Gannon quoting a user, S5 | "I need to fix all the orders in my command. How do I do that?" | Many documents, one command, then across services |
| The built product | does this order state what the authority above it states | One document, upward |

**Why "show its work" is half the sentence.** A cross-document answer that
cannot be checked is worse than no answer, because it travels. The whole
provenance discipline exists to make the crossing checkable, and it is the
reason this is not simply a search box.

---

## 2. The three layers

Only the third is contested. The first two are done and are the asset.

**Layer 0, the encoding.** A paragraph is the addressable unit. Its identifier
is stable and jurisdiction-first. A reference becomes a link only when the
target paragraph is confirmed to exist; a citation that cannot be resolved
produces no link rather than a plausible one. Measured: 56 documents, 20,178
provisions, 362 cited edges, `verify_authority` passing.

**Layer 1, the provenance discipline.** Cited is never conflated with inferred.
Machine output is never trusted. A gap is stated and never closed by inference.
A cited edition is never silently upgraded. A value no person has read is
withheld rather than shown with a caveat. Measured: an attestation ledger bound
to content hashes, a claims table of 18 rows with 7 negatives, an idempotent
build proven by hashing 773 files.

**Layer 2, the answers.** Products standing on layers 0 and 1. Seven candidates
are in play, they have different users, and they are not the same product.

| # | Answer | Whose words | Built |
|---|---|---|---|
| A | What does this change affect | Chiofalo, and the Directive Control Point question | Data exists, view does not |
| B | Does this order match its authority | `POC-PLAN.md` | Yes. The whole site |
| C | A corpus a model or a method can interrogate | Shorter | The enabling discipline exists, unnamed |
| D | How a directive is made, structured at birth | Shorter, SemperScribe | Deferred |
| E | Training and Readiness | Gannon, **confirmed 2026-09-15** | No. Zero held |
| F | Time returned to warfighting | Gannon, to GPO | No. Nothing measures time |
| G | Fix all the orders in my command | Gannon, quoting a user | No. Everything reports; nothing remediates |

**Every one of the seven is layer 2.** That is why each of them felt like "the
concept" when it came up. They are all real, they all stand on the same two
layers, and the sentence that says so was never written down. That absence is
the skew, not any one of the seven.

---

## 3. What is wrong with the application

Six, ranked by what kills the project rather than by size.

### 3.1 It answers a question nobody asked

Across five sources, **not one person asked whether an order matches the
authority above it.** That question is the entire site.

Reconciliation is a genuine crossing. It is also the narrowest one, and it
needs four gates before it says anything: both sides encoded, both sides read
by a person, concepts mapped by hand, units convertible through an explicit
table. That is why it currently produces one agreement and four withheld
comparisons. The discipline is right and the output is honest. The product is
narrow.

The impact question needs one thing, and it already exists:

| Already built | Measured |
|---|---|
| Cited edges | 362 |
| Distinct documents named as targets | 271 |
| Inbound edges per document | computed in `lineage.build_inbound`, used on every policy page |
| Stale citations found | 85 |
| Current documents citing something no longer in force | 4 |

**This was the largest thing wrong. Addressed 2026-09-15:** `currency.html`
and `impact.html` are built, every policy page frames its dependents as what
a reissue would touch, and the home page opens on the currency finding.
Reconciliation stays as the second act.

### 3.2 The proof is at a scale where the tool is not needed

56 documents. A person can do 56 by hand, so nothing here is yet
indispensable, and a reviewer who checks the number will see that.

The pain is roughly 17,500 documents done 17,000 ways. The 85 stale references
out of 362 is the most striking figure the project has produced, and its force
comes entirely from what the same measurement would return across the real
corpus. `config/revision_index.json` already holds 17,514 known identifiers.

**Run 2026-09-15, read-only, 169 seconds.** Across 17,507 documents, 887 in
force cite an instruction the corpus holds as cancelled; 5,169 of 21,198
references name a superseded edition; 6,005 name something not held. Seven
records carrying a limited distribution statement were skipped and counted,
never read. `docs/scale.html`, and the home page.

The demonstration corpus was chosen for depth, and that was right: depth proved
the encoding. **The encoding is proved. The next proof is breadth,** and
breadth is what makes the value legible to someone who has not read the code.

### 3.3 Nothing measures what the pitch sells

Candidate F is priced in time. The project counts documents, references,
findings, and confirmed values. Not one minute.

Gannon's five performance claims in S5 are unmeasured anywhere in the tree, and
one is wrong as stated. Measured for the first time on 2026-09-15:

| Claim | Measured |
|---|---|
| Takes up less space | Wrong against the text. MCO 1050.3J holds 132,953 characters; its XML is 298,372 bytes, about 2.2x |
| Takes up less space | Right against the source. DoWI 1327.06 is a 924,431 byte PDF |
| Low bandwidth, machine to machine | **Right, and this is the number.** One provision is 164 bytes against a 924,431 byte PDF |
| Decreases parse time | True, unmeasured |
| Decreases compute time | True, unmeasured |

`POC-PLAN.md` success criteria S1 to S7 all measure correctness. None measures
effort saved. If F is the pitch, the proof obligation is how long a person
takes to answer one of these questions today, and that has never been timed.

### 3.4 Nobody but the author can run it

- `canonical/` is gitignored. Zero of its files are in git. `build.sh` reads it
  at stage 1. **A fresh clone cannot build the site.** `CLAUDE.md` constraint
  10 states that a fresh clone builds. Both cannot be true.
- No contributing document, no governance, no triage. `CHARTER.md` section 5
  records the collaborative space as not started.
- The announcement recruited volunteers for schema work, a user interface, and
  a back end database. Four of the five asks are forbidden in writing in
  `POC-PLAN.md` section 10 and `ACTION-REGISTER.md` section 7.
- One verifier. The quorum deviation is in force and honestly recorded, and it
  is also a single point of failure for the entire verification claim.

A side project with interest from six directions and no way in dies of the
founder's calendar. That is not a hypothetical: Chiofalo's read is "they don't
want to make this a full-time project yet."

### 3.5 It explains itself in the wrong register

Ashe, already briefed in person, was lost in developer language and rescued by
a picture. `conformance-matrix.md` is 628 lines written for a standards
reviewer who has not appeared in any transcript. Every stakeholder who has
appeared needed less: a graph, a picture, a time argument, a peer conversation
about a grammar.

### 3.6 The programme converts nothing it generates

**Revised 2026-09-15. It is numbered sixth and it belongs second.** The first draft of this section said the
relationships live only in memory. That was too gentle. They also produce
concrete offers, and the conversion rate is zero.

| Opening | From | Cost to claim | State |
|---|---|---|---|
| Brief GPO's legislative branch data partners on the project | LaPlant, S6 | Reply yes | **Not followed up** |
| Present to Library of Congress, House, or Senate support staff | LaPlant, S6 | Reply yes | **Not followed up** |
| Amaya Ashe's wish list, due the 23rd | Ashe, S5 | One conversation | **Not followed up** |

The first two came from the body that publishes the standard this project
follows, after ninety minutes in which their response to the work was not a
correction but an offer to introduce it to the legislative data community.

This outranks most of what is above it. A narrow product can be re-pointed in a
week. An unanswered offer may not come back, and there is no evidence anyone
noticed these were offers.

**The recording problem underneath it is real too.** Four load-bearing rulings
about GPO in this repository were reached by reading their published documents
rather than asking them, while GPO sat in a room for ninety minutes. Pease, the
Directive Control Point, TECOM, and the Personnel Administration School are
recorded nowhere in the tree. `CLAUDE.md` section 16 exists to prevent exactly
this.

### 3.7 And the author of this file made 3.1 worse

On 2026-09-15 the site was rebuilt to tell the narrowest product's story
better, and two things were deleted on a judgement about an audience nobody had
defined: the sentences connecting the encoding to model use, contradicted by
Shorter in S2, and `visuals/04-pipeline-and-gates.svg`, contradicted by Ashe in
S5. The diagram is still on disk and referenced by nothing. With a concept
unsettled, deleting loses the option that reframing keeps.

---

## 4. What follows, if the concept above is accepted

One change carries most of it.

> **Point the application at what a change affects, across the whole corpus,
> and keep reconciliation as the deeper proof standing behind it.**

Why this one and not another:

- **It uses what exists.** The edges, the inbound index, the cited-versus-
  inferred basis, the drift classification. No new capability.
- **It answers a question three constituencies actually asked.** Chiofalo, the
  Directive Control Point, and by extension TECOM.
- **It has no verification gate.** An edge is cited or it is not. Reconciliation
  needs a human reading on both sides before it says anything; impact does not.
  So it says something on day one, at any scale.
- **It scales immediately.** The extraction for 17,514 documents already exists
  upstream.
- **It produces the sentence that lands.** Some number of orders in force today
  rest on something that no longer exists. At 56 documents that number is 4. At
  the full corpus it is unknown, and finding out is a measurement, not a build.

Reconciliation does not go away. It becomes the second act: here is the shallow
answer across everything, and here is the deep answer where two people have
read both sides.

**Where to point it, now that T&R is confirmed.** Three things that were
separate converge on one product:

- **A**, the impact question, is the one three constituencies actually asked.
- **E**, Training and Readiness, is a corpus with a named owner in TECOM, a
  summit that has happened, and Gannon already briefing it at the Personnel
  Administration School.
- **F**, time saved, is the currency the pitch already uses.

They converge because a T&R manual is the place where the impact question is
the *daily* question rather than an occasional one: events carry stable codes
and chain by prerequisite, so a reissue propagates mechanically. The corpus
holds zero T&R manuals and `NAMESPACES.md` would take them with no schema
change.

**Caveat, and it is mine.** That description of T&R structure is general
knowledge, not anything measured in this repository. Read one real manual
before it enters a plan.

**What this does not settle.** Whether the programme is candidate A, C, F, or
G at the top. Those are different pitches to different sponsors and the owner
decides. The layering in section 2 holds regardless, which is why it is worth
writing down before the choice is made.

---

## 5. The questions that change the answer

Three, and each is cheap.

**Answered 2026-09-15.** TNR is Training and Readiness, so candidate E is
evidenced. The GPO slice reached back three more minutes and produced two
standing offers. Nothing was followed up.

What is still open, in order of what it changes:

1. **Can GPO's two offers still be taken up?** One reply each. They are the
   only evidence the whole-of-government claim has ever had.
2. **What does CDA stand for, and what is Gannon's part in creating it?** It
   names where his mandate comes from and how long it lasts, and the whole
   programme is currently running on that mandate.
3. **What was said in the missing 87 minutes with GPO?** Four rulings in this
   repository turn on it.
4. **Does a real T&R manual have the structure section 4 assumes?** Read one.
