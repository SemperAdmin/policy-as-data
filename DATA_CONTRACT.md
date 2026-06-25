# Data contract, policy-as-data proof of concept

This document governs the encoded artifacts in `data/`. It is the standing
mandate for anyone — human or agent — who touches the encoding.

## What this proves

That one Marine Corps issuance can be restricted into structured data — markup
plus an authority graph — faithfully enough that every provision is addressable
and its authority is traceable to statute. The worked document is MARADMIN
051/23, the Military Parental Leave Program.

## Read-only mandate

The files in `data/` are a faithful record of the source issuance, not a
workspace.

- Encoded values read as they do because the issuance says so. The 84-day cap
  is 84 because MARADMIN 051/23 says 84.
- No value is added, changed, or removed except to correct it against the
  source issuance text, with the change recorded. Nothing is encoded that is
  not in the source.

## File map

- `data/maradmin-051-23.uslm.xml` — document-structure layer. USLM-aligned
  markup of the issuance, with stable `@identifier`s on every provision.
- `data/maradmin-051-23.authority.jsonld` — authority graph. Links each encoded
  provision up through DoDI 1327.06 to 10 U.S.C. 701.
- `data/maradmin-051-23.rules.json` — machine-readable rule values extracted
  from the text, each carrying a verification status and a citation.

## Verification legend

Every encoded value and every citation carries one status.

- `VERIFIED` — confirmed against the retrieved issuance text.
- `UNVERIFIED` — the value comes from a subject-matter assertion and the exact
  source line is not yet located. An UNVERIFIED provision is recorded as
  present-but-unproven, and is not asserted in the USLM markup until confirmed.

## Verified versus unverified, current state

VERIFIED (confirmed against the retrieved issuance text; corrections logged in
`data/maradmin-051-23.rules.json`):

- `MAX_PARENTAL_LEAVE_DAYS` = 84. Source: MARADMIN 051/23, para 11.d.
- `ENTITLEMENT_WINDOW_DAYS` = 365. Source: MARADMIN 051/23, para 8.c.(3).
- `MIN_INCREMENT_DAYS` = 7. Source: MARADMIN 051/23, para 8.a.(1)(b).
  (Confirmed against source; was previously UNVERIFIED.)
- `EVENT_PROXIMITY_MERGE_HOURS` = 72. Source: MARADMIN 051/23, para 8.b.(1).
  (Confirmed; the issuance states a 72-hour period, previously asserted as 3 days.)

UNVERIFIED, load-bearing-but-unproven (kept so the distinction stays live on the
face of the data):

- `CURRENT_DOD_PARENTAL_LEAVE_WEEKS` = 12. DoDI 1327.06, para 3.11.c (ADPL). The
  section body is not yet encoded, so the source line is not confirmed.

## Why the verified/unverified split is on the face of the data

The point of the encoding is to distinguish confirmed policy from asserted
policy at the level of the data itself. A reader never has to guess which
provisions are grounded in the issuance text and which are awaiting a confirmed
source line — the status says so, on every value and every citation.

## Confidence

Cap and window encoding: 0.9. Increment and proximity values as written: 0.55,
source line unverified. Encoding approach: 0.82.
