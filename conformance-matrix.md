# Conformance Matrix

Date: 2026-08-03. Owner: Stephen. Scope: the 14 references in Web_resources.csv,
plus the governing authorities those references lead to.

Verdicts follow the four-value scale set in hhq-alignment-plan.md N0.2:

- CONFORMANT - the stack meets the requirement as written.
- ADAPTED - same intent, modern or different form, rationale stated.
- NOT APPLICABLE - out of scope, rationale stated.
- GAP - a real shortfall. Every GAP row names its fix and its state.

Research method: primary sources only. Specification text is quoted verbatim
where a verdict turns on it. Anything not confirmed against an authoritative
source is marked UNCONFIRMED rather than assumed.

---

## Summary

| # | Reference | Verdict | One line |
|---|---|---|---|
| 1 | USLM schema and identifier model | ADAPTED, one GAP FIXED | Identifiers used a reserved character. Fixed. |
| 2 | GovInfo Developer Hub | CONFORMANT | Retrieval pattern matched; no obligation. |
| 3 | GPO MCP preview | NOT APPLICABLE | Two discovery tools over GovInfo packages. No USLM awareness. |
| 4 | DSPO Digital Standards Strategy, Jan 2026 | ADAPTED | Non-prescriptive. The stack already sits at its target tier. |
| 5 | ASSIST and DoDI/DoDM 4120.24 | NOT APPLICABLE, with a caveat | Standards, not issuances. No public API exists. |
| 6 | NIEM and NIEMOpen | GAP, OPEN | DoDI 8320.07 requires a documented assessment. Written, see section 6. |
| 7 | DCAT-US and data.gov | GAP FIXED | OMB M-25-05 requires DCAT-US 3.0. Emitter built. |
| 8 | CKAN | NOT APPLICABLE | Hosting platform, not an encoding standard. |
| 9 | S1000D | ADAPTED | Same architecture, independently arrived at. Two ideas worth adopting. |
| 10 | Open XML SDK, DOCX, LOC format registry | NOT APPLICABLE to the read path | Authoring side. Governs SemperScribe. |
| 11 | SGML / ISO 8879 | NOT APPLICABLE | Doctrinal ancestor. Live descendants are what bind. |
| 12 | Protégé and WebProtégé | ADAPTED | Live tooling. Our graph is JSON-LD, not OWL. |
| 13 | IHMC KAoS | NOT APPLICABLE | Dormant since 2013. Mine the model, not the code. |
| 14 | SFIS | NOT APPLICABLE | Financial data structure. Governs nothing here. |
| 15 | NPS Monterey Phoenix | NOT APPLICABLE | Behavior modeling. Governs nothing here. |

Two GAPs closed this session. One GAP open and now documented. One stale claim
on the public site corrected.

---

## 1. USLM - United States Legislative Markup

Sources: `github.com/usgpo/uslm`, `govinfo.gov/schemas/xml/uslm/uslm-2.1.0.xsd`,
USLM User Guide, USLM 2.1 Review Guide.

### What is actually true

- Current released version is **2.1.0**, dated 2024-08-22 in the schema comment.
  Since 2.1.0 the schema is split into a driver and a 378 KB components file.
- **The U.S. Code itself is still published in USLM 1.0.15**, not 2.1.0.
  Release point 119-102 carries `xmlns="http://xml.house.gov/schemas/uslm/1.0"`.
  Two live namespaces, and the working group's stated policy is that
  "USLM XML files may validate against any of the adopted schema versions."
- **`@identifier` has no pattern.** It is typed `LongStringSimpleType`:
  a string of not more than 1024 characters. No `xsd:pattern`, no enumeration,
  and zero Schematron rules in the components schema. Schema validity therefore
  proves almost nothing about identifier correctness.
- **USLM excludes executive branch documents by design.** Schema Objective
  annotation: "This schema is not intended to model executive branch or judicial
  branch documents, except as this content is included in the documents that are
  within scope." User Guide section 1.3: "While it is not a general model for
  documents outside this specific set."
- **GPO reserves nothing and operates no registry.** Only `usc`, `pl`, and
  `stat` are defined in prose; `act` appears heavily in production and is
  documented nowhere.
- **There is no resolver.** User Guide section 12.6: "A preferred resolver does
  not currently exist for USLM."

### GAP FOUND AND FIXED - the period is a reserved character

