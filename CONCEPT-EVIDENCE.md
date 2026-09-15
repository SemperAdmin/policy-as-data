# Concept evidence register

Opened 2026-09-15. Owner: Stephen. Status: **gathering. Building is on hold.**

Why this file exists: the owner's ruling of 2026-09-15 is that the concept is
skewed and nothing more is built until it is settled. The evidence that settles
it is arriving as transcripts and references. `CLAUDE.md` section 16 is explicit
that a finding living only in a chat transcript is lost, and the first
transcript was pasted twice, which is the same failure arriving early.

This file logs every source, what it establishes, and what it leaves open. It
is not a plan and it decides nothing. `POC-PLAN.md`, `SITE-PLAN.md`, and
`ACTION-REGISTER.md` stay as they are until the concept is settled; when it is,
whichever of them is wrong gets corrected rather than quietly abandoned.

---

## 1. Source log

Check here before analysing anything new.

| # | Received | Kind | Source | Note |
|---|---|---|---|---|
| S1 | 2026-09-15 | email | Announcement to an AI working group, signed jointly by Maj Gannon and MSgt Shorter | Names the public URLs and the help wanted |
| S2 | 2026-09-15 | transcript | Teams call, ~25 min. Shorter, Gannon, Chiofalo | Shorter on leave. Informal sync |
| S3 | 2026-09-15 | transcript | **Duplicate of S2.** Same text, email omitted | No new content |
| S5 | 2026-09-15 | transcript, **fragment** | Teams call, ~66 min. Shorter, Gannon, Amaya Ashe (civilian) | **First 35 seconds and last 90 seconds only; ~63 minutes missing.** Carries the best user-research datum in the record and an action with a date |
| S4 | 2026-09-15 | transcript, **fragment** | Teams call with the Government Publishing Office. ~90 min. Shorter, Gannon, Lisa LaPlant, Matt L (GPO), Brad Chang, Lauren Wood | **First 20 seconds and last 2 minutes only. The middle 87 minutes are missing and are the highest-value unrecovered material in the project.** Affiliations of Chang and Wood not stated |

---

## 2. What each source establishes

### S1, the announcement

Quoted, because the framing is the finding:

> in attempting to leverage AI in policy making, drafting, and reconciliation

> We are looking for folks to help test, provide feedback, further develop the
> schema, user interface and develop the back end database.

Establishes:

- Two published surfaces: `policy-as-data.app.cloud.gov` and
  `web.git.mil/semper_admin/policy-as-data`. Whether either is current with
  this repository is **unconfirmed**.
- Dr Adam Pease, Naval Postgraduate School, has been briefed. He is a
  stakeholder, not a literature source. `resources/` rows 27 to 31 treat him as
  the latter.
- ARDB Directive Controls programme manager has been briefed.
- TECOM readiness and standards doctrine team has been briefed.
- The help wanted names four things the repository forbids in writing.
  Section 6 below.

### S2, the call

Attributions matter here, so each line is tied to its speaker.

**Chiofalo, on distribution and resourcing:**

> probably marine coders or wherever ... so that people can kind of just take
> what they want, contribute if they want, they can branch it off

> I don't think they want to make this a full-time project yet. So this would
> be just everyone's side thing, but everyone seemed interested still.

No billet, no funding, no tasking. Interest without resourcing. This is the
strongest argument in the record for the current architecture, and it is
nowhere in `CLAUDE.md` section 6, which argues the same conclusion from
document count instead.

**Gannon, on who has been briefed:**

> the ARDB Doctrine Control Point, or Doctrine Directive Control Manager, the
> PM for the Marine Corps, and then Training Education Commands, G1, Colonel
> Wilkerson, and ... I'm at the personal administration school ... for some of
> the TNR briefs in preparation for the TNR summit next week.

**Chiofalo, restating the concept back:**

> imagine just like a giant graph ... your very MCO and it links to every other
> relevant MCO or document ... Once something is updated, the other one knows
> it's updated, like a giant spider graph of things.

> let's say you make a post right now about this MCO being updated. Okay,
> that's updated. What other documents does this affect?

**Shorter, correcting it:**

