# Decision brief - B1, B2, B3

Date: 2026-08-08. For: Stephen. Prepared by: the engineering side.
Companion to `POC-PLAN.md` section 11 and `ACTION-REGISTER.md` section 0.

Three decisions gate the POC. Each section states what turns on it, the options,
what each costs, and a recommendation you can accept or overrule. **Two of my
earlier recommendations change here**, and both changes are flagged.

---

# B1. May a finding publish a value drawn from an unverified rule?

## What is actually being decided

`tools/reconcile.py` will compare a value stated at one tier against the same
value stated at another. The question is what it **prints** when an input has not
been human-verified.

This is not abstract. Today the two live inputs are:

| Tier | Value | State | Its own note says |
|---|---|---|---|
| DoDI 1327.06, para 3.11.c | 12 weeks | UNVERIFIED | "the section body is not yet encoded, so the exact value and source line are not yet confirmed against the issuance text" |
| MARADMIN 051/23, para 11.d | 84 days | QUORUM_SHORT | verbatim 84-day enforcement language, confirmed 2026-06-24 |

12 weeks is 84 days. They agree. **Nobody has confirmed the DoD number against
the DoD document.**

## Option A - print it, with a downgrade banner

What `tools/evaluate.py` does today. Output would read roughly:

```
PARENTAL_LEAVE_MAX_DURATION
  DoD    12 weeks (84 days)   [UNVERIFIED]   DoDI 1327.06 para 3.11.c
  USMC   84 days              [QUORUM_SHORT] MARADMIN 051/23 para 11.d
  VERDICT AGREE  -  confidence DOWNGRADED, unverified input
```

**For.** Maximum information. One convention across both tools. The reader sees
the comparison and can weigh it.

**Against.** The banner is the first thing lost. The number gets screenshotted,
pasted into an email, quoted in a brief, read aloud in a brief-back - and every
one of those strips "[UNVERIFIED]". What survives is "DoD says 12 weeks," which
nobody has checked, about a Marine's leave entitlement.

## Option B - withhold the value, report the structure

```
PARENTAL_LEAVE_MAX_DURATION
  DoD    value present at DoDI 1327.06 para 3.11.c, NOT VERIFIED - withheld
  USMC   84 days              [QUORUM_SHORT] MARADMIN 051/23 para 11.d
  VERDICT NOT_COMPARABLE  -  unverified input at the DoD tier
```

**For.** Nothing quotable is unchecked. The finding is still a finding: "the DoD
tier holds a value nobody has confirmed" is exactly the sort of thing this
project exists to surface. It also creates pressure to verify, because the only
way to get a comparison is to do the reading.

**Against.** Less informative. It withholds a real agreement. A reviewer may
read it as the tool being coy about something it knows.

## Correction to what I told you earlier

I said "refuse for values, downgrade for structure," as though there were a
middle path. **There is not, and I was being imprecise.** If the tool computes
`AGREE` from an unverified value, it has published a conclusion derived from
that value, which carries the same exposure one level up and is worse, because a
verdict travels even more easily than a number. Any coherent version of
"withhold" makes the verdict `NOT_COMPARABLE`. So the real choice is A or B.

## Recommendation: B

The asymmetry decides it. A wrong published number about an entitlement is
expensive and hard to retract. A withheld comparison costs one reading. And the
whole claim of this project is that its provenance can be trusted - a tool that
publishes unchecked numbers with a disclaimer is trading that claim for
convenience.

## What B costs you, stated plainly

**With today's data, `reconcile.py` produces zero AGREE findings.** The one live
example becomes `NOT_COMPARABLE` until the DoD value is verified. You would be
demonstrating a tool that says "I cannot compare these yet."

That is survivable and arguably good - it makes M0 unavoidable rather than
optional - but do not be surprised by it, and do not let anyone else be. If you
need an AGREE for a demonstration before M0 completes, say so now and we design
the demonstration around a concept where both tiers are verifiable, rather than
weakening the rule to get a nicer screenshot.

---

# B2. Which second spine for the generality test?

## What is actually being decided

M5 reconciles a second spine to test whether the design was shaped around leave.
Reconciliation needs at least two tiers holding a value for the same concept, so
tier reach matters - but so does whether the documents contain numbers at all.

## The five spines, measured

From `SESSION_HANDOFF.md` section 3. Tier ladder: T0 statute, T1 DoD, T2 DON,
T3 service directive, T4 service manual, T5 message.

| Spine | Seed | Tiers reached | Edges | T0 | T1 |
|---|---|---|---|---|---|
| leave | MARADMIN-2023-129 | T0 T1 T3 T5 | 46 | yes | yes |
| **promotion** | MCO-1400.31D | T0 T1 T3 | 36 | **yes** | **yes** |
| mos | MARADMIN-2026-221 | T0 T3 T4 T5 | 50 | yes | **no** |
| **fitness** | MARADMIN-2021-404 | T1 T3 T5 | 43 | no | **yes** |
| pes | MARADMIN-2026-073 | T1 T3 T5 | 119 | no | yes |

## The case for promotion

Reaches statute and DoD. Documents: MCO 1400.31D, MCO 1400.32D CH-1 and CH-2,
SECNAVINST 1400.1D, 10 U.S.C. 574. Numeric rules exist - time in grade, time in
service, selection zones, board composition.

Strongest structural proof available: a full T0 to T3 ladder in a second subject
area.

## The case for fitness

Documents: DoDI 1308.03, DoDI 1308.3, MCO 6100.13A CH-5, MCO 6100.14,
MCO 6110.3A CH-4, MARADMIN 2021-404.

