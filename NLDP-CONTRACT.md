# NLDP contract and SemperScribe export audit

Date: 2026-08-08. Owner: Stephen.
Source audited: `github.com/SemperAdmin/semperscribe` at `f843a95`, 2026-08-07.
Supersedes section 5 of `INTEGRATION-SEMPERSCRIBE.md`, which was written against
an unknown schema.

---

## 0. The headline

**Option B is already built.** `SESSION_HANDOFF.md` section 7.3 records the
SemperScribe integration as an open decision between Option A, a Python bridge
in this pipeline, and Option B, native TypeScript export in SemperScribe, and
states "Neither is built."

That is now false. `src/lib/policy-as-data.ts` in SemperScribe emits a
policy-as-data canonical record at `schema_version: "0.4.0"`, with provisions,
paths, labels, depths, parents, and `uslm_identifier` values, and it has a test
file beside it. Correct that entry in `SESSION_HANDOFF.md` before anything else,
because a stale open decision is how the same work gets done twice.

**R2 is met.** The largest unknown in the integration design is resolved, and
the LEOS question in `resources/24-leos.md` closes at step 1. Keep SemperScribe.

**And the exporter carries ten defects**, four of them serious, listed in
section 3. Two are re-finds of defects this repository already fixed and
recorded. That is the argument for where the mapping should live, in section 4.

---

## 1. What NLDP actually carries

From `sample-directive.nldp` and `docs/NLDP_FEATURE_GUIDE.md`.

```json
{
  "format": "NLDP", "version": "1.0",
  "metadata": { "createdAt", "formatVersion", "createdBy",
                "package": { "title", "description", "tags" } },
  "integrity": { "dataHash", "crc32", "recordCount" },
  "data": {
    "formData": { "documentType", "ssic_code", "consecutive_point",
                  "sponsor_code", "date_signed", "subj", "from", "to",
                  "sig", "distributionStatement": { "code" } },
    "paragraphs": [ { "id", "level", "content", "isMandatory", "title" } ],
    "references": [ { "text", "order" } ],
    "enclosures": [ { "text", "order" } ],
    "vias": [], "copyTos": [],
    "directiveMetadata": { "lastModified", "status" }
  }
}
```

**Conflict, and it needs resolving rather than picking.** The sample and the
feature guide disagree. The guide documents `metadata.packageId`,
`metadata.author{name,unit,email}`, `metadata.checksums`, and
`formatVersion: "1.0.0"`. The sample carries none of those, uses a top-level
`integrity` block instead of `metadata.checksums`, and says
`formatVersion: "1.0"`. `src/lib/nldp-format.ts` is the implementation and is
the only authority here. **Do not write a parser against the guide.** Read the
format module, then correct whichever of the two is wrong.

## 2. Requirements, answered

Against R1 to R9 in `INTEGRATION-SEMPERSCRIBE.md` section 5.

| # | Requirement | Verdict | Evidence |
|---|---|---|---|
| R1 | Document identity | **MET, in components** | `documentType`, `ssic_code`, `consecutive_point`, `date_signed`. The number is composed, not stored as a string, which is the better shape and is what makes minting here correct. |
| R2 | **Structured provisions with native designators** | **MET** | `paragraphs[]` carries `level` and order. The designator is a pure function of that tree, implemented in `src/lib/citation.ts`, described in its own header as "a leaf module with no imports from the formatter/engine layer." Not a text blob. **This is the requirement that decided the integration.** |
| R3 | Reference list as structured entries | **NOT MET** | `references: [{text, order}]`. Free text. The citation grammar in this pipeline still has to parse it, and `SESSION_HANDOFF.md` section 9 already records 174 of 384 reference items unparsed. The integration does not remove reference parsing. |
| R4 | Enclosures distinguished from body | **MET in NLDP, LOST in export** | `enclosures[]` is a separate array. `createPolicyDataRecord` accepts it, writes `void enclosures`, and drops it. The `encl/` reserved namespace from `NAMESPACES.md` N7 is unused. |
| R5 | Lifecycle | **PARTIAL** | `directiveMetadata.status` exists. Only `"draft"` observed. The enum is unknown and must be obtained. |
| R6 | Signature and promulgation date | **MET** | `sig`, `date_signed`. |
| R7 | Hash of the signed artifact | **NOT MET** | `integrity.dataHash` hashes the NLDP payload, not the signed document. The authored-to-verified promotion in `VERIFICATION-DESIGN.md` section 7 has nothing to compare against. |
| R8 | Contact fields flagged | **PARTIAL** | The guide describes optional personal info and an `author.email`. The export drops `pocs` entirely, which is safe but not faithful. |
| R9 | Cancellation and supersession | **NOT MET** | Not present in NLDP and emitted as empty arrays. |

