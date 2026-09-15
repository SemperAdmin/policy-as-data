# Action register

Date: 2026-08-08. Owner: Stephen. Status: current.
Last verified against disk: 2026-08-08, items 0.1, 0.4, 0.7, 0.8.
Updated 2026-09-11: items 1.8 to 1.11 added from `resources/31-oceans-sumo-roe-paper.md`, accepted by the owner. Track 5 added from `SITE-PLAN.md`, adopted; 5.10 decided, fold.
Updated 2026-09-15: Track 6, demo readiness, added from `CONCEPT.md`. Tracks 1 and 5 are not cancelled and are not the demo path; see `CONCEPT.md` section 3.1 for why.

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

| | Question | Decision |
|---|---|---|
| ~~**B1**~~ | May a finding publish a value drawn from an UNVERIFIED rule? | **DECIDED 2026-08-08: WITHHOLD.** A value that is not VERIFIED is not printed and not compared; the tier is reported as present, cited, and withheld, and the verdict becomes NOT_COMPARABLE. Implemented in `tools/reconcile.py`. |
| ~~**B2**~~ | Which second spine for the generality test? | **DECIDED 2026-08-08: PROMOTION.** Owner decision, over a recommendation of fitness. Carry forward: promotion's rules are more often conditions than scalars, so concept selection at M5 needs care, and `DECISION-BRIEF-B1-B3.md` section B2 holds the fitness case if promotion proves thin. |
| **B3** | Can you obtain DoDI 1327.06 para 3.11.c and 3.11.d text? | **STILL OPEN. The only remaining blocker on Track 1.** Everything that does not depend on the text is now built. If the answer is no, the fallback in `DECISION-BRIEF-B1-B3.md` section B3 applies. |

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
| ~~1.1~~ | M1 | ~~`config/rule_concepts.json` and `config/units.json`~~ **BUILT 2026-08-08.** One concept, `PARENTAL_LEAVE_MAX_DURATION`, canonical unit days. Two conversions, weeks and hours, each naming the text that supports the factor. Months and years explicitly **refused** rather than approximated. | done |
| ~~1.2~~ | M1 | ~~Add `concept`~~ **DONE 2026-08-08.** Added to the two rules that share a concept. The other four carry none and `reconcile.py` lists them as unassigned rather than dropping them. **Verified that adding the field leaves every attestation hash unchanged** - the hash covers value, unit, and citation identifier only, which is why the schema could grow without invalidating the ledger. | done |
| ~~1.3~~ | M2 | ~~`tools/reconcile.py`~~ **BUILT 2026-08-08.** Four verdicts, tier derived from the identifier per `NAMESPACES.md`, citations on every line, `--json`, `--out`. All four paths tested: NOT_COMPARABLE on unverified input, DIVERGE at 70 vs 84 days, AGREE at 84, and the units refusal. | done |
| ~~1.4~~ | M3 | ~~Stage 16, malformed concept check~~ **CLOSED 2026-09-11.** Stage wired 2026-08-08. The malformed-concept check is now in `tools/reconcile.py`: a rule whose `concept` is absent from the register exits 1 before anything is written. The earlier code dropped such a rule silently, not in any finding and not in the unassigned list. Claim C9 in `tests/claims.json` holds it. | done |
| **1.5** | M4 | Render into `docs/`, link from the leave spine. Both paragraphs printed in full for any DIVERGE. | 1.4 |
| **1.6** | — | **Stop and show it to someone who did not build it.** | 1.5 |
| **1.7** | M5 | Second spine. The milestone that decides whether the design was shaped around leave. | 1.6, B2 |
| ~~1.8~~ | M3 | **BUILT 2026-09-11.** `tests/claims.json`, 16 claims, 9 positive and 7 negative, run by `tests/run_claims.py` in `validate.yml`. Mutation-checked: disabling B1 withholding in `reconcile.py` fails N1 and N2 and nothing else. Original item: Claims table: `tests/claims.json`, one row per claim with expected verdict, positive and negative, run by a stdlib script in `validate.yml`. Negatives are the point: never AGREE from an unverified input, never convert years, never answer past the encoded rules. Closes the open half of 1.4 too - a malformed concept reference is a claim row. | 1.3 |
| **1.9** | M4 | **ADDED 2026-09-11, from `resources/31`.** Attested absence. Split `reconcile.py` NOT_HELD into NOT_ENCODED (no rule file carries the concept at that tier) and SILENT (a named verifier read the tier and attested it states no value). New attestation kind `absence`, specified in `verification/README.md` first. Before the page renders: a NOT_HELD that means "nobody looked" must not publish as "the authority is silent". | 1.4 |
| **1.10** | M4 | **ADDED 2026-09-11, from `resources/31`.** Binding kind on the authority tier of each concept in `config/rule_concepts.json`: `fixed`, `floor`, `ceiling`, `delegated`. DIVERGE gains direction: below a floor is a finding, variance on a delegated value is conforming and must not read as one. Before the page renders, for the reason `POC-PLAN.md` section 7 gives. | 1.4 |
| **1.11** | - | **ADDED 2026-09-11, from `resources/31`.** Derivation steps in `evaluate.py` output: inputs, operation, basis per step; a unit conversion cites its `config/units.json` entry; a date shift says whether it is a day count or a calendar year. Same commit as the forfeiture-window decision in `verification/findings-forfeiture-window.md`, since both touch the evaluator. | owner decision on the forfeiture finding |

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
| ~~2.1~~ | ~~Normalization rule~~ **BUILT 2026-08-08.** `tools/normalize.py`. CRLF/LF, per-line strip, internal whitespace collapse, NFC, text-only. Smoke check proves variants collapse to one hash and a real change moves it. The first draft had an inverted line-strip that failed the check; caught and fixed. | done |
| ~~2.2~~ | ~~Ledger format~~ **BUILT 2026-08-08.** Spec in `verification/README.md`. Append-only JSONL, outside `canonical/`. | done |
| ~~2.3~~ | ~~Gitignore the roster~~ **DONE 2026-08-08.** `verification/roster.json` added to `.gitignore`, before any attestation exists. | done |
| ~~2.4~~ | ~~`tools/attest.py`~~ **BUILT 2026-08-08.** `--list`, `--next`, `--assertion`, `--seed`. Writes only `verification/`. A rejection writes a correction **request**; the change goes through `tools/corrections.py`. | done |
| ~~2.5~~ | ~~`tools/verify_status.py`~~ **BUILT 2026-08-08.** Six verdicts, `--json`, `--fail-on-invalidated` exits 1 on drift and 0 otherwise, both tested. **Build stage still to be wired into `build.sh`.** | tool done, wiring open |
| **2.6** | Seed the ledger. **Tool built, run it yourself:** `python tools/attest.py --seed`. Imports 5 inline VERIFIED rules with `method: "imported"`, binding the hash now. Optionally `--seed --verifier V-000` if the documented 2026-06-24 corrections pass is genuinely attributable to you - see section 10. | one command |
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

