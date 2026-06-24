# Frozen data contract, policy-as-data proof of concept

This folder is the spine of the proof of concept. It is artifact one of three.
The implementing agent reads this before writing any code.

## What this proves

One rule from one policy, parsed to structured data, drives a decision the live
system gets wrong. The worked rule is MARADMIN 051/23, the Military Parental
Leave Program. The lead case is a 5-day parental leave request.

## Read-only mandate

The implementing agent treats the files in `data/` as fixed inputs.

- The agent changes logic and UI. The agent does not change encoded rule values.
- A rule value reads as it does because the issuance says so. The 84-day cap is
  84 because MARADMIN 051/23 says 84. If a test wants a different number, the
  test is wrong or the encoding is wrong, and a human decides which. The agent
  does not edit the rule data to make a test pass.

## File map

- `src/types.ts` - the TypeScript contract for `evaluate()`. Input shape, output
  shape, and the four hard constraints on the function.
- `data/maradmin-051-23.rules.json` - the encoded rule values, each with a
  verification status and a citation. This is the file the engine reads at run
  time.
- `data/maradmin-051-23.uslm.xml` - document-structure layer. USLM-aligned
  markup of paragraph 8, with stable identifiers.
- `data/maradmin-051-23.authority.jsonld` - authority graph. Links the cap
  provision up through DoDI 1327.06 to 10 U.S.C. 701.

## Verification legend

Every rule and every citation carries one status.

- `VERIFIED` - the value is confirmed against retrieved issuance text.
- `UNVERIFIED` - the value comes from a subject-matter assertion and the exact
  source line is not yet located. The engine treats an UNVERIFIED rule as
  load-bearing-but-unproven.

## Verified versus unverified, current state

VERIFIED:

- `MAX_PARENTAL_LEAVE_DAYS` = 84. Source: MARADMIN 051/23, para 8.
- `ENTITLEMENT_WINDOW_DAYS` = 365. Source: MARADMIN 051/23, para 8.b.(2).

UNVERIFIED, confirm the source line before the demo relies on either:

- `MIN_INCREMENT_DAYS` = 7. The 5-day case denies only on this rule.
- `EVENT_PROXIMITY_MERGE_DAYS` = 3. The twins-plus-adoption merge depends on it.

## Loud-failure behavior

When the binding constraint for a request is an UNVERIFIED rule, the decision
outcome is `UNVERIFIED`, not `DENY` and not `APPROVE`, and
`restsOnUnverifiedRule` is true. The 5-day request therefore returns
`UNVERIFIED` today, with a reason naming the unconfirmed increment rule. It
flips to `DENY` only after a human marks `MIN_INCREMENT_DAYS` as VERIFIED
against a confirmed source line. This is the feature, not a gap. The system
distinguishes confirmed policy from asserted policy on the face of the output.

## Confidence

Cap and window encoding: 0.9. Increment and proximity rules as written: 0.55,
source line unverified. Contract design: 0.82.