**Five met or partially met, three not met, one lost in translation.** None of
the gaps is fatal and all are additive changes to the NLDP format.

---

## 3. Defect register - the existing exporter

`src/lib/policy-as-data.ts`, read at `f843a95`. Each entry names the constraint
it breaks and where that constraint is written.

### Serious

**D1. The identifier carries a period.** `deriveDocIdentity` builds
`/us/dod/don/usmc/mco/${num.toLowerCase()}` from an `ssic` such as `5215.1K`,
producing `/us/dod/don/usmc/mco/5215.1k`. `NAMESPACES.md` N3: no segment
contains a period, because USLM reserves it for the manifestation suffix, so
that identifier resolves as document `mco/5215` in format `1k`. This is the
exact defect the machine tier fixed and recorded. SECNAV, NAVMC, and MCBUL paths
have the same flaw. **Fix:** periods to underscores, one shared rule.

**D2. `converted_at` is stamped from the clock.**
`converted_at: new Date().toISOString()`. Re-exporting an unchanged document
produces a different record, so ingest cannot be idempotent. This is a re-find
of the third integrity defect fixed on 2026-08-04 and recorded in
`SESSION_HANDOFF.md` section 10: "Eleven top-tier records rewritten by the
clock... The stamp is now the literal `ENTERED = ...`, bumped by hand." **Fix:**
derive the stamp from document content or from `date_signed`, never from now.

**D3. `publication.publishable` is hardcoded `true`.** The quarantine gate is a
hard constraint - `SESSION_HANDOFF.md` section 4.2, "records are never exported,
rendered, or ingested" - and an exporter that always asserts publishable removes
it at the source. Worse, the code reads `distributionStatement.code` and writes
it to `distribution_statement` **without letting it affect publishability**.
Statement A is approved for public release. B through F and X are not. **Fix:**
derive `publishable` from the statement code, and default to `false` with a
reason when the code is absent or unrecognised.

**D4. A draft exports as active.** `status: 'active'` is hardcoded while the
NLDP sample carries `directiveMetadata.status: "draft"`. A draft entering the
corpus of record as active is the worst defect this integration could produce,
because the site presents its contents as policy. **Fix:** map the NLDP status,
and reject anything that is not signed or promulgated.

### Substantive

**D5. `source_hash` carries the literal string `"AUTHORED"`.** The schema
requires `provenance.source_hash` and means a hash of the source artifact.
Putting a state name there destroys the ability to verify against a signed
document. Notable convergence: SemperScribe independently reached for exactly
the concept proposed in `INTEGRATION-SEMPERSCRIBE.md` section 4. It is in the
wrong field. **Fix:** add `AUTHORED` to the `verification` enum, which today
admits only `VERIFIED` and `UNVERIFIED`, and let `source_hash` carry the hash of
the signed artifact once R7 exists.

**D6. References are exported as raw strings with `edge_meta: []`.** No cited
edges are produced. Every authority relationship this project publishes carries
the paragraph it was read from, and this path produces none. Follows from R3.

**D7. Enclosures are dropped.** `void enclosures`. Acknowledged in the code
comment, and it means an order's substantive policy content, which in a real MCO
lives in Enclosure (1), never arrives.

**D8. One flat `body` section.** All provisions land under a single section
anchored `body`. Real orders carry chapters and appendices. Acceptable for a
first pass, and it will not hold for MCO-scale documents.

### Minor

**D9. Pinned to `schema_version: "0.4.0"`.** The schema enum now admits
`0.5.0`, which added the authority tiers above the service. Valid but lagging.

**D10. `pocs: []`.** Contact data is discarded rather than carried and flagged.
Safe, since the failure direction is losing data rather than publishing it, but
it makes the record not faithful, and faithfulness is the store's whole
discipline.

### What is right, and worth saying

- The path ladder matches `NAMESPACES.md` N6 exactly: depth 0 to `pN`, deeper
  levels to bare designators, letters then digits then letters then roman.
- The parent derivation - stack walk to the nearest preceding paragraph with a
  smaller level - is the correct algorithm for a flat list with levels.
- The code documents its own deviation from the UI numbering ladder and states
  which one is authoritative. That is exactly the right instinct.