## 5a. Track 5 - the site as one application. Added 2026-09-11.

From `SITE-PLAN.md`, proposed. Measured state: ten header variants across 78
pages, six hand-authored pages outside the build, stale counts on the home
page, the evaluator on no page, reconciliation unlinked, and the one
end-to-end thread walked by no page. Order: 5.1 and 5.4 first, in parallel.

| # | Item | Blocked by | Priority |
|---|---|---|---|
| ~~5.1~~ | **BUILT 2026-09-11.** `config/site_nav.json` and `tools/chrome.py`; five renderers import `head()` and `header()`; the two chrome CSS copies in the renderers are gone (the hand pages' copies go with 5.2). Measured after a build: 72 generated pages, one header, nine links, current page marked `aria-current`. Hand pages still carry four variants until 5.2. Along the way: the build was idempotent within a day only - six clock stamps, now literals; 770 files byte-identical across two builds. `SESSION_HANDOFF.md` section 10. | done |
| ~~5.2~~ | **BUILT 2026-09-15.** `site/` holds five fragments; `tools/render_pages.py` is stage 18 and writes Home, How it works, About, Search, Accessibility. Every count is a placeholder filled from `config/authority_report.json`, `config/reconciliation.json`, and the ledger; an unfillable placeholder fails the stage. The two MOS pages stay hand pages until 5.10. | done |
| ~~5.3~~ | **BUILT 2026-09-15**, reframed for the audience in `SITE-PLAN.md` section 2: the home page leads with the question and the three findings (drift count, current documents citing a superseded instruction, the forfeiture-window error), then walks the thread in six steps, each linked. The scenario step waits on 5.6. | done, 5.6 pending |
| ~~5.4~~ | **FIXED 2026-09-11.** `evaluate.py` now derives status through `verify_status.derive` and withholds every line resting on a rule below VERIFIED, naming the rule; withheld lines still cite. Claims N8 and C10 hold it. Original: **DEFECT.** `tools/evaluate.py` reads inline `status` from `rules.json`, not the ledger. Inline says VERIFIED for all five MARADMIN rules; the ledger derives QUORUM_SHORT for four. Invisible today because the evaluator has no page; a page would publish values the process has not admitted, against the deviation's own condition in `config/verification_policy.json`. Fix: derive status through `verify_status.derive`, apply B1, withhold and name the rule. Claims rows added. | - | P0, blocks 5.6 |
| ~~5.5~~ | **BUILT 2026-09-15.** Section ids on `verification.html` (process, states, examples, walkthrough, cross-tier, findings, queue, validate); each spine tier block carries the document id, each gap `gap-Tn`. | done |
| ~~5.6~~ | **BUILT 2026-09-15.** `docs/scenarios.html` from `config/scenarios.json`, stage 18, `tools/render_scenarios.py` importing `evaluate()` from `evaluate.py` (the CLI now wraps the same function). Three cases; every line links its paragraph; withheld lines name the value and its state in words; refusals listed. The forfeiture line carries the open finding on its face. With today's ledger two of five values are admitted, so the increment and merge lines are withheld - 2.7 changes that, nothing on the page does. | done; 2.7 for the rest |
| ~~5.7~~ | **BUILT 2026-09-15.** "Compared with its authority" panel on every policy page that takes part in a comparison (today 051/23 and DoWI 1327.06), rows in reader words, paragraph links where the page holds the anchor; "Compared across tiers" pointer on the leave spine. Verdicts and withholding come from `config/reconciliation.json`, never re-decided. Also: every state and verdict now has reader-facing words on the site, with the code kept in the data and the legend; maintainer material (the attestation file, the commands) sits behind a disclosure; spine pages say where a citation was read from in words. Closes 1.5. | done |
| **5.8** | Verified excerpts on `policy-DODI-1327.06.html` rendered from `data/dodi-1327.06.uslm.xml` with badges. Closes the thread's step 4 gap. | 5.1 | P1 |
| ~~5.9~~ | **BUILT 2026-09-15.** `site/about.html`: what this is not (official, a decision, complete, automated judgement), where documents come from, terms, accessibility, feedback. The Standards section left How it works with a pointer to Sources; the upstream pipeline diagram (17,514 documents, a training corpus) left with it, since neither number nor claim belongs to this site. | done |
| **5.10** | MOS strand. **DECIDED 2026-09-11: FOLD.** `mos-manual-lineage.html` becomes a generated editions page from `config/mos-family-manifest.json` and `tools/lineage.py`; `mos-manual-intro.html` becomes the "What it says" section of `policy-NAVMC-1200.1L.html`. Both hand pages leave `docs/` as sources once the generated pages exist. | 5.1 | P1 |
| **5.11** | `viewer/` ruling recorded in one line; `README.md` "What is here" stops listing retired code as current. | - | P1 |
| **5.12** | Interactive evaluator. Needs a decision on where logic lives before any code. | 5.6 shown to someone | P2 |
| ~~5.13~~ | **CORRECTED 2026-09-15: see 6.6 and 6.12.** The export multiplication is fixed; the identifier collision is the store's and is item 6.12. Original entry, wrong in attributing it to the export: Exported XML repeats provision elements and collides identifiers. 14 of 56 exports carry more `<provision>` elements than the store holds provisions; `MCO-1400.31D.issuance.xml` carries 3,932 elements for 378 provisions and one identifier 378 times. Across all exports 19,528 distinct identifiers against 20,178 store provisions. The store is right; the export is wrong. Every export still validates against the XSD, so schema validation did not catch it. Investigate `export_issuance.py` before the exports are offered to anyone; the identifier claim ("every provision has a stable identifier") is false for these files as published. | - | P0 |

---

## 5b. Track 6 - demo readiness. Added 2026-09-15.

Scope: what the application needs to be demonstrable to a general officer and
defensible under approval. Derived from `CONCEPT.md` and the six sources in
`CONCEPT-EVIDENCE.md`. **The owner's role is the application.** Outreach,
the duplication question, and the ask are named in section 5c and are not this
track.

### The demo, five beats

A general gives five minutes. Each beat lands a number and needs no
explanation; Ashe in S5 is the evidence for what happens otherwise.

| # | Beat | State |
|---|---|---|
| 1 | Which of your orders rest on something that no longer exists? Four today, each naming the citing order, the dead target, and why it is dead | Data exists, no page. **6.1** |
| 2 | Click one. MCO 6100.14, paragraph 5, reference (a), cites DoDI 1308.3, cancelled March 2022 | Works today |
| 3 | If DoDI 1327.06 reissues tomorrow, what breaks? | Computed, not framed. **6.2** |
| 4 | How do I know this is right? One withheld value | Works today |
| 5 | Is this just 56 documents? | Missing. **6.3**, and it decides the brief |

### The work

| # | Item | Why | Size |
|---|---|---|---|
| ~~6.1~~ | **BUILT 2026-09-15**, commit dd688b1. `docs/currency.html`, three tiers, citing paragraph in words on every row. Original: **Currency page.** What rests on something no longer in force. Rows from `authority_report.cites_superseded` and `superseded_status`; each links the citing paragraph, which `edge_meta.resolution` already carries (e.g. `p-5:ref/a`). Reader words, no codes | Beat 1, the opening | small, data exists |
| ~~6.2~~ | **BUILT 2026-09-15**, commit dd688b1. `docs/impact.html` sorted by dependents, and every policy page frames its citers as what would need review on a reissue. Original: **Impact view.** For any document: what names it, at which paragraph, framed as what breaks if this reissues. `lineage.build_inbound` already computes it and every policy page already shows it as inbound traffic; this is framing plus an index sorted by how many documents name a target | Beat 3, and the question three constituencies actually asked | small |
| ~~6.3~~ | **RUN 2026-09-15.** 169 seconds over `E:\GunnyBot\canonical`, read-only, newest file there still dated July. 17,507 documents read, 7 quarantined and never read. **887 documents in force cite an instruction the corpus holds as cancelled; 5,169 of 21,198 references name a superseded edition; 6,005 name something not held.** Report is `config/scale_report.json`, 3 MB, identifiers and counts only; rendered at `docs/scale.html` and on the home page. Tooling: `extract_authority.py --report-only` applies the publication gate, writes no record, and emits a compact report; `render_scale.py` renders it or an honest not-run page; the home page carries the counts when the report exists. Original: **Scale run.** Edge extraction and the currency and drift measurements across all 17,514 documents at `E:\GunnyBot\canonical`. **Report only: counts and identifiers, no text, no contacts, no rendered pages.** Needs a `--report-only` flag so nothing is written back. `SESSION_HANDOFF.md` non-negotiable 1 keeps that store untouched; non-negotiable 2 keeps the seven Statement C records out, and that gate must hold even for a counts report | Beat 5. Today the honest answer to "how many orders does the Marine Corps have" is 17,500 and we did 56, which is a scale a person can do by hand. This is the number that makes the brief | medium |
| ~~6.4~~ | **BUILT 2026-09-15**, commit dd688b1. Original: **Home opens on the currency finding**, not the reconciliation thread. Most of the page already reads this way; the lead and the order of the three findings change | The demo opens correctly | small |
| **6.5** | **One time measurement.** Time a person answering one of these questions from the source PDFs, then with the tool. N of 1, and say so on its face | The whole pitch is priced in time and the project has never measured a minute. `POC-PLAN.md` S1 to S7 all measure correctness | tiny |
| ~~6.6~~ | **FIXED 2026-09-15, and the diagnosis in 5.13 was backwards.** The store carries the collision, not the export: 585 of 20,178 provisions in 15 documents have a path already used in the same section, a parser defect now item 6.12. The exporter nested children by path and so emitted every child of a repeated path once per repeat; MCO 1400.31D exported 3,932 elements for 378 provisions. It now attaches each child to the nearest preceding parent and emits every provision exactly once: 378. Claim C13 holds element count against the store count per document. The repeated identifiers remain, stated, until 6.12. Original: **Fix the export identifier defect**, item 5.13. `MCO-1400.31D.issuance.xml` carries 3,932 provision elements for 378 provisions and one identifier 378 times | If a technical reviewer opens the XML, that is the moment the room turns. The identifier claim is false for these files as published | unknown until diagnosed |
| ~~6.7~~ | **CHECKED 2026-09-15.** The live site at policy-as-data.app.cloud.gov serves the pre-session home page: programme prose, 54 documents, 351 references. Expected, since nothing has been pushed. Owner deploys via GitHub when this branch lands; check again then. | done, recheck after push |
| ~~6.8~~ | **DECIDED 2026-09-15: the emblem stays.** About already states the site is not official and carries no Authority to Operate; `NOTICE` section 4 carves the mark out of the licence. Nothing further. | done |

Order: 6.1, 6.2, 6.4 together, about a day. 6.3 and 6.5 in parallel, and they
are the pair that makes the demo land. Then 6.6 to 6.8.

### Needed the moment leadership says yes, not before

| # | Item | Why |
|---|---|---|
| **6.9** | A fresh clone that builds. `canonical/` is gitignored, `build.sh` reads it at stage 1, and `CLAUDE.md` constraint 10 claims a fresh clone builds. Both cannot be true | Approval means other people. Today nobody but the owner can run this |
| **6.10** | `CONTRIBUTING.md` and a governance stub. `CHARTER.md` 5 records the collaborative space as not started, and the announcement recruited volunteers for four things the repository forbids | Same |
| **6.12** | **Parser: provision paths are not unique within a section.** 585 of 20,178 provisions across 15 documents (MCO 1610.7B 242, MCO 1400.31D 122, the two 1400.32D changes 50 each, MARADMIN 274/26 40). A repeated marker under a repeated heading gets the same path, so the identifier collides. Fixing it changes machine-tier identifiers, which is the [ID2] promotion question in `SESSION_HANDOFF.md` 7.1 again. Not for the demo; stated on the site as a known limit until fixed | needed before exports are offered to a consumer |
| **6.11** | One Training and Readiness manual encoded, as the second corpus. T&R is confirmed (S2, owner 2026-09-15), TECOM owns it, the grammar takes it unchanged, and the corpus holds none | The impact question is the daily question in a T&R manual rather than an occasional one. **Read one real manual first**; its structure is currently asserted from general knowledge, not measured here |

---

## 5c. Not the application, and not this owner's lane

Recorded so they are not lost. `CONCEPT.md` section 3.6.

| # | Item | Why it matters to the brief |
|---|---|---|
| **6.A** | **The duplication question.** Why does the Directive Control Point not already do this. Open since the first analysis, answered nowhere in the tree | The first question a general asks. The app supplies part of the answer: the current system did not catch four orders resting on a cancelled instruction |
| **6.B** | **The ask.** Nobody has written down what leadership is being asked to approve: people, corpus access, a decision on where it lives, or permission to continue | A brief with no ask gets a nod and no follow-up |
| **6.C** | GPO's two standing offers and Ashe's wish list, all unanswered | The only outside validation the programme has |

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

## 10. Consequence you should see before running the seed

Seeding does **not** leave the five MARADMIN 051/23 rules showing VERIFIED. It
leaves them `QUORUM_SHORT`.

An evaluator-consumed rule value requires two attestations by different
verifiers. The imported seed carries `verifier: null`, because the 2026-06-24
corrections entry records a date and a source but no person, so it counts as
zero independent readings. The five rules read:

    0 of 2 independent attestations plus 1 imported seed carrying no named verifier

That is the honest state, and it is a downgrade from what the data currently
asserts inline. Three ways forward, and I recommend the first:

1. **Accept it and attest.** Five values, two readings each, against a message
   you already have. An afternoon, and it makes the POC's inputs real.
2. **Attribute the seed.** `--seed --verifier V-000` if that corrections pass
   was genuinely your reading. Then the five sit at 1 of 2, needing one
   independent second. Legitimate, and it is a claim about a past act, so it is
   your call and not a default.
3. **Lower the quorum for rules to 1.** I would not. A wrong rule value produces
   a wrong computed answer about a Marine's leave with nobody between the error
   and the reader, and even at quorum 1 a seed with no named verifier still does
   not qualify.

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

**MIT, and there is a DoD authority for it that beats my original reasoning.**
SemperScribe's `LICENSES.md` cites DoD CIO memorandum "Software Development and
Open Source Software," 24 January 2022, Attachment 2 paragraph 3G, which names
Apache-2.0, BSD, GPL, LGPL, and MIT as "acceptable for DoD use," with anything
else needing Component CIO permission. **MIT is on the approved-without-action
list.** That is a better basis than sibling-consistency, and it independently
confirms the EUPL rejection in `resources/23`: EUPL is not on the list and would
need Component CIO sign-off on top of its copyleft problem.

**The one fact that would change this:** if any part of this repository was
produced by a federal employee as part of official duties, section 105 applies
to that part regardless of what `LICENSE` says, and the file needs a mixed
statement. Confirm before committing.

**Two fields to confirm:**

1. The copyright line reads "policy-as-data contributors", parallel to
   SemperScribe. Substitute a personal or organisational name if you prefer.
2. `NOTICE` section 4 **revised 2026-08-08** after checking the asset. You are
   right for this repository: `semper-logo.jpg` is original Semper Admin
   artwork, not an official emblem file. It is now carved out as a **mark**,
   not as government material, and the emblem clause is forward-looking rather
   than descriptive. One observation, not a legal conclusion and I am not a
   lawyer: the illustration renders an Eagle, Globe and Anchor device on the
   cover cap. Original artwork depicting a protected device is a different
   question from using the official asset, and it is worth a look by someone
   qualified.

3. **SemperScribe is the other answer, and it needs a carve-out.**
   `src/lib/dod-seal-data.ts` is 3.8 MB of base64 holding `DOD_SEAL_DETAILED`
   and `NAVY_SEAL_BLUE`, stamped into DOCX letterheads via
   `docx-generator.ts:117` and into PDF via `pdf-seal.ts`. That is official
   symbol use. **It is also correct behaviour** - a letterhead generator under
   SECNAV M-5216.5 should place the seal. The problem is narrower: an MIT file
   at the repository root appears to licence 3.8 MB of DoD and Navy seal data.
   Fix: add a seal carve-out to `LICENSES.md`, which is already the right home,
   since it is an inventory of what is governed by what and seals are governed
   by regulation rather than by a licence. **Do not remove the seals.**

---

## 8. Confidence

0.85. Every item traces to a numbered section of a document in the repository,
and the dependency order was derived from stated blockers rather than assumed.

Lower on Track 1 timing, because 1.0 depends on obtaining a source that
`REFERENCES.md` already records as human-in-the-loop, with two documents blocked
for exactly that reason. If B3 comes back no, Track 1 restarts at concept
selection and this register needs rewriting from 1.0 down.