> the spider graph to make sure things relate, which is an element of it, but
> it's being able to have that information in a somewhere that a large language
> model or a systematic way could be interrogated and used. Because right now
> we do it in like 17,000 different ways. So we also have the methodology that
> we have for like creating directives. How do we actually make policy, how
> does it get used, how is it referenced, how is it looked at, right? And
> that's where a lot of this gets really crazy.

Three things in one answer: the graph is an element, not the point; the point
is interrogable information; and the directive-making methodology is the part
that "gets really crazy."

**Chiofalo, on his own separate project:**

> It's been officially adopted by MIU now. So project lead. I have my
> assistant, Major Nathan Kemp. And other Assistant Lieutenant Colonel Rhodes.

**Gannon, at the end:**

> Showed him some prescribe at the schoolhouse and six AI and Aegis code.

"prescribe" is SemperScribe. "six AI" and "Aegis code" are not decoded.

### S4, the GPO call

**A fragment.** What survives is the opening seconds of introductions and the
closing two minutes. Everything substantive happened in the missing 87 minutes.

Establishes, from what survives:

- **The Government Publishing Office has been engaged for ninety minutes.**
  That is a working session, not a courtesy call.
- Attendees named: Lisa LaPlant and Matt L, both GPO side; Brad Chang and
  Lauren Wood, affiliation not stated on the transcript. LaPlant ran the
  meeting flow and closed it.
- Shorter's assessment: "a great use of resources." Brad Chang and Lisa LaPlant
  both call it a great discussion. No content survives to say why.

**Gannon's closing argument**, the one substantive passage in the fragment:

> the more we break down some of these barriers, especially with data and
> interoperability will decrease a lot of the time that we spend on compliance
> ... I'm not saying compliance is bad, I'm not saying we shouldn't comply with
> Congress and be accountable to the United States people ... our primary
> mission is still train man and equip for fighting battles ... the time we
> spend doing this administrative stuff is the time we're not focused on
> warfighting ... If we don't get after automating this stuff and making this
> far more efficient, we're going to just eat into our enterprise and
> organizational warfighting capabilities.

A readiness argument, priced in time. Candidate F in section 4. The hedge on
compliance is pre-emptive and rehearsed, which suggests this is the standing
pitch rather than an improvisation.

### S5, the call with Amaya Ashe

**A fragment.** The opening 35 seconds of a live demo and the closing 90
seconds. About 63 minutes missing.

**The most useful sentence anyone has said about this project.** Ashe, a
civilian who had already been briefed in person by Gannon:

> I honestly, Sir, I was lost. I was like conceptually I'm not getting it
> because you're talking to me with all this developer language and I'm just
> like, I don't even know what you're talking about. Like I know what you're
> talking about in terms of the concept, but you know, we didn't have like that
> visual even.

She understood the concept and lost the explanation. **The visual is what
closed it.** This is the too-technical problem confirmed by a stakeholder
rather than inferred, and it names the remedy.

Recorded against this: on 2026-09-15 two things were removed from the site on
a judgement about an undefined briefing audience. The sentences connecting the
encoding to model use, contradicted by Shorter in S2. And
`visuals/04-pipeline-and-gates.svg`, contradicted by Ashe here. **The file is
still on disk and is now referenced by nothing.** One pattern, not two calls:
with the concept unsettled, deleting loses the option that reframing keeps.

**Gannon states the user's problem in the user's words:**

> it's gone from. I need to fix all the orders in my command. How do I do that?
> Like AI? OK, how do I get AI to do it to then? Well, I have all these other
> orders across these other services. How do I do that?

This is **remediation, not checking**, and no candidate in section 4 covers it.
Every concept so far tells a reader that something is wrong. This is a person
holding a stack of orders they have to correct. It also escalates from one
command to across services, a joint scope claim made in passing while
`CHARTER.md` section 5 rates whole-of-government as aspiration.

**Gannon's demo narration, and what it claims:**

> We don't have to build anything new, but then we have the computer code that
> another data system needs to see ... this is computer speak to computer speak
> talking to each other, and it's also very low bandwidth. It takes up a lot
> less space. It also decreases our compute time, it also decreases the amount
> of time it takes to parse out stuff and then we can also trace things
> together.

Five claims. **None is measured anywhere in this repository.** Measured now,
against this corpus, so the briefing stops carrying unchecked numbers:

| Claim | Measured |
|---|---|
| Takes up a lot less space | **Wrong against the text.** MCO 1050.3J carries 132,953 characters of provision text; its export XML is 298,372 bytes, about 2.2x. Markup costs space |
| Takes up a lot less space | **Right against the source.** DoWI 1327.06 is a 924,431 byte PDF of 76 pages |
| Low bandwidth, machine to machine | **Right, and this is the number that makes the case.** One provision, the unit of an actual question, is **164 bytes** against a **924,431 byte** PDF |
| Decreases parse time | True and unmeasured. A consumer indexes rather than parses |
| Decreases compute time | True and unmeasured |

The figure that supports the pitch is 164 against 924,431, and it exists in no
file. Say the precise claim, which is about the size of what a machine must
fetch to answer one question, not about total size.

**An action with a date:**

> if you guys [need] anything between now and the 23rd, just let me know. But
> otherwise I'll just try and make sure I have my wish list by then

A named person, a deliverable, and a date. The most actionable item in any
source so far, and it sits next to Chiofalo's "I don't think they want to make
this a full-time project yet." Both are resourcing signals and they point
opposite ways.

Ashe also says "sounds like this was perfect timing." What was timed is not
recoverable from the fragment.

---

## 3. The pain statement, in the owner's words

> right now we do it in like 17,000 different ways

**This sentence is in no project document.** `POC-PLAN.md` section 3 states the
pain as silent divergence after a reissuance, which is a maintainer's problem.
The owner's statement is a user's problem and it is the larger one: there is no
single way to get an answer out of policy.

Everything built so far demonstrates that one way to ask is possible. None of
it is framed that way.

---

## 4. Concept candidates

Seven, each with a constituency. They share a substrate. They are not one
product, and the difference has never been written down.

| # | Concept | Whose words | Built? |
|---|---|---|---|
| A | Impact analysis. What does this update affect | Chiofalo, and the ARDB question | Partly. 362 edges both directions, drift report. No "what changes if X reissues" view |
| B | Reconciliation. Does the order match its authority | `POC-PLAN.md`, and the site as it stands | Yes, and it is now the whole site |
| C | An interrogable substrate, for a model or a systematic method | Shorter, S2 | Built, and never named. The enabling discipline exists; nothing says that is what it is for |
| D | Authoring. How a directive is actually made | Shorter, S2, second half. SemperScribe | Deferred. `ACTION-REGISTER.md` Track 3 |
| E | Training and Readiness. **Inference, see section 5** | Gannon, S2, if TNR is T&R | No. Zero T&R manuals held |
| F | Administrative burden reduction. Time returned to warfighting | Gannon, S4, to GPO | No. **Nothing built measures time.** The site counts documents, references, drift findings and confirmed values. Not one minute |
| G | Remediation. "I need to fix all the orders in my command" | Gannon, S5, quoting the user | No. Every other candidate reports that something is wrong. None helps correct it |

**The layering that is missing.** Layer 0 is the encoding: the paragraph as the
addressable unit, the identifier grammar, cited versus inferred, the
attestation ledger. It is done, it is defensible, and every candidate above
needs it. Layers 1 are products over it. The repository's governing documents
scope candidate B as though it were the whole project, and forbid the
architecture that C and the announcement's asks would need.

**The two framings, and who holds each.** Three sources now show the same
split. Gannon frames outward and Shorter frames inward.

| Source | Gannon | Shorter |
|---|---|---|
| S1, the announcement | "leverage AI in policy making, drafting, and reconciliation" | not separately stated; signed jointly |
| S2, the call | the stakeholder list, T&R | substrate, interrogable, 17,000 ways, the methodology |
| S4, GPO | data and interoperability barriers, compliance time, warfighting capability | "we're definitely doing the right thing" |

This is a natural division: one pitches, one builds. It is not a conflict and
it is not a problem in itself. It becomes one because **neither half is written
down**, so each new audience hears whichever man is in the room, and the two
accounts drift further apart with every briefing.