USLM User Guide section 12.2 defines the reference grammar as
`[item][work][lang][portion][temporal][manifestation]`, and:

> manifestation (". " prefix) - identifies the format as a simple file
> extension (".xml" for the XML file, ".htm" for HTML, and ".pdf" for the PDF).

Our identifiers rendered directive numbers straight into the path:

    /us/dod/don/usmc/mco/1050.3j

A resolver following the published grammar reads that as the work
`/us/dod/don/usmc/mco/1050` in the manifestation `3j`. The identifier is
ambiguous against the only grammar GPO has published. Since the entire reason
to adopt the convention is that a third party can resolve our references
without asking us what we meant, this is a real defect, not a cosmetic one.

FIX APPLIED: `tools/normalize_identifiers.py`. The period becomes an underscore
inside every path segment. The underscore is in the RFC 3986 section 2.3
unreserved set, which the USLM 2.1 Review Guide already requires for version
strings, so the substitute comes from the vocabulary the specification uses.

    /us/dod/don/usmc/mco/1050.3j   ->  /us/dod/don/usmc/mco/1050_3j
    /us/dod/dodi/1327.06           ->  /us/dod/dodi/1327_06
    /us/usc/t10/s701               unchanged

Document ids, native numbers, and displayed text keep their periods, because
that is how a Marine writes them. Only the machine identifier changes.
18,417 identifiers across 15 records in the spine set. This is an identity
change under [ID2] and sits in staging pending owner adjudication.

### VERDICT: ADAPTED

Our XML export is not USLM and does not claim to be. It emits root `<issuance>`
in namespace `https://policy.usmc.mil/ns/uslm/1.0` - a USLM-derived vocabulary
in its own namespace. That is the right call and it is now the better-supported
one, because USLM 2.1 closed the door 2.0 left open:

> USLM 2.1 changes the definitions for these elements so that elements in
> namespaces other than USLM are not allowed. ... Aside from the specific
> exceptions, this is now the only way to include content in another namespace
> in a USLM document.

Embedding service-issuance structure inside a real USLM document would now fail
2.1 validation. A sibling namespace is the conformant path, not a compromise.

The site's wording already states this correctly - "follows United States
Legislative Markup conventions, extended to service issuances" and "Exports
validate against a published XML schema." Both are accurate. Do not upgrade
that language to "USLM conformant."

### Adopt from USLM, not yet done

1. **Versioning attributes.** `@startPeriod` and `@endPeriod` with multiple
   versions of an element coexisting in one document is a near-exact fit for
   orders amended by change transmittals. Our `dates` block carries the data
   already.
2. **Status vocabulary, with one honest mismatch.** USLM `StatusEnum` offers
   `inEffect`, `cancelled`, `repealed`, `expired`, `terminated`, `omitted`,
   `renumbered`, `redesignated`, `transferred`, `reserved`. **There is no
   `superseded` value.** Our `superseded` maps to no USLM term. Record it as
   ADAPTED with a `@role` refinement rather than forcing a wrong term.
3. **Avoid `@temporalId`.** Proposed 2.1.1 removes it: "Remove the unused
   temporalId, occurrence, and actionDate attributes."
4. **Hierarchy element names.** `<section>` / `<subsection>` / `<paragraph>` /
   `<subparagraph>` / `<clause>` / `<subclause>` / `<item>` map onto our
   provision depths and cost nothing to adopt in the export.

### Stale artifact found, and rebuilt

`tools/export_uslm.py` was two schema versions behind the store, and it had
shipped three defects into published files:

1. It read canonical 0.2.1 while the store is 0.5.0, so everything the
   provision parser and the authority extractor produce was invisible to it.
2. It wrote `status="UNVERIFIED"` on the root element while the companion
   authority graph for the same document wrote `"status": "active"`. One
   attribute was carrying two orthogonal facts, so two published artifacts
   contradicted each other about the same document.
3. It emitted each section as one flat paragraph holding a raw text dump. The
   provision tree never reached the XML at all.

REPLACED by `tools/export_issuance.py` writing usmc-issuance 2.0, with
`schema/usmc-issuance-2.0.xsd` published alongside it. See section 16.

---

## 2. GovInfo Developer Hub - CONFORMANT

