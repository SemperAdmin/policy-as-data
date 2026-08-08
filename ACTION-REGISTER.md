# Action register

Date: 2026-08-08. Owner: Stephen. Status: current.
Last verified against disk: 2026-08-08, items 0.1, 0.4, 0.7, 0.8.

Consolidates every open item raised this session across `CHARTER.md`,
`POC-PLAN.md`, `REUSE-ASSESSMENT.md`, `VERIFICATION-DESIGN.md`,
`INTEGRATION-SEMPERSCRIBE.md`, `NLDP-CONTRACT.md`, `SEMPERSCRIBE-HANDOFF.md`,
and `resources/`.

**Why this file exists.** Twelve documents were written today and every one
carries open items. Scattered across twelve files they will not get done, and
`CLAUDE.md` section 16 is explicit that a finding living only in a transcript is
lost. This is the single list. When an item closes, close it here and in the
document that owns it.

---

## 0. The three answers still owed

Nothing in Track 1 starts without these. They were asked in `POC-PLAN.md`
section 11 and are still open.

| | Question | My recommendation |
|---|---|---|
| **B1** | May a finding publish a value drawn from an UNVERIFIED rule? | **Refuse for values, downgrade for structure.** Say "DoD tier not verified" rather than "DoD says 12 weeks, unverified." A downgraded number gets screenshotted and forwarded without the banner. |
| **B2** | Which second spine for the generality test? | **Promotion.** It reaches T0/T1/T3, and a cross-tier test touching statute proves more than one stopping at DoD. Not MOS - it names no DoD authority at all. |
| **B3** | Can you obtain DoDI 1327.06 para 3.11.c and 3.11.d text? | If no, pick a different concept **before** writing code. This is the POC's critical path and it is transcription, not software. |

---

## 1. Track 0 - unblock. Do these first, they are cheap and they gate others.

