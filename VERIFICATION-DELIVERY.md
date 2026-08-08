# Where verification runs

Date: 2026-08-08. Owner: Stephen. Status: options, one blocking question.
Companion to `VERIFICATION-DESIGN.md`, which covers the act. This covers the
delivery of the act.

---

## 1. Agreed, and the CLI is not the part that is wrong

A CLI on one laptop is not a process. It is a person with a script, and it does
not survive that person. For actual use you need a queue, an identity, and an
audit trail somebody other than the operator can inspect.

But separate the engine from the interface, because only one of them is the
problem.

| Layer | What it does | Move it? |
|---|---|---|
| **Rules** | normalization, hashing, quorum, verdicts | **no.** `normalize.py` and `verify_status.py` are the standard. Reimplementing them in TypeScript is the multiple-implementations defect that has already bitten this programme three times today. |
| **Store** | the append-only ledger | maybe. The format is JSONL and portable. |
| **Interface** | present the assertion, capture the answer | **yes. This is the real request.** |
| **Identity** | who the verifier is | **yes, and it is the hard part.** |

The CLI stays as the engine and the validator. What changes is what sits in
front of it.

## 2. Identity is what actually decides this

An attestation that does not name a person is worth nothing. `attest.py` takes
`--verifier V-001` on trust, which is honest for one operator on one machine and
collapses the moment two people share a tool.

So "in the app" is really "with authenticated identity," and that is an
infrastructure question, not a UI question. Note what both current apps say
about themselves: SemperScribe is local-first with no backend, no telemetry, and
no Authority to Operate. policy-as-data is a static site on GitHub Pages and
cloud.gov. **Neither can authenticate anyone today**, and adding that is not a
feature, it is a different system with a different approval path.

## 3. Four ways to deliver it

### A. Static verification queue, local write

The build renders a page listing every pending assertion with its claim,
citation, source link, and status. The verifier reads it in a browser and still
runs the CLI to record.

- **Cost:** one renderer. No backend, no auth, no architecture change.
- **Gets you:** visibility, a shareable worklist, source links one click away.
- **Does not get you:** identity, or a write path off the operator's machine.

### B. Browser captures, user commits the file

A page in the app presents the assertion and produces an attestation JSON the
user downloads and drops into `verification/incoming/`. The build validates and
appends.

- **Cost:** one page, one ingest step. No backend.
- **Gets you:** a real interface, usable by someone who will never open a
  terminal.
- **Does not get you:** authenticated identity. The verifier still types who
  they are.
- **Precedent:** this is exactly SemperScribe's NLDP export and the Release gate
  in `SEMPERSCRIBE-HANDOFF.md`. Same pattern, same constraints, already agreed.

### C. Git as the system of record

The verifier opens a pull request adding one line to the ledger. GitHub identity
is the verifier identity. Review by a second person is the second attestation. A
workflow runs `verify_status.py --fail-on-invalidated` as a required check.

- **Cost:** a workflow file. `.github/workflows/validate.yml` already exists.
- **Gets you:** authenticated identity, immutable audit, two-person review,
  append-only, and a queue, with **no new infrastructure at all**.
- **Does not get you:** a non-technical user. It requires a GitHub account and
  a tolerable PR flow.
- **This is the strongest answer available today** for a small team, and it is
  the one most people miss.

### D. Real backend

Authentication, server-side ledger, roles, queue, notifications.

**Correction, 2026-08-08.** I first costed this as "a database, hosting, an
identity provider, and an ATO conversation," as though all four were greenfield.
That is wrong for your situation, and the deployment files say so.

`docs/manifest.yml` pushes `policy-as-data` with the `staticfile_buildpack`,
64 MB, one instance, `force_https: true`. Purely static, so your reading is
right - there is no backend today. But `deploy_cloudgov.bat` authenticates
against `login.fr.cloud.gov/passcode` and its own error path notes that
cloud.gov "requires a government email address" and that a commercial address
cannot self-register. **You are already operating inside a FedRAMP-authorized
platform with a government identity gate on it.**

What that changes:

