# Site plan - one application, then the pages that explain it

Date: 2026-09-11. Owner: Stephen. Status: **adopted 2026-09-11.** The one
owner decision, section 8, was taken the same day: fold. Everything else was
decidable on the engineering side and is decided here.

The tasking: the site is mixed in how it functions. It should be a single
application working fully at small scale, with separate pages explaining the
elements. This plan measures the mix, states the target, and lists the moves.

**Scope ruling.** Restructure, not rebuild. The renderers, the encoding, the
schema, the identifier grammar, and the build are not reopened. "Single
application" means one coherent static site with one thread demonstrated end
to end. It does not mean a server, a framework, or an interactive app.
`CLAUDE.md` sections 2.10 and 6 govern.

---

## 1. The mix, measured

Measured against `docs/` on 2026-09-11, 78 pages.

**Ten header variants.** Distinct header link sets, by page count:

| pages | links in the header |
|---|---|
| 57 | Home, All policies, Authority chains, Sources |
| 6 | Home only |
| 6 | Home, All policies, Authority chains, Connections, Sources |
| 3 | Home, How it works, Version history, Search, Feedback |
| 1 | Home, How it works, All policies, Authority chains, Connections, Verification, Sources, Search, Feedback |
| 5 | five further one-off sets |

Verification, How it works, and Search are unreachable from any of the 57
policy pages. The five spine pages carry Home only. Same defect class as the
four-copy CSS trap in `SESSION_HANDOFF.md` section 10.

**Six pages are hand-authored and outside the build.** `index.html`,
`how-it-works.html`, `accessibility.html`, `search.html`,
`mos-manual-intro.html`, `mos-manual-lineage.html`. No tool writes them.
`README.md` says `docs/` is rendered output, regenerated rather than edited;
these six are edited. The stale counts below are the consequence.

**Nothing on the site runs.** The POC's two tools are CLI-only.

- `tools/evaluate.py`, the cited decision engine, has no page. Two prose
  mentions.
- `tools/reconcile.py` findings are section 5 of 7 on `verification.html`,
  with no anchor, not linked from MARADMIN 051/23's page or the leave spine.

**The home page is a table of contents.** Headline is the programme name,
body is programme prose, then six links to pages that do not reference each
other. It states 54 documents, 351 references, and 7 publications. The build
measures 56 and 362. `VERIFICATION.md` already records a stale claim on the
public site; this is another.

**Three strands with three identities.**

| strand | pages | chrome | in build |
|---|---|---|---|
| library, spines, connections, verification | 70 | G.O.A.T.S. brand block, varying nav | yes |
| MOS Manual intro and lineage | 2 | "Policy version history", nav says Library | no, hand |
| `viewer/`, `prototypes/` | not in `docs/` | own | no, retired |

**Two explainer pages overlap.** `how-it-works.html` closes with a Standards
section; `sources.html` is the standards register.

**The one end-to-end thread exists only in data.** Every link below is in the
repository. No page walks it.

```
MARADMIN 051/23 para 11.d      84 days     VERIFIED, V-001, 2026-08-08
  concept PARENTAL_LEAVE_MAX_DURATION
DoWI 1327.06 para 3.11.c.(3)(a)1   12 weeks  VERIFIED, V-001, artifact hash bound
  reconcile: AGREE at 84 days
  evaluate: remaining days, forfeiture date, increment validity, cited per line
```

A reader assembles that from five pages and a terminal.

---

## 2. Target

One thread on the home page, walked step by step, every step linking into the
page that holds that element. Seven explainer and library pages under one nav.
One chrome, rendered by one function from one list.

```
Home            the thread, walked
Library         all policies, six type indexes, search
Authority       the five spines
Connections     the network
Verification    the process, the queue, the cross-tier report
Scenarios       the evaluator, three fixed inputs, every line cited      NEW
How it works    structure, identifiers, chapter and verse
Sources         the standards register
About           charter, licence, disclaimers, accessibility, feedback   NEW
```

The audience is the one `POC-PLAN.md` section 3 names: the action officer
asking "does the Marine Corps implementation match the authority it claims to
implement." Not the individual Marine. The home page asks that question and
walks the answer.

---

## 3. The thread, step by step

Each step names the existing page and anchor it links to, and the gap where
none exists.

