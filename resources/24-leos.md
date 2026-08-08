# 24. LEOS, Legislation Editing Open Software - EVALUATE, do not adopt yet

Sources:
<https://interoperable-europe.ec.europa.eu/eu-oss-catalogue/solutions/leos-core-0>,
<https://github.com/MinBZK/leos> (a Ministry of the Interior fork; upstream is at
code.europa.eu). Retrieved 2026-08-08. Publisher: European Commission, DG DIGIT.

## What it is, confirmed

| | |
|---|---|
| Purpose | "an open source software designed to help those involved in drafting legislation," with online collaborative editing, version control, and co-editing |
| Version | 5.4.2, released 2026-07-10 |
| Development status | Stable |
| Licence | **EUPL-1.2** |
| Format | XML, **Akoma Ntoso V3**, an OASIS LegalDocML standard, in the **AKN4EU** interinstitutional instantiation |
| Platform | web application, containerized. Docker Compose and Kubernetes manifests present |
| Maintainer | European Commission DIGIT LEOS team |

This is not a research prototype. It is a stable, actively released, EU
institutional product, and it is the working implementation of the
Digital-Ready Policymaking thesis reviewed in `resources/18`. Its existence is
useful independent evidence that the direction this project is taking is
correct.

Caution on the fork read: the MinBZK repository describes itself as "a Proof of
concept version" and states "This version is not meant for production." That is
the fork's status, not the upstream product's. Do not cite the fork's disclaimer
as a statement about LEOS.

## The question actually being asked

Not "which drafting tool is better." The real discriminator:

**Must the drafting tool produce Marine Corps naval correspondence under MCO
5215.1K - Situation, Mission, Execution, Cancellation, references, enclosures?**

If yes, SemperScribe already knows that format and LEOS does not. LEOS models EU
legislative instruments in AKN4EU: proposals, directives, regulations, recitals,
articles. A Marine Corps Order is not one of those, and neither is a MARADMIN.
Teaching LEOS the naval-correspondence structure means forking an EUPL-licensed
containerized web application and maintaining that fork. Adding structured
export to SemperScribe is a smaller job by a wide margin.

**They are not competitors at the same layer.** LEOS is a drafting platform with
a legal-document model. SemperScribe is a naval-correspondence authoring tool.
The overlap is that both can, in principle, emit structured XML.

## Three findings that decide it

**1. The licence conflicts with the destination, in one direction.**

EUPL-1.2 is copyleft. Running LEOS unmodified as a separate application
alongside this repository raises no issue. **Modifying it and distributing the
result does**, and a USMC-specific LEOS is a modification by definition. That
derivative would be EUPL, which cannot then sit inside a repository targeting
the 17 U.S.C. 105 public-domain position recorded in `resources/20` - and that
repository still ships no `LICENSE` at all. `REUSE-ASSESSMENT.md` section 6 gate
1 fails today for anything, and gate 1 is where this stops.

Note the boundary precisely: this is an argument against **forking LEOS into
this project**, not against **using LEOS as a separate system**. Those are
different decisions with different answers.

**2. It fails the standalone gate, and that is by design rather than by defect.**

`README.md` requires `./build.sh` to succeed on a fresh clone with nothing else
present. LEOS is a containerized web application with Docker Compose and
Kubernetes manifests. That is a correct architecture for a collaborative
drafting platform and an infrastructure commitment this project has deliberately
avoided. `REUSE-ASSESSMENT.md` gate 2 and gate 3 both fail.

**3. Akoma Ntoso output would be an improvement over an unknown NLDP.**

This is the argument **for** LEOS and it is a real one.
`INTEGRATION-SEMPERSCRIBE.md` section 5 requirement R2 is that the export carry
structured provisions with native designators, and states that the integration
is not worth building if R2 fails. **AKN satisfies R2 by construction.** An
AKN-emitting drafting tool removes the largest unknown in that design.

It also converts the interface from a proprietary format to an OASIS standard,
which is exactly what `REUSE-ASSESSMENT.md` section 1 says to reuse
aggressively. The cost is an AKN-to-`usmc-issuance-2.0` converter, and that is a
bounded, well-specified piece of work against a documented schema - a far better
position than mapping an undocumented NLDP.

## Recommendation

**Keep SemperScribe. Require structured export. Evaluate LEOS only if
SemperScribe cannot deliver it.**

The decision tree, in order:

1. **Ask whether SemperScribe meets R2.** One conversation. If yes, build the
   Option A bridge and this question closes.
2. **If SemperScribe cannot meet R2**, you need a drafting tool that can, and
   LEOS is the best-evidenced candidate in existence. At that point evaluate it
   properly: as a **separate system** emitting AKN, never as a fork inside this
   repository.
3. **Either way, adopt the interface idea now.** Whatever the drafting tool,
   require the export to be structured XML with native designators. Prefer AKN
   over a private format if the tool can produce it, because a standard
   interface survives a change of tool and a private one does not.

**What to take from LEOS regardless of the decision:** its document model is
worth reading before the NLDP contract in `INTEGRATION-SEMPERSCRIBE.md` section
5 is finalized. It is a mature answer to the same question, and AKN4EU shows how
a jurisdiction extends AKN for its own instruments - which is structurally the
same move this project made extending USLM conventions for service issuances.

## Verdict

**EVALUATE, do not adopt yet.** Not a drop-in replacement for SemperScribe,
because it does not model naval correspondence. Not a component of this
repository, because EUPL and containerized deployment fail two reuse gates. A
serious candidate as a separate drafting system if and only if SemperScribe
cannot produce structured output, and a valuable design reference in every case.

## Confidence

0.8. Version, licence, status, format, maintainer, and platform were retrieved
from the catalogue entry and the repository. The AKN4EU and MCO 5215.1K
structural mismatch is a reasoned conclusion from both models rather than a
quoted statement, and is marked as such. LEOS's full technical prerequisites -
language, framework, repository backend - were **not confirmed**; the fork
exposes only Dockerfiles and shell, and the upstream at code.europa.eu was not
retrieved. Confirm before any evaluation proceeds past step 1.
