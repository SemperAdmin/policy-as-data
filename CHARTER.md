# Charter

Date: 2026-08-08. Owner: Stephen. Status: adopted text, with the derivation
recorded and the scope bounded.

Companion to `README.md`, which states what the repository is, and to
`resources/18-digital-ready-policymaking.md`, which is where this statement's
source was reviewed.

---

## 1. The statement as supplied

Reproduced verbatim, dated, and unedited, so later revisions have a baseline to
diff against.

> Semper Admin for short as part of the GOATS project, Generalized Orders
> Administrative Tool(s) objective is to serve as a dynamic knowledge hub for
> all stakeholders involved in the policymaking process, helping to make
> policies and legal acts more digital-ready to ensure their smooth
> implementation. We aim to build and disseminate knowledge, provide tools and
> guidance, support trusted exchange of information and create a collaborative
> space for all aspects of digital-ready policymaking. For the whole of US
> Government starting with the Marine Corps and Department of Navy as the US
> Government use case and proof of concept.

## 2. Derivation, and why it is recorded here

The mission language is a near-verbatim adaptation of the European Commission's
Digital-Ready Policymaking collection on the Interoperable Europe Portal,
retrieved 2026-08-08.

| GOATS statement | Interoperable Europe Portal, DRPM collection |
|---|---|
| "serve as a dynamic knowledge hub for all stakeholders involved in the policymaking process, helping to make policies and legal acts more digital-ready to ensure their smooth implementation" | "serve as a dynamic knowledge hub for all stakeholders involved in the policymaking process, helping to make policies and legal acts more digital-ready to ensure their smooth implementation" |
| "build and disseminate knowledge, provide tools and guidance, support trusted exchange of information and create a collaborative space for all aspects of digital-ready policymaking" | "build and disseminate knowledge, provide tools and guidance, support trusted exchange of information and create a collaborative space for all aspects of digital-ready policymaking" |

Two clauses are word for word. The adaptation is the third sentence, which
substitutes the US Government for the European public sector.

This is recorded rather than hidden for three reasons.

1. **The discipline demands it.** This repository does not conflate cited and
   inferred anywhere else. A mission statement carrying an uncited source would
   be the one artifact in the tree held to a lower standard than its data.
2. **The lineage is an asset.** Aligning with a named, funded, legally-grounded
   European programme is a stronger position than asserting an original mission.
   Regulation (EU) 2024/903 is the only binding public-sector interoperability
   law in force anywhere. Standing on it deliberately reads as competence.
   Standing on it silently reads as something else the first time a reviewer
   runs the sentence through a search engine.
3. **Reuse status is unsettled.** European Commission portal content is
   generally reusable under Decision 2011/833/EU with attribution, and the
   specific licence applying to this collection page is **UNCONFIRMED** as of
   2026-08-08. Attribution discharges the obligation under either reading. Any
   external publication of this statement should confirm the page licence first.

**Required attribution wherever the statement appears externally:**

> Mission language adapted from the Digital-Ready Policymaking collection,
> Interoperable Europe Portal, European Commission.
> <https://interoperable-europe.ec.europa.eu/collection/digital-ready-policymaking>

## 3. The statement, corrected

The supplied text has two defects that block use as written. Both are mechanical.

**Defect 1: the name has no referent.** "Semper Admin for short" states an
abbreviation without naming what it abbreviates. A reader cannot resolve it.

**Defect 2: the acronym expansion is unstable.** "Generalized Orders
Administrative Tool(s)" yields GOAT or GOATS depending on how the parenthetical
is read. An acronym with a variable letter count is not an identifier. Fix the
expansion to the plural and drop the parenthesis.

Corrected edition, adopted:

> **GOATS**, the Generalized Orders Administrative Tools programme, exists to
> serve as a dynamic knowledge hub for all stakeholders involved in the
> policymaking process, helping to make policies and legal acts more
> digital-ready to ensure their smooth implementation. GOATS builds and
> disseminates knowledge, provides tools and guidance, supports trusted exchange
> of information, and creates a collaborative space for all aspects of
> digital-ready policymaking.
>
> The programme is scoped to the United States Government. The Marine Corps and
> the Department of the Navy are the first use case and the proof of concept,
> selected because their issuance hierarchy is deep enough to test the model and
> narrow enough to encode in full.
>
> **Semper Admin** is the programme's public identity: the portal and the
> product family a user sees. GOATS is the programme. Semper Admin is the name
> on the door.

## 4. Name register

Every name in current use, what it is, and what it is not. This section exists
because the tree already carries five names across three repositories and a
sixth was introduced by this statement.

| Name | What it is | Repository | Relationship |
|---|---|---|---|
| **GOATS** | the programme. Generalized Orders Administrative Tools. | none of its own | the umbrella. New as of this charter. |
| **Semper Admin** | the public identity and product family | `SemperAdminPortal` | the front door. Owns the visual system in `branding/SEMPER-STYLE-GUIDE.md`, mirrored here read-only at v1.2. |
| **policy-as-data** | the standard, the schema, the renderers, the demonstration corpus, and the site | this repository | the encoding. The product is the encoding itself. |
| **GunnyBot** | the factory. Acquisition, extraction, the corpus at ~17,500 documents. | `E:\GunnyBot` | upstream. The boundary is held in `HANDOFF.md`. |
| **SemperScribe** | the authoring side. Naval Letter Data Package, MCO 5215.1K structure. | separate | downstream of drafting, upstream of encoding. Integration is an open decision in `SESSION_HANDOFF.md` section 3. |