| step | reads | links to | state |
|---|---|---|---|
| 1 | The question: does MARADMIN 051/23 state the parental leave maximum the DoD instruction states? | - | copy |
| 2 | The message, paragraph 11.d, 84 days, as encoded | `policy-MARADMIN-2023-051.html#p11-d` | exists |
| 3 | Where it sits: the ladder above it, T0 statute to T5 message | `authority-leave.html` | exists; **no section anchors** |
| 4 | The DoD paragraph, 3.11.c.(3)(a)1, 12 weeks, as encoded | none | **GAP.** The verified tier `data/dodi-1327.06.uslm.xml` renders nowhere. `policy-DODI-1327.06.html` is the metadata-grade machine record. The paragraph is quoted only on `verification.html`. |
| 5 | Do they agree: AGREE at 84 days, and four concepts NOT_COMPARABLE with the reason for each | `verification.html`, cross-tier section | exists; **no anchor** |
| 6 | Who confirmed it, against what, bound to what hash | `verification.html`, walkthrough | exists |
| 7 | What follows: a worked scenario, remaining days and forfeiture date, cited per line, with what the engine refuses | none | **GAP.** No scenarios page. |
| 8 | What this proves and what it does not: encoded values compared, not the issuances; the DoD tier unverified for four of five concepts until B3 closes | - | copy |

Step 5 is honest and unflattering: one AGREE, four NOT_COMPARABLE. That is
the demonstration. `DECISION-BRIEF-B1-B3.md` section B1 already says not to be
surprised by it.

Step 8 carries the control `POC-PLAN.md` section 7 requires. A home page that
walks to "AGREE at 84 days" is a compliance statement about a live issuance.
It must say it compares encoded values and it must show both paragraphs.

---

## 4. Chrome: one list, one function

**`config/site_nav.json`.** The nav, as data. Label, target, order. One copy.

**`tools/chrome.py`.** One function returning the header, brand block, nav,
breadcrumb, and footer for a page, given its title and its place in the nav.
One CSS constant. The five renderers import it. The four existing copies of
the chrome CSS go away.

**Hand pages become fragments.** `site/` holds the body of each hand-written
page as an HTML fragment: `index`, `how-it-works`, `about`, `search`,
`accessibility`. A new stage, `tools/render_pages.py`, wraps each fragment in
the chrome and writes `docs/`. The six hand pages leave `docs/` as sources and
return as outputs, which is what `README.md` already claims for the whole
directory. Idempotent by construction: fragment in, page out, prior output
removed first.

**Counts from the build.** `render_pages.py` reads the same numbers
`verify_authority.py` and `check_site.py` measure and substitutes them into
the fragments. A count on the home page is never typed.

---

## 5. Scenarios page, and the defect it exposes

**The page.** `config/scenarios.json` holds three fixed inputs. A new stage
runs the evaluator in-process for each and renders the decision lines, each
with its citation and identifier, and the refusal list. No JavaScript
decision path: a browser-side evaluator is a second implementation of the
logic in a second language, and `build.sh` stage 17 already names that trap.
Interactive is P2 and needs a decision on where logic lives first.

**The defect.** `tools/evaluate.py` reads each rule's inline `status` from
`rules.json`. It does not read the ledger. The inline status says VERIFIED for
all five MARADMIN rules; the ledger derives QUORUM_SHORT for four of them.
Today that is invisible because the evaluator has no page. The moment it has
one, its output publishes values the verification process has not admitted,
and `config/verification_policy.json` states the deviation's own condition:
"This deviation does not extend to any evaluator output shown to a Marine.
Before a computed entitlement reaches a member, restore quorum 2."

Two consequences, both required before the scenarios page ships:

1. `evaluate.py` derives status from the ledger through `verify_status.derive`,
   the same call `reconcile.py` makes. Inline `status` becomes what
   `verify_status.py` already calls it, a legacy claim.
2. The evaluator applies B1. A rule that is not VERIFIED is not used; the
   decision line that depends on it is withheld and says which rule, and the
   scenario says so at the top. With today's ledger that withholds most of
   the worksheet. Item 2.7, attest the six values, is an afternoon and
   unblocks it. Until then the page shows what the process has admitted and
   nothing else, which is the correct output.

**The framing.** The page is titled Scenarios, not Calculator. It states that
it evaluates encoded rules against fixed inputs to demonstrate cited
computation, and that it is not an entitlement determination. The page
carries the quorum deviation banner `verification.html` already carries.

---

## 6. Page moves

| page | today | disposition |
|---|---|---|
| `index.html` | hand, programme prose, stale counts | fragment. Body becomes the thread. Counts from build. |
| `how-it-works.html` | hand, standards section at the end | fragment. Standards section moves to Sources. |
| `accessibility.html` | hand | fragment, section of About. Keeps its URL as a redirect stub or stays as a page; either is fine. |
| `search.html` | hand, works served only | fragment. Its `file:` message stays. |
| `sources.html` | generated | unchanged, gains the Standards section from How it works |
| `verification.html` | generated, 7 sections, no anchors | section anchors added. Cross-tier section gains an anchor the home page and the leave spine link to. |
| `authority-*.html` | generated, Home-only nav | chrome from `chrome.py`, tier anchors |
| `policy-*.html` | generated | chrome from `chrome.py`. MARADMIN 051/23 and DoWI 1327.06 pages gain a "Compared across tiers" panel, from `config/reconciliation.json`, linking to the cross-tier anchor. That is item 1.5. |
| `policy-DODI-1327.06.html` | metadata-grade machine record | gains a "Verified excerpts" section rendering the provisions `data/dodi-1327.06.uslm.xml` holds, each with its verification badge. `data/` beats `data/exports/` is constraint 2.9; rendering it where it exists is the same rule applied to the page. Closes the step 4 gap. |
| new `about.html` | - | charter statement with its required attribution, `LICENSE` and `NOTICE` summary, the non-official and no-ATO posture, accessibility, feedback link |
| new `scenarios.html` | - | section 5 |
| `mos-manual-intro.html`, `mos-manual-lineage.html` | hand, own chrome, not built | **owner decision, section 8** |
| `viewer/`, `prototypes/` | retired, still listed in `README.md` "What is here" | out of that list. `prototypes/README.md` already records the ruling; `viewer/` needs the same one line. Removal from tree is a separate, later decision. |