An access channel, not a requirement. We used it exactly as intended: statute
text pulled from `uscode.house.gov` granule URLs, recorded in
`provenance.source_path` on every statute record. No obligation attaches.

Worth knowing: GovInfo hosts every adopted USLM schema version at
`govinfo.gov/schemas/xml/uslm/uslm-{version}.xsd`, so offline validation
against a pinned version is available.

---

## 3. GPO MCP preview - NOT APPLICABLE

Stated status, verbatim: "This is a public preview ... GPO has built a minimum
viable product to gather feedback." It exposes exactly two tools,
`searchGovInfo` and `describePackageOrGranule`, over GovInfo packages.

It has **no USLM awareness**: no identifier resolution, no `/us/...` lookup, no
section-level extraction, no validation. It cannot resolve our references and
was never going to. Revisit if GPO adds an identifier-resolution tool.

---

## 4. DSPO Digital Standards Strategy, January 2026 - ADAPTED

Source: `dsp.dla.mil`, "Department of War (DOW) Digital Standards Strategy,"
signed Thomas W. Simms, Defense Standardization Executive.

### The finding that governs how you cite it

It is **not directive**. Section II, verbatim:

> The guidance in the strategy is not intended to be prescriptive, such that
> DOW programs will have additional requirements for the use of digital
> standards.

No compliance date, no milestone schedule, no tasking table. Implementation is
deferred to a roadmap that does not yet exist and that I could not find
published as of 2026-08-03. Cite it as direction of travel, never as a mandate.

### Where the stack sits against its own model

The strategy adopts a three-tier model from ISO/IEC SMART and defines the tiers:

> Machine-readable - Structured content that can be recognized and validated
> by software.
> Machine-interpretable - Semantic content that can be acted upon by software.

and expands the upper tier:

> Semantic meaning can also be added to data exchange formats to facilitate
> machine interpretation. This is achieved by adding metadata and attributes,
> and using schemas (e.g., XSD), controlled vocabularies, and ontologies.

Mapping our artifacts:

| Tier | Strategy definition | Our artifact | State |
|---|---|---|---|
| Human-readable | paper, PDF | the rendered library, Section 508 targeted | built |
| Machine-readable | XML, CSV, JSON with defined structure | canonical JSON against a versioned JSON Schema, plus the XML export | built |
| Machine-interpretable | schemas, controlled vocabularies, ontologies | the tier vocabulary, the cited/inferred edge basis, the authority graph as JSON-LD | built, ontology not formalized |

LOE 2 is the closest thing to a directed action and it names the format:

> The DOW has chosen XML because it is a ubiquitous machine-readable format.

Our canonical store is JSON with an XML export. Both are named as
machine-readable in the strategy's own definition, so this is ADAPTED, not a
gap. Retaining human-readable output is explicitly required and we do it:
"Human-readable documents often can be autogenerated from machine-readable and
machine-interpretable formats."

Guiding Principle III - "Digital standards guidance will be tool-agnostic to
allow for wider use and applicability" - is satisfied: every artifact is a
plain file in an open format, and the pipeline has no proprietary dependency.

### The gap this project actually fills

DoWI 5025.01, "DoW Issuances Program," was reissued **20 January 2026, eight
days after the Digital Standards Strategy**, and contains no machine-readability
provision at all. Production format is Microsoft Word plus PDF. SECNAV M-5215.1
is stricter still and entirely typographic: "Courier New 12 font is the only
authorized font," five-page limit for SECNAV instructions, SSIC numbering.

So DoD requires structured XML for **technical manuals**, DSPO has committed to
converting **standards** to XML, and **policy issuances** - the layer that
directs all of it - are governed by Word templates and a mandated font. That
inconsistency is the argument for this project, stated in the Department's own
documents. It is the strongest line available for an HHQ pitch.

---

## 5. ASSIST and the Defense Standardization Program - NOT APPLICABLE, with a caveat

DoDI 4120.24 and DoDM 4120.24 govern **specifications and standards**, not
policy issuances. Our corpus contains neither. The Glossary is unambiguous
about what ASSIST covers: "the DoD's official source for standardization
documents."

CAVEAT worth recording: **ASSIST has no public API and no bulk data interface.**
Probes for `/api`, `/online/api`, `/webservices/`, and `robots.txt` all 404.
Search is an ASP.NET WebForms postback - scriptable, but undocumented,
unversioned, and unsupported. There is no published machine-readable index of
DoD standards. The Digital Standards Strategy concedes this and makes fixing it
LOE 2 and LOE 4, with no date and no funding named.