Two rulings follow from the table.

**GOATS does not get a repository.** A programme name with a repository behind
it becomes a fourth codebase to maintain and a fourth place for a document to
live. GOATS is a name and a charter. It stays that way until something exists
that belongs to no other repository.

**Semper Admin does not absorb policy-as-data.** `README.md` states "This is a
standalone project. It carries its own corpus, its own tooling, and its own
build. Nothing else needs to be present." That property is the reason the
extraction from GunnyBot was worth doing, and adopting a programme identity does
not spend it. A clone still builds with `./build.sh` and no Semper Admin
dependency.

## 5. Scope, and what is evidence versus what is aspiration

"For the whole of US Government" is the sentence a reviewer will test first.
State the ladder honestly and the claim survives contact.

| Rung | Claim | Standing |
|---|---|---|
| Marine Corps issuances | the model encodes MCO, MARADMIN, MCBUL, NAVMC | **evidenced.** 56 documents, 362 cited references, 85 drift findings, all measured. |
| Department of the Navy | SECNAVINST and ASN (M&RA) memoranda encode in the same grammar | **evidenced, thinly.** Three SECNAVINST and two ASN memoranda in the corpus. |
| Department of Defense | DoDI, DoDD, and DTM encode in the same grammar | **evidenced at metadata grade.** Identity, dates, supersession, and reference lists transcribed. Section text not ingested, and every record says so on its face. |
| Statute | USC encodes | **evidenced, and it is the anchor.** 10 U.S.C. 701 and 1052 are encoded from the authoritative source. |
| Whole of US Government | the grammar generalizes beyond DoD | **aspiration.** Zero civilian-agency documents are encoded. Nothing outside `/us/dod/` and `/us/usc/` has been tested against the identifier register. |

The honest form of the whole-of-government claim:

> The identifier grammar in `NAMESPACES.md` is jurisdiction-first and
> department-agnostic by construction. `/us/<department>/<service>/<doctype>/`
> admits a civilian agency without a schema change. That is a design property,
> demonstrated only inside the Department of Defense to date.

**Do not state a government-wide capability as achieved.** The corpus is 56
documents. A reviewer who checks will find that number, and every claim in the
tree that survives checking is worth more than the one that does not.

## 6. What the mission changes, and what it does not

The DRPM language is drafting-side. It speaks of making "policies and legal acts
more digital-ready," which is an act performed on a document before it is
issued. This repository's object is the opposite end of the lifecycle: faithful
encoding of issuances already in force. Adopting the mission does not move that
boundary, and the boundary is what keeps the work honest.

| Mission clause | Which component owns it | State |
|---|---|---|
| dynamic knowledge hub | Semper Admin portal, and `docs/` as its evidence base | partial. The site publishes 56 documents, five authority chains, and a connection network. |
| make policies more digital-ready | SemperScribe. Structure at authoring time removes extraction entirely. | open. This is the strongest reason the DRPM source stays in the register. |
| build and disseminate knowledge | `docs/`, `conformance-matrix.md`, `resources/` | done, for this corpus. |
| provide tools and guidance | `tools/`, `schema/`, `NAMESPACES.md` | done, and unlicensed. See the gap below. |
| support trusted exchange of information | the two-tier VERIFIED / UNVERIFIED model, and cited-versus-inferred provenance | done, and it is the differentiator. Nothing in the DRPM source requires this. |
| collaborative space | none | not started. No contribution path, no issue triage, no governance document exists. |

Two rows are unfunded promises today. Say so in any briefing rather than letting
the mission statement imply otherwise.

## 7. The gap this charter inherits

A mission that promises "provide tools and guidance" and "support trusted
exchange of information" is a distribution commitment, and this repository has
no distribution terms. There is no `LICENSE`, no `NOTICE`, no `CITATION.cff`,
and no `code.json` anywhere in the tree, verified by directory walk on
2026-08-08, while `docs/` is served by GitHub Pages and `deploy_cloudgov.bat`
targets cloud.gov.

Adopting this charter raises that from an oversight to a contradiction: you
cannot promise dissemination and ship no terms of use. The fix and the working
federal precedent are in `resources/20-nist-code-portal.md`. **State: OPEN, and
this charter is now blocked on it.**

## 8. What this charter does not claim

**Not an endorsement.** Nothing here implies the European Commission,
Interoperable Europe, or any Member State endorses GOATS or Semper Admin. The
relationship is one-way adaptation of published mission language.

**Not a legal obligation.** Regulation (EU) 2024/903 binds Union institutions
and Member State public sector bodies. It does not reach a US Department of
Defense component, and no DoD issuance incorporates it by reference. Alignment
here is voluntary and chosen.

**Not an official position.** This charter states a project's intent. It is not
a Marine Corps, Department of the Navy, or Department of Defense position, and
carries no authority over anyone.

**Not a replacement for the issuing authority.** Unchanged from `README.md`:
the issuing authority's copy governs.

## 9. Confidence

0.8 on the derivation and the name register: the EU source text was retrieved
and quoted verbatim on 2026-08-08, and every repository name in section 4 is
cited from a file in the tree. 0.6 on the licence position, because the specific
reuse terms of the source page are UNCONFIRMED and only the general Commission
reuse decision is known. GOATS itself appears nowhere in this repository before
this file, so section 4 records a decision rather than an observation.
