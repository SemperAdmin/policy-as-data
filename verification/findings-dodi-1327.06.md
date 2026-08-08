# Source reading - DoWI 1327.06, for M0

Date: 2026-08-08. Read by: machine, from the PDF you supplied.
Edition read: **DoWI 1327.06, August 7, 2025, incorporating Change 1,
June 30, 2026.** 75 pages, full text extracted.

**This is not an attestation.** A machine read the PDF. Verification is a human
act and the ledger records a person. What follows is the evidence a verifier
needs in order to run `tools/attest.py` in minutes rather than hours.

---

## 1. The five findings, in order of consequence

### F1. DTM 23-001 is cancelled, and it sits in the parental-leave authority chain

Paragraph 1.3.a, verbatim:

> This issuance incorporates and cancels:
> ...
> (2) Directive-type Memorandum 23-001, "Expansion of the Military Parental
> Leave Program," January 4, 2023, as amended.

`data/maradmin-051-23.rules.json` carries this chain:

```
/us/usc/10/701  ->  /us/dod/dodi/1327.06  ->  /us/dod/dtm/2023/23-001
                ->  /us/dod/don/usmc/maradmin/2023/051
```

The chain routes **through a document that DoDI 1327.06 itself absorbed and
cancelled.** MARADMIN 051/23 implemented the DTM in January 2023; the DTM was
folded into the instruction in August 2025. The service message's live authority
is now the instruction directly, and the DTM link is historical.

`REFERENCES.md` records DTM 23-001 as encoded "full" with no cancellation.
Nothing in the corpus knows it is cancelled.

**This is the kind of finding S6 asks for** - a currency defect on a live
authority chain that nobody had on a list. Note honestly what produced it: a
human reading a source, not the reconciliation tool. The tool would have found
it only if the chain carried an encoded currency check, which is a candidate for
a later concept.

### F2. The issuance is styled DoW, not DoD

Cover page: **"DOW INSTRUCTION 1327.06"**. Originating Component: "Office of the
Under Secretary of War for Personnel and Readiness". Change 1 approved by "Sean
O'Keefe, Deputy Under Secretary of War for Personnel and Readiness". Every page
footer: `DoWI 1327.06, August 7, 2025 / Change 1, June 30, 2026`.

Paragraph 1.4.d gives the reason: **"Update reference and organizational titles
for currency."**

Two consequences, and I have made a decision on one and flagged the other.

- **Labels updated** to DoWI, because a label should say what the document says.
- **The identifier keeps `/us/dod/`.** `NAMESPACES.md` allocates that token, an
  allocated token is not reused, and the identifier is a machine name a reader
  never sees. Whether a `DOWI` doc_type is needed, and whether `/us/dow/` should
  ever be allocated, is **a register question for you**, not a silent rename.
  Note it also affects the `doc_type` enum in `schema/policy_document.schema.json`.

### F3. Change 1 exists and the corpus did not record it

The record carried "Effective August 7, 2025" only. Change 1 is effective
**June 30, 2026** and is administrative in scope, per paragraph 1.4:

> The changes to this issuance are administrative and:
> a. Update language to comply with Section 631 of Public Law (PL) 119-60.
> b. Authorize a Service member who meets a qualifying circumstance in
> Paragraph 3.11.c.(11) to use active duty parental leave (ADPL) during a 2-year
> period beginning after an event described in Paragraph 3.11.c.(1)(c) with
> approval from the first general officer/flag officer (GO/FO) in the member's
> chain of command.
> c. Incorporate language in accordance with the October 10, 2025 Secretary of
> War (SecWar) Memorandum.
> d. Update reference and organizational titles for currency.

Item b is a **2-year** ADPL window in a defined circumstance. It does not change
the 12-week maximum, but any evaluator that computes a forfeiture date must know
it exists.

### F4. The 12-week value is right. The citation was not.

The encoded citation was `/us/dod/dodi/1327.06/s3/3.11/c/adpl-entitlement`,
labelled "para 3.11.c (ADPL)". **Paragraph 3.11.c is the ADPL heading and states
no value.** The figure appears in four sub-paragraphs:

| Paragraph | Verbatim |
|---|---|
| 3.11.c.(3)(a) | "For the birth parent, 12 weeks of ADPL is authorized following a period of convalescence from childbirth." |
| **3.11.c.(3)(a)1** | **"Twelve weeks of ADPL is authorized during the 1-year period beginning after the child's date of birth."** |
| 3.11.c.(3)(b) | "For the non-birth parent, 12 weeks of ADPL is authorized during the 1-year period beginning after the child's date of birth." |
| 3.11.c.(4) | "Service members, including dual military couples, are each authorized 12 weeks of ADPL during the 1-year period beginning after a minor child is placed with the Service member for adoption or the date of the minor child's adoption..." |
| 3.11.c.(5) | "Service members, including dual military couples, are each authorized 12 weeks of ADPL during the 1-year period beginning after a minor child is placed with the Service member for long-term foster care..." |