Relevant if the corpus ever ingests MIL-STDs. It does not today.

Adjacent standards confirmed live in ASSIST on 2026-08-03, for the record:
MIL-STD-40051E Change 1 (30 Jul 2025, active) is the Army technical-manual XML
standard, **and USMC is a Navy custodian on it**. MIL-STD-3031B(1) (31 Jul 2025,
active) carries the Army S1000D business rules against Issue 4.2.
MIL-STD-2361C is **cancelled** - do not cite it.

---

## 6. NIEM and NIEMOpen - GAP, OPEN

Sources: NIEM NDR v6.0 (OASIS Standard, 28 Nov 2025), DoDI 8320.07, DoD CIO
memorandum of 18 March 2013.

### The obligation is real and we had not discharged it

DoDI 8320.07, "Implementing the Sharing of Data, Information, and Information
Technology (IT) Services in the Department of Defense," section 3.b:

> the use of National Information Exchange Model (NIEM)-based exchanges must be
> considered for all new Extensible Markup Language (XML) information exchanges

and its Procedures section 2.a(1)(a):

> Consider the NIEM standards-based approach first when developing XML
> information exchanges ... organizations will perform a business case
> assessment to compare the suitability of NIEM to that of any potential
> alternative approaches ... When NIEM is not the most efficient or effective
> means to address an information sharing requirement, organizations will
> document the technical, fiscal, and operational reasons why.

We publish an XML information exchange. The assessment is a required artifact
and it did not exist. That is a genuine GAP, and it is the single most
consequential finding in this matrix for anything headed up the chain.

### The assessment, discharged

**Requirement.** Publish Marine Corps policy issuances as structured data with
paragraph-level addressing, cited authority edges, and supersession state.

**Does NIEM fulfil it?** Partially, and not off the shelf.

- NIEM 6.0 carries 17 domains. **None covers policy, directives, or document
  management.** Keyword searches of the 6.0 model return zero types matching
  "Directive" and zero matching "Memorandum".
- Military Operations (`mo`) is scoped to Joint Capability Areas - force
  support, battlespace awareness, logistics, command and control. Not issuances.
- The building blocks do exist in NIEM Core. **`nc:DocumentType` carries 65
  child properties**, and a meaningful set are directly on point:
  `nc:DocumentEffectiveDate`, `nc:DocumentExpirationDate`,
  `nc:DocumentIssueDate`, `nc:DocumentApprovedIndicator`, `nc:DocumentStatus`,
  `nc:DocumentIdentification`, `nc:DocumentDispositionAuthorityName`,
  `nc:DocumentSupplementalMarkingText`, `nc:DocumentAuthor`.
- The `cui` namespace carries the controlled-marking vocabulary, which maps
  onto our distribution-statement and quarantine handling.
- **What NIEM has no vocabulary for is the thing this project exists to do**:
  a provision-depth hierarchy inside a document, and a citation that resolves
  to a paragraph rather than to a document. NIEM models exchanges between
  systems, not the internal structure of a legal text. USLM and S1000D both do
  model that; NIEM does not.

**Technical reason for the current approach.** Provision-level addressing is
the requirement. NIEM would model each issuance as an `nc:Document` with
metadata and an attachment, which loses exactly the structure we built. USLM
conventions carry it natively.

**Fiscal reason.** A conformant NIEM exchange needs an extension namespace, a
message specification, CTAS conformance assertions, and NDR-conformant schema
documents. That is a real build with no reusable domain to start from.

**Operational reason.** The consumers today are a public reader and a retrieval
index, not a system-to-system exchange with a partner agency. NIEM's value
appears when a second system must consume the exchange under an agreed contract.

**Conclusion, and the honest form of it.** NIEM is not the right encoding for
the document model. It is a strong candidate for the **exchange layer** the day
a partner system consumes this corpus, and the natural design is an extension
namespace augmenting `nc:DocumentType` with our identifier, status, and
authority-edge properties, reusing `cui` for markings. Recorded as: considered,
not adopted for the encoding, planned for the exchange layer, revisit on first
external consumer.

### Two precision points for any submission