- The licence is **MIT**. No copyleft problem, unlike LEOS. Note that
  SemperScribe ships a `LICENSE` and this repository does not.

---

## 4. Where the mapping should live

**Recommendation: move it here. Option A, as originally recommended, and retire
the TypeScript exporter to an NLDP emitter only.**

**Why.** D1, D2, D3, D4, and D9 are all the same failure: rules that belong to
this repository being reimplemented in another one. The identifier grammar is in
`NAMESPACES.md`. The quarantine gate is in `DATA_CONTRACT.md` and
`SESSION_HANDOFF.md`. The schema version is in `schema/`. The idempotence
requirement is in `BUILD.md`. None of those is visible from a TypeScript file in
a different repository, and every one of them was broken there.

This is the failure mode `resources/17-rules-as-code.md` names directly:
multiple implementations of the same rule, diverging silently. It has now
happened inside your own programme, between two repositories you own, within
weeks. That is the strongest possible evidence for the reconciliation POC and it
should be cited as such.

**The split I recommend:**

| Side | Owns |
|---|---|
| **SemperScribe** | authoring, the NLDP format, and the paragraph tree with levels and order. Emits NLDP and nothing else. |
| **policy-as-data** | doc-type mapping, identifier minting, the path and label ladder, publishability, status, provenance, schema version, ingest, staging |

**One exception worth arguing for.** `citation.ts` is described as a leaf module
with no engine dependencies. Rather than porting the designator ladder to Python
and having two implementations again, have SemperScribe **emit the computed
designator per paragraph in the NLDP**. Then there is one implementation, in the
tool that owns the numbering, and this side consumes it rather than recomputing
it. That is a small change and it removes a whole class of future divergence.

**Cost of moving it.** SemperScribe loses a feature it already has, and someone
has to say so. The mitigation is that it loses nothing a user sees: the user
still exports a file, and the file becomes NLDP rather than a canonical record.

---

## 5. Two other findings

**The name GunnyBot means two different things.** In this programme it is the
policy factory at `E:\GunnyBot`, ~17,500 documents, recorded in `HANDOFF.md`,
`CHARTER.md` section 4, and `SESSION_HANDOFF.md` section 12. In SemperScribe,
`src/lib/gunnybot/` is a bring-your-own-key, session-only, multi-provider LLM
chat assistant with no connection to the corpus. Two products, one name, both
yours. Rename one before either is described to anyone outside, and update
`CHARTER.md` section 4 either way, because a name register that records one
meaning while a sibling repository uses another is worse than no register.

**SemperScribe's own posture is a governance input to the charter.** Its README
states: "Not Official USMC Software... a non-official Proof of Concept
maintained on a personal basis... carries no Authority to Operate... Do not
enter CUI, PII, or sensitive information." It also carries `RMF_READINESS.md`,
`PRIVACY_POSTURE.md`, `SECTION_508_FINDINGS.md`, and `SBOM_POLICY.md`, which is
more compliance groundwork than this repository has.

Two consequences. First, the artifact of record for any drafted policy is the
**signed document**, not the NLDP, which is another argument for R7. Second,
`CHARTER.md` claims a whole-of-government trajectory while both component tools
are explicitly non-official with no ATO. That is not a contradiction, since a
proof of concept is allowed to be one, but the charter should say it in the same
place it makes the claim.

---

## 6. Next steps, in order

1. **Correct `SESSION_HANDOFF.md` section 7.3.** Option B exists. Record what it
   does and that it is defective, so it is not rebuilt or trusted.
2. **Read `src/lib/nldp-format.ts`** and resolve the sample-versus-guide
   conflict in section 1.
3. **Get the `directiveMetadata.status` enum.** D4 cannot be fixed without it.
4. **Decide section 4.** Mapping here or there. Everything else waits on it.
5. **Then** fix D1 to D4 in whichever repository wins, and only then wire ingest.

Nothing above changes the POC. `POC-PLAN.md` still recommends reconciliation,
and this audit strengthens that case rather than weakening it.

---

## 7. Confidence

0.9. Every defect was read from source at a named commit and every constraint it
breaks is quoted from a file in this repository. The `verification` enum, the
`schema_version` enum, the `status` enum, and the `publication` shape were read
from `schema/policy_document.schema.json` directly.

Lower on two points. The `directiveMetadata.status` enum is **UNCONFIRMED**;
only `"draft"` was observed in one sample. The sample-versus-guide conflict was
identified but not resolved, because `src/lib/nldp-format.ts` was not read in
this pass. Both are named in section 6 rather than assumed.