| Assumed cost | Actual |
|---|---|
| hosting | already yours. Changing `buildpacks:` from `staticfile_buildpack` to a Python buildpack is a manifest edit. |
| ATO | cloud.gov is FedRAMP-Authorized at Moderate, package F1607067912. Roughly 155 of 323 Rev 5 controls are platform-owned and another 98 shared, so about 253 are inherited or partly inherited. You still own the rest, and your Authorizing Official still has to say yes. |
| database | cloud.gov brokers services. Whether the brokered database and identity offerings sit inside the authorization boundary is **UNCONFIRMED** - the platform's own ATO-process page does not say, and I did not verify it. Confirm before designing on it. |
| identity | cloud.gov's own login already gates deployment. Whether an application can use it to authenticate *end users* is a different question and is **UNCONFIRMED**. |

- **Gets you:** everything.
- **Still production, not a POC**, and B or C migrate into it cleanly because
  the ledger format does not change.

### The threshold is not technical

The reason to go slowly here is not the buildpack. It is this:

**A server-side ledger turns the verifier roster into government-held personal
data.** Today `verification/roster.json` is one gitignored file on one machine,
which is exactly why it was designed that way. Move attestation into a hosted
app and you are storing who attested to what, when, against which document, in a
system that - by both apps' own written statements - carries no Authority to
Operate.

That is the threshold. Not the database, not the buildpack. Cross it
deliberately, with the ATO conversation already had, or not at all.

## 4. Recommendation

**Now: A.** One renderer, no architecture change, and it delivers the half of
your request that costs nothing - a verifier can see the queue, read the claim,
and click through to the source without a terminal. It is P1 in
`ACTION-REGISTER.md` already, as item 2.9.

**For actual use: C, unless your verifiers are not git users.** It is the only
option that gets authenticated identity without new infrastructure, and the
identity problem is the one that decides whether an attestation means anything.
Two-person quorum comes free as PR review, which would also let the deviation in
`config/verification_policy.json` be retired honestly.

**If the verifiers are S-1 clerks rather than engineers: B.** Same pattern as
SemperScribe's release gate, so the programme carries one convention instead of
two.

**D is closer than I first said, and the gate is the data question, not the
tech.** Being on cloud.gov already means the platform, the transport, and most
of the control inheritance are solved. What is not solved is holding verifier
identity in a hosted system without an ATO. Settle that first; the engineering
after it is small.

One thing worth noticing while you decide: the act that is already
authenticated in your pipeline is the **deploy**, not the verification.
`deploy_cloudgov.bat` makes you sign in with a government email before anything
reaches cloud.gov. That is weaker than authenticating the verifier - a deployer
is not a reader - but it means the published site is already the output of an
identified person, which is more than most static sites can say.

## 5. What does not change under any option

- `normalize.py` stays the only implementation of the hash rule.
- `verify_status.py` stays the only implementation of quorum and verdicts.
- The ledger stays append-only JSONL, and superseding never erases.
- An attestation still binds to a content hash, so a value that changes still
  invalidates the reading.
- `canonical/` and `data/` are still never written by a verification tool.

Any interface that reimplements one of those is wrong, regardless of how good it
looks. That is the lesson from the SemperScribe exporter and from my own three
tools disagreeing about quorum this afternoon.

## 6. Blocking question

**Who are the verifiers, and what will they actually use?**

- A small technical team with GitHub accounts, then **C**.
- Marines at a desk with no accounts and no terminal, then **B**.
- Only you, for now, then **A** and revisit when a second person exists.

The answer decides the design, and nothing should be built until it is
answered. It also decides whether the quorum deviation is temporary or
structural.

## 7. Scope

This is **P3** in `POC-PLAN.md` terms - "any API, service, database, or
authenticated surface" is named as out of scope, and that still holds. Option A
is the exception, because it is a renderer and not a service.

Building an authenticated verification app before the reconciliation POC has
produced a single finding would be the clearest possible case of the P2/P3 creep
the plan exists to stop.

## 8. Confidence

0.85 on the options. The constraints are quoted from `README.md`, SemperScribe's
README, `POC-PLAN.md`, `docs/manifest.yml`, and `deploy_cloudgov.bat`. The
cloud.gov control-inheritance figures are quoted from the platform's own
ATO-process documentation.

0.6 on the option D costing, and the two UNCONFIRMED rows above are why. Whether
cloud.gov's brokered database and identity services fall inside the FedRAMP
authorization boundary was not established, and it is the fact that decides
whether option D is a manifest change or a procurement. Confirm with cloud.gov
support before any design work.