Three reasons it may be the better test.

1. **It is where the numbers are.** Body composition standards, PFT and CFT
   minimums by age and sex, weight and circumference tables. Reconciliation
   compares values, and this spine is dense with them. Promotion's rules are
   more often conditions than scalars.
2. **It carries a known authority defect.** Three current MCOs cite DoDI 1308.3,
   **cancelled March 2022**. The current edition is DoDI 1308.03. Comparing what
   the cancelled edition said against what the current one says against what the
   MCO implements is precisely the divergence this tool is built to find, and
   the setup already exists in the corpus.
3. **It is a different shape.** Fitness reaches no statute tier. That forces
   `NOT_HELD` to be a first-class result rather than an edge case, which is a
   harder and more useful generality test than repeating a ladder leave already
   proved.

## Correction to what I told you earlier

I recommended promotion, and I picked it on **tier reach alone** - it touches
T0, so I called it the stronger proof. Having looked at what is actually in each
spine's documents, that reasoning was thin. Leave already proves the T0-to-T5
ladder. Doing promotion largely re-proves it.

## Recommendation: fitness

Because **S6 is the criterion that decides the POC** - at least one DIVERGE or
NOT_HELD finding nobody had beforehand - and fitness is where a real divergence
is most likely to exist. Keep promotion as the third spine if M5 succeeds.

One caution, and it is real: the cancelled-DoDI finding is **already known** and
recorded in your headline findings. Re-deriving it does not satisfy S6. What
would satisfy S6 is a **value-level** divergence - a standard the MCO implements
differently from the DoD instruction it cites. That is unknown territory, which
is the point.

---

# B3. Can you obtain DoDI 1327.06 para 3.11.c and 3.11.d?

## What is actually being decided

Whether M0 - the POC's critical path - can start.

## Exactly what is needed

The text of two paragraphs from **DoDI 1327.06, Military Leave, Liberty, and
Administrative Absence**, current edition effective 7 August 2025:

- **3.11.c** - Active Duty Parental Leave (ADPL)
- **3.11.d** - Inactive Duty Parental Leave (IDPL)

Verbatim. Paragraph numbering intact. Enough surrounding context to confirm the
paragraph reference is right.

## Why it is the critical path

`data/dodi-1327.06.rules.json` holds one rule, `CURRENT_DOD_PARENTAL_LEAVE_WEEKS`
= 12 weeks, status UNVERIFIED, and its own note says the section body is not
encoded so the value and the source line are not confirmed. Under B1 option B,
that means no comparison happens at all until this is read. Everything in
Track 1 from 1.1 onward sits behind it.

## Why it is not simply a download

`REFERENCES.md` records that this environment cannot fetch marines.mil, DoD, or
GPO sites - network policy plus 403s - and that acquisition is human-in-the-loop
by design. Two documents are already blocked for related reasons, one because
the PDF is a scanned image with no text layer.

Practically: open the current DoDI 1327.06 in a browser, find section 3.11, copy
paragraphs c and d, paste them into a message here. If the PDF has a text layer
this is minutes.

## The three answers, and what each triggers

**Yes, and it is clean text.** M0 proceeds. Encode both paragraphs, attest the
value against them, and Track 1 starts. Best case.

**Yes, but it is a scanned image.** Same class as the blocked ASN memorandum.
OCR belongs to GunnyBot, not here, per `resources/19`. Either transcribe two
paragraphs by hand - two paragraphs is a coffee, not a project - or treat it as
a no.

**No.** Then the concept changes, and the answer ties to B2. The only other
place in the corpus with two tiers holding comparable values is the **fitness**
spine: DoDI 1308.03 at the DoD tier and MCO 6110.3A CH-4 at the service tier,
both already in `canonical/`, both dense with numeric standards. Fitness becomes
the **first** spine rather than the second, and leave becomes the generality
test. Nothing else in the plan changes.

## Recommendation

Try for it, and time-box it. If you cannot have those two paragraphs in front of
you within a day, switch to fitness-first rather than letting Track 1 sit. The
POC does not depend on parental leave; it depends on any concept stated at two
tiers where both statements can be read.

---

# Decision record - fill and return

```
B1  publish unverified values?
    [ ] A  print with downgrade banner
    [ ] B  withhold value, verdict NOT_COMPARABLE          (recommended)
    reason:

B2  second spine
    [ ] fitness       numeric density, known authority defect   (recommended)
    [ ] promotion     full T0-T3 ladder
    [ ] other:
    reason:

B3  DoDI 1327.06 para 3.11.c / 3.11.d
    [ ] yes, text attached
    [ ] yes, but scanned - will transcribe
    [ ] no  -> switch to fitness-first, leave becomes the generality test
    reason:

Also outstanding, from ACTION-REGISTER 2.6:
    seed attribution
    [ ] leave as imported, verifier null - attest all five properly
    [ ] re-seed with --verifier V-000, needing one independent second each
```

---

# Confidence

0.85. Spine tiers, edge counts, seeds, and the cancelled-DoDI finding are quoted
from `SESSION_HANDOFF.md`. The two rule values and their statuses were read from
`data/*.rules.json`. The document lists come from `canonical/`.

Lower on one point: the claim that the fitness documents are numerically dense
is inferred from what body composition and physical fitness orders normally
contain, **not** from reading MCO 6110.3A CH-4's provisions in this pass. If B2
turns on that, it is worth ten minutes of checking before you commit - and if it
turns out to be thin, promotion is the fallback and the reasoning above reverses
cleanly.