| # | Item | Blocks | Source |
|---|---|---|---|
| ~~0.1~~ | ~~Delete `.git\_to_delete\`~~ **CLOSED 2026-08-08.** Directory listing of `.git` returns 13 entries: `hooks info logs objects refs COMMIT_EDITMSG config description FETCH_HEAD HEAD index ORIG_HEAD packed-refs`. No `_to_delete`, and **no `index.lock`**. The git blocker is gone. | — | verified this pass |
| **0.2** | Commit `.gitattributes`, then `git add --renormalize .`, **then** commit today's twelve new files. In that order. | a reviewable diff | `SESSION_HANDOFF.md` 8 |
| ~~0.3~~ | ~~Add `LICENSE` and `NOTICE`~~ **DRAFTED 2026-08-08, awaiting your confirmation.** MIT, not the NIST public-domain model - see the correction in `ACTION-REGISTER.md` section 9. `NOTICE` separates the MIT grant, the US Government text carrying no copyright, the emblem carve-out, and the privacy statement. **Confirm the copyright line and section 9 before committing.** | reuse gate 1 | `resources/20`, `CHARTER.md` 7 |
| **0.4** | Delete the remaining `_to_delete` folders. **Verified present 2026-08-08:** `docs\search\_to_delete_t` (the 76 MB one, delete first), `docs\_to_delete`, `tools\_to_delete`, `data\exports\_to_delete`. Plus the two on the GunnyBot side. | repository size | verified this pass |
| **0.7** | **PARTIAL 2026-08-08.** My own propagation is fixed: `resources/README.md` and `resources/index.json` now quote the scale from `conformance-matrix.md` and flag the dangling target. **Still open in `conformance-matrix.md` and `NAMESPACES.md`, which are yours to change.** Resolve the dangling citation to `hhq-alignment-plan.md`. `conformance-matrix.md` sources the four-value verdict scale from it, `NAMESPACES.md` names its N3.1 deliverable, and `resources/README.md` repeats the citation - **and the file is not in this repository.** Either bring it in, or cite the scale to a document that is here. I propagated that citation without confirming the target exists, which is my error. | the register's own provenance | verified this pass |
| ~~0.8~~ | ~~Confirm `tools\__pycache__` is gitignored~~ **CLOSED 2026-08-08.** `.gitignore` already carries `__pycache__/`, `*.py[cod]`, `_to_delete/`, `_to_delete*/`, and `canonical/`. No change needed, and the `_to_delete` folders were never in git, so 0.4 is disk space only. | — | verified this pass |
| ~~0.5~~ | ~~Correct `SESSION_HANDOFF.md` 7.3~~ **DONE 2026-08-08.** Item 3 of section 7 now records that Option B exists, names its four serious defects, and states the ruling that the mapping moves here. Nothing else in that file was touched. | — | `NLDP-CONTRACT.md` 0 |
| **0.6** | Rename one **GunnyBot**. The policy factory and SemperScribe's LLM assistant share a name. Update `CHARTER.md` 4 either way. | any external description | `NLDP-CONTRACT.md` 5 |

**0.3 is the one that matters.** It is an afternoon of work, it closes the only
GAP open in the resource register, it unblocks reuse gate 1 in
`REUSE-ASSESSMENT.md`, and until it is done the charter promises dissemination
while the repository ships no terms of use.

---

## 2. Track 1 - the POC. Reconciliation.

Sequential. Nothing here starts before section 0 is answered.

| # | Milestone | Item | Blocked by |
|---|---|---|---|
| **1.0** | M0 | Encode DoDI 1327.06 para 3.11.c and 3.11.d from the authoritative text. Promote to VERIFIED. **No code.** | B3 |
| **1.1** | M1 | `config/rule_concepts.json` and `config/units.json`. One concept, one conversion. Read OpenFisca's parameter model first. | 1.0 |
| **1.2** | M1 | Add `concept` to the six existing rules in the two `rules.json` files. | 1.1 |
| **1.3** | M2 | `tools/reconcile.py`. One concept, two tiers, four verdicts, citations on every line, refusal register. CLI and JSON out, no rendering. | 1.2, B1 |
| **1.4** | M3 | Idempotence proven by hashing. Malformed concept references fail the build. One new stage. | 1.3 |
| **1.5** | M4 | Render into `docs/`, link from the leave spine. Both paragraphs printed in full for any DIVERGE. | 1.4 |
| **1.6** | — | **Stop and show it to someone who did not build it.** | 1.5 |
| **1.7** | M5 | Second spine. The milestone that decides whether the design was shaped around leave. | 1.6, B2 |

**Success turns on S6:** at least one DIVERGE or NOT_HELD finding across two
spines that nobody had on their list beforehand. If that is zero, the concept is
not proven and the honest answer is to say so.

---

## 3. Track 2 - verification. Build it regardless of which POC wins.

This track serves **both** the reconciliation POC and the authoring loop. The
POC's V1 inputs are six rule values that need attestations, and the ingest path
needs the same ledger. It is the shared dependency, so it is not optional.

| # | Item | Priority |
|---|---|---|
| **2.1** | Define the **normalization rule** before anything else. Line endings, whitespace, NFC, text-only hashing. Test it against the CRLF problem in `SESSION_HANDOFF.md` 8. Get this wrong and every attestation invalidates on a round trip. | P0, first |
| **2.2** | `verification/attestations.jsonl` format. Append-only, outside `canonical/`. | P0 |
| **2.3** | `.gitignore` the verifier roster **before** the first attestation is written. | P0 |
| **2.4** | `tools/attest.py` - present one assertion, capture the decision, append. Never writes `canonical/`. | P0 |
| **2.5** | `tools/verify_status.py` plus a build stage deriving status and reporting invalidations. | P0 |
| **2.6** | Seed the ledger from existing inline statuses as `method: "imported"`, honestly marked as carrying no verifier and no source edition. | P0 |
| **2.7** | **V1: attest all six rule values, two-person.** Smallest set, highest consequence, and it is the POC's input. | P0 |
| **2.8** | V2: the source paragraphs behind the 362 cited edges. Compute the distinct count first - the ~300 estimate is not measured. | P1 |
| **2.9** | Per-provision verification badge on the site, showing state, method, and date. Never a name. | P1 |

**2.1 before 2.2.** The normalization rule is the whole design.

---

## 4. Track 3 - SemperScribe and ingest

SemperScribe work is in flight and owned in that repository. **The receiving side
here waits.** Building ingest now while the POC is unfinished is the two-POCs
failure `POC-PLAN.md` section 11 rejects.

| # | Item | Owner | State |
|---|---|---|---|
| **3.1** | NLDP 1.1, Release gate, retire `policy-as-data.ts`, fix the lifecycle enum | SemperScribe | **in flight** |
| **3.2** | Settle the semantics of `basicDirectiveReference`. A change package pointing at its basic order is not a new edition superseding an old one. | either | **UNCONFIRMED, blocks mapping** |
| **3.3** | GunnyBot emits a reference index: identifier, title, date, lifecycle, superseded-by. Replaces `config/revision_index.json` and feeds SemperScribe's picker. | GunnyBot | not started |
| **3.4** | Add `AUTHORED` to the `verification` enum in `schema/policy_document.schema.json` and `usmc-issuance-2.0.xsd`. | here | **deferred until 3.1 lands** |
| **3.5** | `tools/nldp_to_canonical.py` plus `staging/` and an explicit promotion path. | here | **deferred until after the POC** |
| **3.6** | Ingest gate: reject anything without a `release` block, anything not signed or promulgated, anything failing the quarantine gate. | here | with 3.5 |

**3.3 is the item to start early.** It has a long lead time, it lives in a third
repository, and it closes the deliberate coupling already recorded as open in
`SESSION_HANDOFF.md` 9.

---

## 5. Track 4 - register and documentation hygiene

Small, and they keep the record honest.

| # | Item | Source |
|---|---|---|
| **4.1** | Merge `resources/17` to `24` into `conformance-matrix.md` as sections 17 to 24. | `resources/README.md` |
| **4.2** | Add the required EU attribution wherever the charter statement appears externally. Confirm the source page's reuse licence first - it is UNCONFIRMED. | `CHARTER.md` 2 |
| **4.3** | Add the non-official / no-ATO posture to `CHARTER.md` 5, in the same place the whole-of-government claim is made. Both component tools carry that disclaimer. | `NLDP-CONTRACT.md` 5 |
| **4.4** | Reframe the 85 drift findings as a compliance risk register rather than housekeeping. Documentation only. | `resources/17` |
| **4.5** | Record `config/revision_index.json` as a static-snapshot limit against the single-knowledge-source rule. | `resources/17` |
| **4.6** | Confirm OpenFisca's licence and the granularity of its variable `reference`. Both UNCONFIRMED, and the licence alone could be decisive. | `REUSE-ASSESSMENT.md` 7 |
| **4.7** | Discharge `resources/21`, NPS FAST. Paste the landing page, About, and any documentation from a browser, or confirm it is CAC-gated. | `resources/21` |
| **4.8** | Fill the table in `resources/22`. Title, author, publisher, year, ISBN. | `resources/22` |
| **4.9** | Carry the authority statement into exported XML as a processing instruction or header comment. Near-zero cost. | `resources/20` |

---

## 6. Critical path

```
0.1  CLOSED - .git is clean, no index.lock
 |