Corrected to **3.11.c.(3)(a)1**, the sentence that states the number and the
period together.

This is why "the value is right" is not the same as "the record is right." Under
this project's discipline an edge names the paragraph it was read from, and the
old citation named a heading.

### F5. IDPL is not 12 weeks, and assuming it were would be wrong by a factor of 14

Paragraph 3.11.d.(3)(a): "Birth parent, 12 IDPL periods will be authorized
during the 1-year period".

Paragraph 3.11.d.(1)(c) defines the unit:

> IDPL will be taken in increments equivalent to a 4-hour inactive duty training
> period of which a maximum of two such increments may be taken per day. Each
> such 4-hour increment constitutes an IDPL period.

Twelve IDPL periods is **48 hours**. Twelve weeks of ADPL is 84 days. The two
entitlements share a number and nothing else.

Encoded as `IDPL_MAX_PERIODS`, unit `idpl_periods`, and deliberately carrying
**no concept**. Putting it under `PARENTAL_LEAVE_MAX_DURATION` would let the
units table be asked to bridge periods to days, and it would refuse - correctly,
but for the wrong reason. The right reason is that it is a different entitlement
for a different population.

---

## 2. What changed in the data

`data/dodi-1327.06.rules.json`, with a `corrections` entry recording all of it.
Status stays **UNVERIFIED** throughout: a machine read the PDF, and promotion is
yours.

| | Before | After |
|---|---|---|
| label | DoDI 1327.06 | DoWI 1327.06 |
| date | Effective August 7, 2025 | + Change 1 effective June 30, 2026 |
| originator | OUSD(P&R) | Office of the Under Secretary of War for P&R |
| rule id | CURRENT_DOD_PARENTAL_LEAVE_WEEKS | ADPL_MAX_WEEKS |
| citation | `.../s3/3.11/c/adpl-entitlement` | `.../s3/3.11/c/3/a/1` |
| rules | 1 | 2, IDPL added |

No attestation was invalidated, because this rule never had one.

---

## 3. What a verifier does now

Everything needed is above. The reading is confirming these against the PDF, not
finding them.

```
python tools/attest.py --assertion "/us/dod/dodi/1327.06#ADPL_MAX_WEEKS" --verifier V-001
```

Answer `v`, edition `DoWI 1327.06, August 7, 2025, Change 1 June 30, 2026`,
obtained `esd.whs.mil, PDF supplied 2026-08-08`, date today. Then a second
verifier repeats it, because a rule value consumed by an evaluator needs two
independent readings.

Do the same for the MARADMIN side:

```
python tools/attest.py --assertion "/us/dod/don/usmc/maradmin/2023/051#MAX_PARENTAL_LEAVE_DAYS" --verifier V-001
```

**When both sides reach two verifiers, `reconcile.py` prints your first real
cross-tier comparison.** Expected: `AGREE`, 12 weeks = 84 days at T1, 84 days at
T5. No code change required.

---

## 4. Follow-on work this reading created

| | Item | Where |
|---|---|---|
| 1 | Record DTM 23-001 as cancelled by DoWI 1327.06, and mark the MARADMIN 051/23 authority chain accordingly | `canonical/`, and it is a lineage change, so it is an owner action |
| 2 | Decide the DoW register question: a `DOWI` doc_type, and whether `/us/dow/` is ever allocated | `NAMESPACES.md`, `schema/policy_document.schema.json` |
| 3 | Encode the 2-year ADPL window from Change 1 para 1.4.b before any evaluator computes a forfeiture date | `data/dodi-1327.06.rules.json` |
| 4 | DTM 23-001, DTM 22-004, and DTM 23-003 are all cancelled by this issuance. Check whether the other two are in the corpus. | `REFERENCES.md` |
| 5 | Consider a `CANCELLED_BY` concept so the tool finds F1-class defects rather than a human having to | `config/rule_concepts.json` |

Item 5 is the interesting one. F1 was found by reading, which does not scale.
The reconciliation machinery could find it if currency were encoded as a
comparable fact.

---

## 5. Confidence

0.9 on everything quoted. Every passage above is verbatim from the PDF you
supplied, located by paragraph, and the arithmetic on IDPL is from the
issuance's own definition.

Lower on two points. Whether `/us/dod/dtm/2023/23-001` in your corpus is the
January 4, 2023 DTM the cancellation names was **not** cross-checked against the
canonical record; `REFERENCES.md` calls it "OSD DTM 23-001, Expansion of the
MPLP" which matches, but confirm before recording the cancellation. And whether
Change 1 alters anything in 3.11.d was **not** exhaustively checked - the
Summary of Change 1 does not mention IDPL, and I did not diff the base edition
against Change 1 paragraph by paragraph.
