# Human verification - process design

Date: 2026-08-08. Owner: Stephen. Status: proposed.

Companion to `VERIFICATION.md`, which records whether the demo works, and to
`schema/README.md`, which defines the verification semantics. This document
covers the missing piece: **the act itself.**

---

## 1. The defect this closes

**Verification today is a status field, not a process.** `VERIFIED` and
`UNVERIFIED` exist in the schema, `data/` is hand-encoded and confirmed, and
promotion is stated as explicit and recorded. Nothing anywhere records **who**
verified, **against which edition**, **on what date**, or **what the text was at
that moment**.

The consequence is a specific and serious one. A provision stamped VERIFIED
keeps that stamp if the extraction later changes its text. Nothing detects it.
That is the same defect class as the three fixed on 2026-08-04 and recorded in
`SESSION_HANDOFF.md` section 10 - a build reporting success while quietly
changing what it should not - and it is the more expensive kind here, because
the whole claim of this project is that its provenance can be trusted.

Everything below follows from one control: **an attestation binds to the exact
content it attested to, and stops applying the moment that content changes.**

---

## 2. The atom

Verification applies to an **assertion**, not to a document. Two kinds exist
today and both are claims about what a source says:

| Kind | Example | Where it lives |
|---|---|---|
| **Provision text** | `/us/dod/dodi/1327.06/s3/3.11/c` says what the record says it says | `canonical/`, `data/` |
| **Rule value** | `MAX_PARENTAL_LEAVE_DAYS` is 84, at MARADMIN 051/23 para 11.d | `data/*.rules.json` |

Record-level and document-level status is **derived**, never set by hand. A
record is VERIFIED when every assertion in it is. Most will not be, and the site
should say so per provision rather than per document, because per-document is
where an honest UNVERIFIED gets read as "the whole thing is unreliable."

---

## 3. Where attestations live, and why not in the record

**Recommendation: an append-only ledger outside `canonical/`.**

```
verification/attestations.jsonl      append-only, one JSON object per line
verification/roster.json             UNPUBLISHED, maps verifier ids to people
```

Three reasons, and the first is decisive.

1. **`canonical/` is read-only to tooling.** `DATA_CONTRACT.md`. A verification
   tool that writes the store breaks the mandate on day one.
2. **An attestation is a fact about a human act, not about the document.** The
   document did not change when someone read it.
3. **It makes status derived and therefore recomputable.** The build reads the
   ledger, hashes current content, and emits status. That is idempotent by
   construction, which every stage here has to be.

Migration is additive. Existing inline statuses seed the ledger as
`method: "imported"` attestations with the current content hash, dated to the
import, and honestly marked as carrying no verifier and no source edition.
Nothing is lost and nothing is overstated.

### The entry

```json
{
  "assertion": "/us/dod/don/usmc/maradmin/2023/051/p11/d",
  "kind": "provision",
  "content_hash": "sha256:...",
  "verified_against": {
    "edition": "MARADMIN 051/23, DTG 272030Z JAN 23",
    "obtained": "marines.mil, retrieved 2026-06-24",
    "artifact_hash": "sha256:..."
  },
  "verifier": "V-003",
  "at": "2026-06-24T00:00:00+00:00",
  "method": "read-and-compare",
  "result": "VERIFIED",
  "note": ""
}
```

`result` takes `VERIFIED`, `REJECTED`, or `UNABLE`. `method` takes
`read-and-compare`, `second-person`, `authored-match`, or `imported`.

---

## 4. The control: hash binding

Status derives to VERIFIED **only if** the current normalized content hash
equals the attested hash. Any difference reverts the assertion to UNVERIFIED,
and the build reports the count and the identifiers. Never silently.

**This needs a normalization rule, and getting it wrong would be expensive.**
`SESSION_HANDOFF.md` section 8 records that `git status` already reports dozens
of phantom modifications because the working tree is CRLF and files written from
a Linux environment arrive with LF. If the content hash is taken over raw bytes,
every Windows-to-Linux round trip invalidates every attestation in the corpus
and the verification effort evaporates.

**Normalization, before hashing, and this is not negotiable:**

1. Line endings to `\n`.
2. Trailing whitespace stripped per line.
3. Runs of internal whitespace collapsed to one space.
4. Unicode NFC.
5. Hash the provision's **text only** - never its identifier, attributes,
   position, or surrounding structure.

Point 5 matters: moving a provision, renumbering it, or re-rendering the file
must not invalidate a text attestation. Only a change to what it says should.

---

## 5. Targeting - you cannot verify 20,178 provisions

The corpus holds 20,178 provisions. Hand-verifying them is not a plan, it is a
way to guarantee nothing gets verified. Verify what is load-bearing and publish
the fact that everything else is not.

| Tier | What | Approximate count | Why first |
|---|---|---|---|
| **V1** | Rule values consumed by an evaluator | **6 today** | They produce computed answers about a Marine's entitlement. Highest consequence, smallest set. |
| **V2** | Source paragraphs named by a `cited` edge | order of 300, from 362 edges | Every authority claim on the site rests on one of these. If an edge names a paragraph that does not say what the edge claims, the chain is wrong. |
| **V3** | Provisions rendered as the answer on a spine page | five spines | What a reader actually reads. |
| **V4** | Everything else | ~19,800 | Stays UNVERIFIED, and the site says so per provision. |