0.2  gitattributes, renormalize, commit today's work   <-- START HERE
 |
0.3  LICENSE + NOTICE  ......................... unblocks reuse, closes the only GAP
 |
 +--> 2.1 normalization rule --> 2.2..2.6 ledger + tools --> 2.7 V1 six values
 |                                                              |
 +--> B3 --> 1.0 transcribe DoDI 3.11.c/d ---------------------+
                                                                |
                                             B1, B2 --> 1.1 .. 1.5 --> 1.6 SHOW IT
                                                                            |
                                                              1.7 second spine
```

Two long-lead items run in parallel with everything: **1.0 transcription**,
which is human and cannot be compressed, and **3.3 the GunnyBot reference
index**, which lives in another repository.

**This week, in order:** 0.8, 0.2, 0.3, then answer B1 to B3, then start 1.0 and
2.1 together. 0.1 is closed. Run git natively on Windows, never through the
device bridge - `SESSION_HANDOFF.md` 11 records that bridged git leaves an
`index.lock` it cannot unlink, which is how 0.1 arose in the first place.

---

## 7. Not being done, and why

Named so they cannot creep back in.

- **Generalizing `evaluate.py`.** P2. It is a months-long question about whether
  policy logic becomes data, not a POC.
- **Civilian-agency corpus.** P3. Whole-of-government is aspiration, and
  `CHARTER.md` 5 governs.
- **Any database, queue, framework, API, or account system.** P3 by definition.
- **DMN, SHACL, JSONLogic.** Real candidates at a stated trigger, and the trigger
  has not fired. `REUSE-ASSESSMENT.md` 3.
- **LEOS.** Closed at step 1 of its decision tree, because R2 is met.
- **Any LLM or statistical component in the decision path.**
- **Reopening the period ruling in the verified tier, the `[ID2]` promotion, or
  the namespace split.**

---

## 9. Correction: the licence model changed, and I was wrong the first time

`resources/20-nist-code-portal.md` leaned on the NIST 17 U.S.C. 105 public-domain
model. **That is the wrong model for this repository**, and the drafted `LICENSE`
does not use it.

17 U.S.C. 105 removes copyright from works **prepared by an officer or employee
of the United States Government as part of that person's official duties**. The
evidence says this is not that:

- SemperScribe, the sibling repository under the same organisation, ships MIT
  with "Copyright (c) 2026 SemperScribe Contributors".
- Its README states it is "a non-official Proof of Concept maintained on a
  personal basis," not USMC, DON, or DoD software, with no Authority to Operate.
- This repository's own `README.md` says "Not an official reference."

Personal-time work is **not** section 105 material. Copyright subsists, and a
work with copyright and no licence is all-rights-reserved by default, which is
strictly worse for reuse than either alternative. It needs an actual grant.

**MIT, and the reason is consistency as much as permissiveness.** It matches the
sibling repository, so the programme carries one licence rather than two; it
imposes no obligation on a government body adopting the schema; and it is
compatible with everything, which keeps reuse gate 1 open instead of trading one
copyleft trap for another.

**The one fact that would change this:** if any part of this repository was
produced by a federal employee as part of official duties, section 105 applies
to that part regardless of what `LICENSE` says, and the file needs a mixed
statement. Confirm before committing.

**Two fields to confirm:**

1. The copyright line reads "policy-as-data contributors", parallel to
   SemperScribe. Substitute a personal or organisational name if you prefer.
2. `NOTICE` section 4 carves out `branding/` and every military emblem, seal,
   and insignia. That carve-out is deliberate. An MIT grant that appeared to
   licence the Marine Corps emblem would be wrong, and emblem use is governed by
   statute and service regulation rather than by any licence you can write.

---

## 8. Confidence

0.85. Every item traces to a numbered section of a document in the repository,
and the dependency order was derived from stated blockers rather than assumed.

Lower on Track 1 timing, because 1.0 depends on obtaining a source that
`REFERENCES.md` already records as human-in-the-loop, with two documents blocked
for exactly that reason. If B3 comes back no, Track 1 restarts at concept
selection and this register needs rewriting from 1.0 down.