**C and the "no LLM" rule are not in conflict, and saying so costs nothing.**
"No LLM in the decision path" and "a corpus a model can interrogate" are the
same discipline stated twice. Retrieval is the model's job; adjudication is the
citation's job. Every control already built exists to make a machine-retrieved
answer checkable: the paragraph as the unit, cited never inferred, withheld
until a person reads it. That is precisely what makes the corpus AI-ready, and
no file says so. Writing it down resolves the loudest apparent skew for free.

Recorded against this: on 2026-09-15 the two sentences on `how-it-works.html`
connecting the encoding to model use were removed, on a judgement about a
briefing audience that had not been defined. Reconsider when the concept
settles.

---

## 5. The T&R inference

**Claim, not fact.** "TNR" in S2 is most likely **T&R, Training and
Readiness**. Gannon uses it twice in one sentence, from the Personnel
Administration School, about briefs before a summit.

If it is right, it is the strongest product fit in the record and it is in a
throwaway line:

- A T&R manual is already structured to the event. Every event carries a stable
  code, prerequisites naming other events, and chains across MOS, billet, and
  unit.
- They reissue constantly. "What does this affect" is the T&R question, asked
  daily by the people who own them.
- TECOM owns them, and TECOM readiness and standards is already briefed.
- **The corpus holds zero.** One NAVMC document is held, the MOS Manual.
  `NAMESPACES.md` line 58 already allocates `/us/dod/don/usmc/navmc/{number}`,
  so they would encode with no schema change.

Resolving question: does TNR mean Training and Readiness, and was the summit
about T&R manuals.

---

## 5a. GPO, and the four rulings made without asking them

The tree carries three GPO-related verdicts, every one reached by reading
published documents rather than by asking. `conformance-matrix.md` sections 1,
2, and 3. GPO has now been in the room for ninety minutes and the record of it
is a fragment.

Each row below is an assertion currently load-bearing in this repository, and a
question the missing 87 minutes may already have answered.

| The tree asserts | Turns on |
|---|---|
| United States Legislative Markup "is not intended to model executive branch or judicial branch documents", so this vocabulary is a **sibling** in its own namespace and conformance is refused. `conformance-matrix.md` 1 | Whether that scope is settled policy or present scope. If GPO would extend or bless an executive-branch profile, section 1 changes and so does `NAMESPACES.md` |
| "GPO reserves nothing and operates no registry." Only `usc`, `pl`, and `stat` are defined in prose | Whether a Defense Department branch could be registered, and with whom |
| "A preferred resolver does not currently exist for USLM", quoting the User Guide | Whether one is planned. The whole value of adopting the convention is that a third party can resolve a reference without asking what was meant |
| The GPO model-context preview has no identifier awareness and "cannot resolve our references". Stated revisit trigger: "if GPO adds an identifier-resolution tool" | Whether they are adding one. A ninety-minute meeting is the moment that trigger fires |

**And one finding that runs the other way.** `conformance-matrix.md` section 1
records a defect found in GPO's own published reference grammar: the period is
reserved for the manifestation suffix, so `/us/dod/don/usmc/mco/1050.3j`
resolves as the work `mco/1050` in the format `3j`. This project found it,
fixed it locally with an underscore drawn from the vocabulary the specification
itself uses, and wrote up why. If that was raised in the missing 87 minutes,
the relationship is not a small project asking a large agency for help. It is a
finding delivered to the body that owns the specification, and that changes
what can reasonably be asked for next.

**GPO is also the first civilian-agency contact.** `CHARTER.md` section 5 rates
whole-of-government as aspiration with zero civilian documents encoded. This is
the first engagement outside the Department of Defense.

---

## 6. Where the announcement and the repository disagree

Not editorial. Each row is a written rule.

| S1 offers | The repository states |
|---|---|
| Leverage AI in the work | "Any LLM or statistical component in the decision path" is out of scope. `POC-PLAN.md` 10, `ACTION-REGISTER.md` 7 |
| Help develop the back end database | "Any database, queue, framework, API, or account system. P3 by definition." `ACTION-REGISTER.md` 7 |
| Help develop the user interface | The site is build output. `README.md`: regenerated, never edited |
| Help further develop the schema | "The encoding, the schema, the identifier grammar, the two-tier model, the build. Those are decided." `CLAUDE.md` 0 |
| Branch it off and contribute | No contributing file, no governance, no triage. `CHARTER.md` 5 records it as not started |