- NIEM moved to **OASIS Open**, not the Linux Foundation. NDR 6.0 and Model 6.0
  became OASIS Standards on 28 November 2025 and were submitted to ISO/IEC
  JTC 1 in June 2026.
- NDR 6.0 section 6 forecloses a claim people make casually: "NIEM does not
  define conformance for applications, systems, databases, or tools. It is
  therefore impossible for any of these to properly claim 'NIEM conformance'."
  Only namespaces, schema documents, models, and messages can conform. Never
  write that the system is NIEM-conformant.

---

## 7. DCAT-US and data.gov - GAP FIXED

OMB M-25-05, 15 January 2025, rescinded and replaced M-13-13 and states:

> The OMB-approved standard metadata schema will conform to the United States
> profile of the W3C Data Catalog Vocabulary Version 3, known as the
> DCAT-US 3.0.

Its compliance table sets **30 September 2026** for agency inventories to be
updated to DCAT-US 3.0 and hosted at `www.[agency].gov/data.json`.

FIX APPLIED: `tools/emit_dcat.py` produces a DCAT-US 3.0 catalog with one
dataset and four distributions - canonical JSON, XML export, authority JSON-LD,
and the rendered library. The publication gate runs first, so a record with
`publishable=false` never reaches the catalog.

Three things this does NOT claim, stated in the tool's own header: this is a
catalog record for an unofficial reference corpus, it is not an agency data
inventory, and emitting it makes nobody compliant. It exists so the packaging is
right the day an issuing authority adopts it.

Three practical notes recorded in the tool:

- v3.0 moved from JSON Schema Draft-04 to **2020-12**. Old validators give
  false passes.
- **`accessLevel` is not a v3.0 core field**; `accessRights` carries that
  meaning. Both are emitted, because data.gov harvests 1.1 and 3.0 side by side
  during the transition.
- data.gov reads the source **verbatim**: "It does not correct typos, normalize
  field values, or fill in missing information. Your agency owns the quality of
  your catalog entries."

Status caution for any submission: DCAT-US 3.0 is promulgated and required, but
its prose specification is a Candidate Recommendation Snapshot and
resources.data.gov labels the implementation guidance draft as of 2026-07-05.
Say "required under M-25-05," not "final."

---

## 8. CKAN - NOT APPLICABLE

CKAN is the platform running `catalog.data.gov` and `inventory.data.gov`, both
on 2.11.2. Harvesting has moved to a separate service at `harvest.data.gov`.

It constrains nothing about how we encode. What matters is item 7: publish a
`data.json` at a stable public URL with no authentication, then register a
harvest source. Relevant at publication, not at design.

---

## 9. S1000D - ADAPTED

Current issue is **Issue 6**, September 2024. Free of charge but **not
open-licensed**: copyright ASD, AIA, and ATA, and S1000D is a registered
trademark of ASD. Treat as zero-cost, all-rights-reserved. Anyone embedding its
schemas or code vocabularies in a redistributed product needs the click-through
terms read by counsel.

DoD use is service-by-service, not department-wide: MIL-STD-3031B (Army),
MIL-STD-3048B/C (Air Force), and a NAVSEA letter of 17 February 2010 that
**authorizes but does not mandate** it. Both service standards are pinned to
**Issue 4.2**, two major issues behind current.

### The architectural convergence is the finding

S1000D arrived at the same architecture we did, from the technical-publications
community rather than the legislative one:

| S1000D | Our stack |
|---|---|
| Data Module - the atomic authored unit | the canonical record |
| Common Source DataBase - one repository, publications assembled from it | `canonical` as corpus of record, every output derived |
| Data Module Requirements List - the agreed scope contract | `spine_set.txt` and the family manifests |
| `issueNumber` / `inWork` - released issue versus draft revision | `verification` UNVERIFIED versus VERIFIED |
| `dmRef` plus `referredFragment` - address a fragment inside another module | our provision-path citations |

That last row is the important one. S1000D solved cross-document
fragment-level addressing by referencing a **code**, not a location, so
references survive repository churn. Our `uslm_identifier` does the same thing.
Two communities, same answer, independently.

### Two ideas worth adopting

1. **The information code.** The S1000D Data Module Code carries a three-digit
   `infoCode` - a controlled vocabulary of information KINDS, not subjects.
   `022` is a business-rules module, `0A2` an applicability repository. We have
   no equivalent. A controlled vocabulary of provision kinds - requirement,
   definition, responsibility, procedure, exception - would make the corpus
   queryable in a way subject keywords never will.