---

## 7. Register items

Track 5, site. Proposed for `ACTION-REGISTER.md`.

| # | item | blocked by | priority |
|---|---|---|---|
| 5.1 | `config/site_nav.json` and `tools/chrome.py`. Five renderers import it. Four CSS copies removed. Zero header variants after a build, proven by the same extraction that measured ten. | - | P0 |
| 5.2 | `site/` fragments and `tools/render_pages.py`. Six hand pages leave `docs/` as sources. Counts substituted from build measurement. Idempotent, hashed. | 5.1 | P0 |
| 5.3 | Home page body: the thread, section 3, eight steps, linked. | 5.2, 5.5, 5.6 for the two gap steps | P0 |
| 5.4 | `evaluate.py` reads status from the ledger and applies B1. Claims rows added: never a decision line from a non-VERIFIED rule. | - | P0, blocks 5.6 |
| 5.5 | Anchors: `verification.html` sections, `authority-*.html` tiers. | 5.1 | P0 |
| 5.6 | `scenarios.html`, `config/scenarios.json`, new stage. | 5.4 | P0 |
| 5.7 | Reconciliation panel on the two policy pages and the leave spine. Item 1.5, unchanged, listed here for order. | 5.1 | P0 |
| 5.8 | Verified excerpts on `policy-DODI-1327.06.html` from `data/`. | 5.1 | P1 |
| 5.9 | `about.html`; Standards section moves from How it works to Sources. | 5.2 | P1 |
| 5.10 | MOS strand disposition. | owner | P1 |
| 5.11 | `viewer/` ruling recorded; `README.md` "What is here" corrected. | - | P1 |
| 5.12 | Interactive evaluator. Needs a decision on where logic lives. | 5.6 shown to someone | P2 |

Order: 5.1, 5.4 in parallel. Then 5.2, 5.5. Then 5.6, 5.7. Then 5.3. Show it
(item 1.6). Then P1.

**Item 2.7 is on the critical path** for the scenarios page to show anything.
It is not a site item and it is not code.

---

## 8. The owner decision: the MOS strand - DECIDED 2026-09-11: FOLD

Two hand pages carry the 25-year edition history of the MOS Manual across four
identifier schemes. Nothing else on the site tells that story, and the "what
came before" section on every policy page is the same idea generalized.

**Fold.** `mos-manual-lineage.html` becomes a generated page from
`config/mos-family-manifest.json` and `tools/lineage.py`, which already
produce the data the hand page states. It sits under Authority or Library as
"Editions". `mos-manual-intro.html` becomes the "What it says" section of
`policy-NAVMC-1200.1L.html`, which is where that text belongs. Cost: one
renderer, medium. Gain: the strand joins the build and the chrome.

**Archive.** Both pages move out of `docs/`, into `prototypes/` beside the
retired editor, with the ruling recorded. Cost: near zero. Loss: the only
edition-history narrative on the site.

Decision: fold, per the owner 2026-09-11. The reasoning that was put to him: the lineage data is already computed every build and
rendered on every policy page one document at a time; a page showing one
family across 32 editions is the natural index over it, and it is a claim
the corpus can actually prove. The intro page is the weaker half and can be
archived alone if the fold is too much.

---

## 9. What this plan does not do

- No server, database, framework, API, or account. Section 10 of
  `POC-PLAN.md` applies.
- No JavaScript in a decision path.
- No change to `canonical/`, `data/`, the schemas, or the identifiers.
- No change to what any policy page claims about a document. Chrome and
  anchors only, plus the two additive panels in 5.7 and 5.8.
- No new dependency.

## 10. Risks

- **Fragments are a new kind of source in the tree.** They are hand-written
  HTML with a substitution step. Keep the substitution to counts and nav; the
  moment a fragment needs logic, it is a renderer and belongs in `tools/`.
- **The thread is one domain.** Home page built around leave will look shaped
  around leave, because it is. M5 is where that gets tested; the home page
  should be written so a second thread slots in beside the first.
- **Step 5 shows one AGREE and four NOT_COMPARABLE.** Anyone shown the site
  before item 2.7 and B3 close sees that. Say it before they see it.