**And the contribution ask is not fulfillable today.** `canonical/` is
gitignored, zero of its files are in git, and `build.sh` reads it at stage 1.
Nobody who clones either URL can build the site. `CLAUDE.md` constraint 10 says
a fresh clone builds. Both cannot be true.

---

## 7. Stakeholders, and what is recorded

Four briefings have happened. **None appears anywhere in the tree.** Searching
the repository for ARDB, TECOM, MIU, or a briefing record returns nothing; Dr
Pease appears only as a literature citation.

| Who | What they would ask | Recorded |
|---|---|---|
| Dr Adam Pease, NPS | Ontological rigour: the world model, subsumption, formal semantics | No. `resources/` row 28 answers the technical question and predates the briefing. The register's own stated weakness is that it holds no independent assessment; a briefed specialist is the answer to it |
| ARDB Directive Control PM | Does this replace, feed, or duplicate the system of record | No. **The tree contains no answer to this question at all.** It is the first question a general asks |
| TECOM readiness and standards | Doctrine and standards, not directives | No. The tier map carries a doctrine tier holding zero documents |
| Col Wilkerson, TECOM G1 | Manpower and administration | No. Closest constituency to the encoded leave use case |
| Personnel Administration School | Does this belong in the course | No. A schoolhouse insertion point is a different adoption path from the directives control point |
| **Government Publishing Office** | Publishes the standard this project follows. Owns USLM, GovInfo, and the resolution grammar | **Fragment only.** Ninety minutes, opening and closing preserved, middle lost. Section 5a |
| **Amaya Ashe, civilian** | Office not stated. Thanks them for "contributions to the Corps", which suggests a headquarters or programme role. **Has a wish list due the 23rd** | Fragment only. Her one recorded judgement is that the explanation lost her and the visual saved it |
| MIU | Adjacent, via Chiofalo's separate project | No. Also competition for the same volunteer pool |

---

## 8. Unknowns, each with the question that resolves it

| # | Unknown | Question |
|---|---|---|
| U1 | Whether Gannon and Shorter hold the same concept. S1 leads with AI across three activities; S2 leads with substrate | Ask each other, before the next brief |
| U2 | What Pease, ARDB, and TECOM actually said and asked for | Write down what was said, from memory or notes, while it is recoverable |
| U3 | Whether the database and UI ask is a requirement or recruitment language | A requirement legitimately changes the architecture ruling. A phrase burns a volunteer's weekend |
| U4 | TNR. Section 5 | One line |
| U5 | "six AI" and "Aegis code" | Name them before someone assumes overlap |
| U6 | Whether either published URL is current with this repository | Compare the deployed site against a local build |
| U7 | Who did not join the call. "whenever he decided to come join us would be fantastic" | Who, and does it matter |
| U8 | **What was said in the missing 87 minutes of the GPO call.** The highest-value unknown in this file | Recover it now: the recording, the chat, notes, or both men writing down what they remember before it fades |
| U9 | Whether the period defect in the published grammar was raised with GPO | It changes what can be asked for next |
| U10 | Affiliations of Brad Chang and Lauren Wood | One line each |
| U12 | **Amaya Ashe's office, and what the wish list on the 23rd feeds.** Requirements, funding, tasking, or a brief | One line. It is the nearest thing to a resourcing decision in the record |
| U13 | Which visual closed it for her: a site diagram, the rendered page, or a live demo | Decides what to build more of |
| U14 | What "perfect timing" referred to | One line |
| U15 | What the sentence "it's gone from ... " was going to end with. The demo answered it and the fragment does not | Ask Gannon what he showed |
| U11 | Whether candidate F is measurable. How long a person takes today to answer one of these questions from the source PDFs | Time one. It is the only proof F admits, and nothing in the tree measures time |

---

## 9. Not decided

Nothing in this file decides anything. The open question is which candidate in
section 4 the programme is, and whether the others are products over the same
substrate or different programmes. Until that is answered:

- No code.
- `POC-PLAN.md` and `SITE-PLAN.md` stand as written, including the parts this
  file suggests are too narrow. They are not edited to match a concept that has
  not been chosen.
- New sources are logged in section 1 first.
