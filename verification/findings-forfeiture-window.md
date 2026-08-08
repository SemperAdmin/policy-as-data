# Finding - the forfeiture window is encoded as a number the source does not state

Date: 2026-08-08. Raised by: `tools/reconcile.py`, via a refused unit conversion.
Severity: **a computed date given to a Marine can be one day early.**
Status: **OPEN. Owner decision required.** Nothing was changed.

---

## The finding

Both tiers state the forfeiture window as **one year**. The corpus records it as
**365 days**.

| | Text | Encoded |
|---|---|---|
| DoWI 1327.06 para 3.11.c.(10)(c) | "ADPL that is not taken before the expiration of **1 year** from the date of a child's birth, minor child's adoption... will be forfeited" | `ADPL_FORFEITURE_WINDOW_YEARS` = 1 **years** |
| MARADMIN 051/23 para 8.c.(3) | "Parental leave not executed before the expiration of **1 year** from the date of the qualifying event is forfeited" | `ENTITLEMENT_WINDOW_DAYS` = 365 **days** |

**365 is not in either issuance.** It is an arithmetic step taken during
encoding and then presented as a cited value. Under this project's own rule -
a cited value is what the paragraph says, and anything else is inferred - it
should never have been recorded as a citation to para 8.c.(3).

## How it surfaced

Not by anyone reading it. `config/units.json` refuses to convert years, with
this reason written when the table was built:

> No fixed day count. The one-year forfeiture period in MARADMIN 051/23 para
> 8.c.(3) is already encoded as 365 days by the source's own arithmetic.
> Converting elsewhere would invite a leap-year error nobody would catch.

When the DoD counterpart was encoded in the unit the source actually uses,
reconciliation returned `NOT_COMPARABLE` and named the refusal. The refusal was
correct and the reason it gave turned out to be the defect itself.

## The consequence, measured

`tools/evaluate.py` computes the forfeiture date as
`governing_event + timedelta(days=WINDOW["value"])`, with the value 365.

```
event 2027-03-01   +365d = 2028-02-29   "1 year from" = 2028-03-01   ONE DAY EARLY
event 2023-01-01   +365d = 2024-01-01   "1 year from" = 2024-01-01   correct
event 2027-02-28   +365d = 2028-02-28   "1 year from" = 2028-02-28   correct
```

Any qualifying event falling on or after 1 March in the year before a leap year,
or on or before 29 February of a leap year, produces a date one day early.

**732 of 2,922 qualifying-event dates across 2024 to 2031 - 25%.** In 2027,
306 of 365 dates are affected. The engine would tell a Marine their parental
leave expires a day before it does, on a quarter of all possible event dates.

The error direction matters: it is always **early**, never late. It shortens the
entitlement rather than extending it.

## Why this is the POC's proof

`POC-PLAN.md` success criterion S6: *at least one DIVERGE or NOT_HELD finding
that was not on anyone's list beforehand. If this is zero, the concept is not
proven.*

This was not on anyone's list. It was produced by encoding a value in the unit
its source uses and letting an explicit conversion table refuse to guess. A
search index over PDFs cannot find it. A human reading either issuance would not
find it, because **neither issuance is wrong** - the defect is in the encoding
between them, which is precisely the layer this project exists to make visible.

## What was NOT done

The MARADMIN value was not changed. It carries an attestation, and altering it
would invalidate a human's reading without that human's involvement - which is
the whole thing the ledger exists to prevent. This is a report, not a repair.

## Options

**1. Encode both tiers in years, teach the evaluator calendar arithmetic.**
Correct. `ENTITLEMENT_WINDOW_DAYS` becomes `..._YEARS` = 1, and `evaluate.py`
uses a date-shift rather than a day-count. Costs an attestation - the value
changes, so the existing reading invalidates and must be redone. That is the
system working.

**2. Keep 365 and label it an approximation.** Cheapest, and dishonest in the
one place this project cannot afford to be. It would also leave the evaluator
producing wrong dates.

**3. Encode both, mark the day-count as derived.** Keeps the fast path, records
that 365 is inferred rather than cited. Middle ground, and it still leaves
`evaluate.py` computing the wrong date unless it is taught to prefer the
years-based value.

**Recommendation: option 1.** The entitlement is a date a Marine plans around.
An off-by-one that is always early, on a quarter of event dates, is not an
acceptable rounding.

## Follow-on

- `evaluate.py` uses `ENTITLEMENT_WINDOW_DAYS` in exactly one place; the change
  is small.
- Check whether any other rule in the corpus records a converted number where
  the source states a period. This is the first place to look for a second
  instance.
- Consider a `derived: true` flag on any rule value that is not verbatim from
  its cited paragraph, so this class is visible without a reconciliation run.

## Confidence

0.95. Both quotations are verbatim from the issuances. The arithmetic was
computed rather than reasoned, and the 25% figure is an exhaustive count over
2024-2031 rather than an estimate. The `evaluate.py` line was read.

The one thing not established: whether MARADMIN 051/23's own text anywhere
states a day count for the forfeiture window, which would make 365 a quotation
after all. The encoded note quotes only "1 year". **Check para 8.c.(3) in the
message before adopting any option.**
