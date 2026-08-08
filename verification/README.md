# verification/

The attestation ledger. What a human read, when, against which edition, and what
the content was at that moment.

Design and rationale: `VERIFICATION-DESIGN.md`. This file is the format.

---

## Why status is not stored

`VERIFIED` is **derived**, every build, by comparing what a human attested to
against what the corpus currently says. It is not a field anyone edits.

That is the whole control. Before this, a provision stamped VERIFIED kept the
stamp if the extraction later changed its text, and nothing detected it - the
same defect class as the three integrity defects fixed on 2026-08-04, where a
build reported success while quietly changing what it should not.

An attestation binds to a content hash. **It stops applying the moment that
content changes**, and the change is reported as `INVALIDATED` rather than
absorbed.

## Files

| File | Published | What |
|---|---|---|
| `attestations.jsonl` | yes | append-only, one JSON object per line |
| `correction_requests.jsonl` | yes | rejections awaiting an owner decision |
| `roster.json` | **NO, gitignored** | maps verifier ids to people |

Verifier ids are opaque. A public register of who attested to what is personal
data attached to an official act, and it gets the same treatment as the contact
details in `canonical/`: held unpublished, never rendered. The site shows the
state, the method, and the date. Never a name.

## An entry

```json
{
  "assertion": "/us/dod/don/usmc/maradmin/2023/051#MAX_PARENTAL_LEAVE_DAYS",
  "kind": "rule",
  "content_hash": "sha256:a31b62c9...",
  "verified_against": {
    "edition": "MARADMIN 051/23, DTG 272030Z JAN 23",
    "obtained": "marines.mil, retrieved 2026-06-24",
    "artifact_hash": null
  },
  "verifier": "V-001",
  "at": "2026-06-24T00:00:00+00:00",
  "method": "read-and-compare",
  "result": "VERIFIED",
  "note": ""
}
```

`result`: `VERIFIED`, `REJECTED`, `UNABLE`.
`method`: `read-and-compare`, `second-person`, `authored-match`, `imported`.
`kind`: `rule`, `provision`.

Append-only. A superseding entry for the same assertion and verifier wins on
`at`; nothing is edited in place and nothing is deleted.

## What the hash covers

**Rule value** - the value, the unit, and the citation identifier. Not the note,
not the label, not the id. Editing prose in a note is not a change to the claim.
Changing 84 to 90, or repointing the citation from para 11.d to para 8, is.

**Provision** - its text only. Not the identifier, label, depth, or position.
Renumbering or moving a provision must not invalidate a human's reading of its
words.

Text is normalized before hashing: CRLF to LF, per-line strip, internal
whitespace runs collapsed, blank edges trimmed, Unicode NFC.
`tools/normalize.py` is that rule and it is the only place it lives. Hashing raw
bytes would invalidate every attestation in the corpus on the first
Windows-to-Linux round trip, because the working tree is CRLF and Linux-written
files arrive with LF - see `SESSION_HANDOFF.md` section 8.

Run `python tools/normalize.py` for a smoke check that variants collapse and a
real change does not.

## Verdicts

| | |
|---|---|
| `VERIFIED` | live attestation, hash matches, quorum met |
| `INVALIDATED` | attested, then the content changed. **The interesting one.** |
| `REJECTED` | a human read it and says the encoding is wrong. A found defect. |
| `UNABLE` | a human tried and could not, usually because the source was unobtainable |
| `QUORUM_SHORT` | attested and matching, but short of the required independent readings |
| `UNVERIFIED` | no attestation |

## Quorum

Rule values consumed by an evaluator need **two attestations by different
verifiers**. A wrong rule value produces a wrong computed answer about a
Marine's leave with no human between the error and the reader.

Provision text needs **one**. It renders next to its citation where any reader
can check it.

An imported seed carries `verifier: null` and never counts toward quorum. A
legacy claim is not an independent reading.

## Commands

```
python tools/normalize.py                                   # smoke check
python tools/attest.py --seed                               # one-time import
python tools/attest.py --list                               # what needs work
python tools/attest.py --next --verifier V-001              # record one
python tools/verify_status.py                               # derived status
python tools/verify_status.py --json                        # machine readable
python tools/verify_status.py --fail-on-invalidated         # build gate
```

`attest.py` never writes `canonical/` or `data/`. A rejection writes a
correction **request**; the change itself goes through `tools/corrections.py` as
an owner action.

## Build integration

Add as a stage, after validation and before render:

```
python tools/verify_status.py --fail-on-invalidated
```

Idempotent: it reads two inputs and writes nothing. A build that finds an
invalidated attestation stops, because the alternative is publishing a VERIFIED
badge over text nobody has read.