V1 and V2 together are on the order of 300 assertions. That is days of focused
work, not years, and it converts the site's central claim from asserted to
attested. **Do V1 first.** Six rule values, and two of them are the 12-weeks /
84-days pair the POC turns on.

---

## 6. The workflow

Deliberately a CLI and a file. No web application, no accounts, no workflow
engine.

```
1.  python tools/attest.py --next
        picks the highest-priority assertion with no live attestation

2.  the tool prints:
        the identifier
        the encoded text, exactly as stored
        the citation it claims (document, paragraph, edition)
        where to open the authoritative source

3.  the human opens the issuing authority's copy and compares

4.  the human answers:
        v  verified
        r  rejected, and supplies what the source actually says
        u  unable, and supplies why

5.  the tool appends one ledger entry. It NEVER writes canonical/.

6.  on reject, a correction request is written to staging. The change itself
    goes through tools/corrections.py, unchanged, as an owner action.

7.  build.sh derives status, and reports:
        verified, rejected, unable, invalidated-since-last-run
```

**Rejection is the valuable outcome.** A rejected attestation is a found defect
in the encoding, which is worth more than a confirmation. Report rejections
prominently rather than burying them in a pass rate.

---

## 7. Two-person rule, where it is proportionate

| Assertion kind | Attestations required |
|---|---|
| Rule value consumed by an evaluator | **two, by different verifiers, independently** |
| Provision text | one |
| Authored-match, per `INTEGRATION-SEMPERSCRIBE.md` section 4 | one, plus the hash comparison, which is machine-checked |

Rationale: a wrong rule value produces a wrong computed answer about someone's
leave, with no human between the error and the reader. A wrong provision text is
visible to anyone reading the page next to the citation. Different consequence,
different control. Applying two-person to all 20,178 provisions would be
theatre, and would stop verification happening at all.

---

## 8. Publication, and the privacy problem in it

The site should show, per provision: the verification state, the method, and the
date. That is the trust artifact and it is the thing currently missing - today a
reader sees UNVERIFIED with no way to know what would change it.

**Do not publish verifier names.** A public register of who attested to what is
personal data attached to an official act, and this repository already holds the
discipline that contact details stay in the unpublished store and are masked at
the export boundary. Same treatment:

- The ledger carries an opaque verifier id.
- `verification/roster.json` maps ids to people and is **never published**, the
  same way `canonical/` is not.
- The site shows role and date, never a name.

Add `verification/roster.json` to `.gitignore` before the first attestation is
written, not after.

---

## 9. What this changes elsewhere

| Artifact | Change | Size |
|---|---|---|
| `canonical/`, `data/` | none. Status becomes derived on render. | zero |
| `schema/README.md` | verification semantics gain the attestation model | small |
| `usmc-issuance-2.0.xsd` | `@verification` may gain `AUTHORED`, per the integration design | small, and only if that integration proceeds |
| `build.sh` | one new stage: derive status, report invalidations | one stage, idempotent |
| `tools/` | `attest.py` and `verify_status.py` | two tools |
| `.gitignore` | the roster | one line |
| the site | per-provision badge with method and date | renderer change |

No new dependency. Standard library, one JSONL file, `hashlib`.

---

## 10. Risks

- **The normalization rule is the whole design.** Get it wrong and either every
  attestation invalidates on a line-ending change, or a real text change slips
  through. Test it against the CRLF problem in `SESSION_HANDOFF.md` section 8
  before writing a single attestation.
- **An append-only file in git is a merge conflict generator** if more than one
  verifier works at once. At current scale, one verifier, this is not a problem.
  Name it now so it is not discovered later; the fix is one file per verifier,
  merged at build.
- **Attestation without the source is worthless.** `REFERENCES.md` records that
  acquisition is human-in-the-loop and that two documents are blocked, one
  because the PDF is a scanned image. You cannot verify against a source you do
  not have, and `UNABLE` with a reason is the correct and honest outcome there.
- **Verification decays.** An attestation against the 2023 edition says nothing
  about the 2025 reissue. The ledger records the edition, so the existing drift
  machinery can flag attestations made against a superseded edition. That is a
  P2 addition and worth noting now.

---

## 11. Priorities

| | Item | Priority |
|---|---|---|
| P0 | Ledger format, normalization rule, `attest.py`, `verify_status.py`, derived status in the build, roster gitignored | required |
| P0 | V1 verified: all six rule values, two-person | required, and it is the POC's input |
| P1 | V2 verified: source paragraphs behind cited edges | usable MVP |
| P1 | Per-provision badge on the site | usable MVP |
| P2 | Attestation decay against superseded editions | later |
| P2 | Multi-verifier ledger sharding | when a second verifier exists |
| P3 | Any web UI, account system, or review queue | not now |

---

## 12. Confidence

0.85. The defect in section 1 follows directly from the absence of any
verifier, date, or content-hash field in the current schema and from the
integrity defects already recorded. The normalization trap in section 4 is
confirmed by the CRLF finding in `SESSION_HANDOFF.md` section 8.

Lower on section 5's counts: 20,178 provisions and 362 edges are quoted, but the
number of **distinct** source paragraphs behind those edges was not computed and
is an estimate. Compute it before committing to a V2 schedule.