2. **The applicability model.** S1000D declares a property vocabulary in a
   central repository, writes boolean `evaluate`/`assert` expressions over it,
   and binds arbitrary content nodes to those expressions with `applicRefId`.
   That is structurally what `rules.json` and the parental-leave evaluator are
   reaching for, with twenty years of production use behind it. Worth reading
   before the evaluator generalizes.

---

## 10. Open XML SDK, DOCX, LOC format registry - NOT APPLICABLE to the read path

These govern the **authoring** side. The read pipeline ingests PDF and HTML and
never touches DOCX.

They become directly relevant to SemperScribe, and there the connection is
concrete rather than theoretical: DoWI 5025.01 makes Word the production format
("the FP sends the MS Word file of the issuance ... to the Directives
Division"), and SECNAV M-5215.1 prescribes the typography down to the font. A
tool that authors a compliant naval letter AND exports policy-as-data in one
step has to speak Open XML properly. The LOC format description is the right
reference for long-term preservation posture.

Recorded as NOT APPLICABLE here, GOVERNING for SemperScribe.

---

## 11. SGML, ISO 8879 - NOT APPLICABLE

The doctrinal ancestor of everything else in this list, and the ancestor of the
DON XML NDR the alignment plan already treats as a baseline. Its live
descendants bind; it does not.

Of historical note, and it matters for a supersession claim: MIL-STD-2361C
established SGML requirements for Army training and doctrine publications and
was **cancelled 15 March 2021**, superseded through MIL-STD-40051-1D and -2D
into MIL-STD-40051E. The SGML lineage in DoD technical publications is now
entirely inside MIL-STD-40051E.

---

## 12. Protégé and WebProtégé - ADAPTED

Protégé Desktop **5.6.9**, released 7 March 2025 - live, but maintained as a
community project with a single primary maintainer. WebProtégé's last tagged
release is 4.0.2 (July 2023) and the monolithic repository is mid-rearchitecture
into microservices.

Our authority graph is JSON-LD, not OWL. That is the right call for now: the
graph asserts cited relationships between documents, which needs no description
logic. Protégé earns its place when the ontology grows classes and reasoning -
inferring that a provision is in force from the status of everything above it,
for instance. Recorded as: correct tool, not yet needed, do not adopt early.

---

## 13. IHMC KAoS - NOT APPLICABLE

Dormant. The evidence is unambiguous: last publication 2008, site last modified
between 2010 and 2012, user guide dated January 2013, download pages return 404,
and distribution was via Java Web Start - removed from the Oracle JDK in 2018.

Its **conceptual model is still worth reading**: policy as a constraint on an
OWL-defined action class, and the authorization/obligation by positive/negative
quadrant. Do not depend on the code.

The live successors are the ones to name in any submission:

| Standard | Body | Status | Fit |
|---|---|---|---|
| **LegalRuleML Core 1.0** | OASIS | OASIS Standard, 8 Sep 2021 | **The closest fit of anything in this matrix.** Deontic operators, defeasibility, temporal validity, jurisdiction, and provenance back to the authoritative source text. That last property is exactly what a government policy corpus needs and what ODRL and XACML both lack. |
| ODRL 2.2 | W3C | Recommendation, 2018, actively extended | Permission, prohibition, and duty as RDF. The KAoS idea, alive. |
| SHACL | W3C | 1.0 Recommendation; 1.2 suite in Working Draft | The right tool for making "this record is well formed" machine-checkable. Complements rather than competes. |
| XACML 3.0 | OASIS | Standard; 4.0 in development | Access-control decisioning. Not an encoding for policy text. |

Recommendation on record: when `rules.json` generalizes past parental leave,
read LegalRuleML first. Its isomorphism requirement - a rule traceable to the
provision that states it - is the discipline this corpus already practices, and
adopting the vocabulary would make that discipline legible to outside reviewers.

---

## 14. SFIS - NOT APPLICABLE

The Standard Financial Information Structure is the DoD enterprise financial
data standard. It governs financial reporting elements. Nothing in the policy
corpus is a financial transaction.

The one adjacency: MCO 1050.3J's reference list names DoD 7000.14-R, the
Financial Management Regulation, and the store holds DoDFMR records. That is a
policy document citing a financial regulation, not financial data. No SFIS
obligation attaches.

---

## 15. NPS Monterey Phoenix - NOT APPLICABLE

A behavior modeling language and tool for reasoning about system and process
behaviors, generating use-case scenario variants. It models processes, not data.

Where it could earn a place, stated so the row is not merely dismissive: the
publish-review-republish loop is a process with real failure modes, and the
corpus plan named the absence of that loop as the thing that makes a public
corpus stale within a quarter. Modeling that workflow is a legitimate use. It
governs nothing about the encoding.

---

## Actions arising

| # | Action | State |
|---|---|---|
| 1 | Remove the reserved period from USLM path segments | DONE, in staging, needs [ID2] ruling |
| 2 | Emit a DCAT-US 3.0 catalog | DONE, `tools/emit_dcat.py` |
| 3 | Document the NIEM consider-first assessment per DoDI 8320.07 | DONE, section 6 above |
| 4 | Publish a namespace register - GPO reserves nothing | DONE, `NAMESPACES.md` |
| 5 | Rebuild the exporter against schema 0.5.0 | DONE, `tools/export_issuance.py` |
| 6 | Add `@startPeriod` / `@endPeriod` and separate lifecycle from verification | DONE, see section 16 |
| 7 | Decide the `superseded` status mapping - USLM has no such value | DONE, kept as our own term with a documented translation, section 16 |
| 8 | Publish an XSD so the "validates against a published schema" claim is testable | DONE, `schema/usmc-issuance-2.0.xsd` |
| 9 | Read LegalRuleML before generalizing `rules.json` | OPEN |
| 10 | Consider an information-kind vocabulary, per the S1000D infoCode | OPEN |
| 11 | Retire `export_uslm.py` and the `.uslm.xml` extension in the repo push | OPEN, needs a repo commit |

## Confidence

- Verdicts 1, 4, 6, 7: 0.95. Specification and directive text read directly and quoted.
- Verdicts 2, 3, 5, 8, 11, 13, 14, 15: 0.9. Straightforward scope determinations.
- Verdicts 9, 10, 12: 0.85. Correct as scope calls; the adoption recommendations carry judgment.
- The DSPO roadmap promised in the Digital Standards Strategy: UNCONFIRMED whether it has been produced. No published roadmap found as of 2026-08-03.
- Whether DoDI 8320.07 has been reissued since Change 1 of December 2017: UNCONFIRMED. The 2015/2017 PDF is still the version served.

---

## 16. The exporter rebuild - what changed and why

`tools/export_issuance.py` replaces `tools/export_uslm.py`. Output validates
against `schema/usmc-issuance-2.0.xsd`, published in this repository. 54 of 54
exports valid, 20,088 provisions, 286 provision-level citations, 367 authority
edges.

### Lifecycle and verification are now separate attributes

The old export asked one `@status` attribute to answer two unrelated questions
and gave the verification answer, so every document read as though its policy
status were unknown. They are now distinct:

    @lifecycle     is the policy in force?        active | cancelled |
                                                  superseded | unknown
    @verification  has a human confirmed the      VERIFIED | UNVERIFIED
                   extraction against source?

A document can be active and UNVERIFIED. Almost all of them are.

### The `superseded` decision

USLM's `StatusEnum` has no `superseded` value. The nearest terms are `repealed`
and `omitted`, and both assert something the source never said. RULING: keep
`superseded` in our own vocabulary and publish the translation rather than force
the mapping. A consumer converting to USLM maps `active` to `inEffect` and
`cancelled` to `cancelled`, and carries `superseded` as a refinement. The
lossiness is stated in the XSD annotation rather than hidden in a lookup table.

### The file extension changed, deliberately

Output is `.issuance.xml`, not `.uslm.xml`, and the tool is no longer named for
USLM. The vocabulary is a sibling of USLM in its own namespace, and USLM's
Objective annotation excludes executive branch documents. Naming our files
`.uslm.xml` invited exactly the misreading section 1 warns against. The repo
push notes still reference the old name and extension and need updating.

### A defect the rebuild surfaced

Attribute values were not being run through the XML 1.0 character filter. Only
element text was. A form feed inside a distribution statement extracted from PDF
was enough to produce a file that no parser would read, and it surfaced only at
parse time in whichever consumer opened it next. Filtering now happens where the
attribute is written.
