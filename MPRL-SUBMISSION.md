# MPRL submission draft - Authority Currency

Date: 2026-11-24. Status: **DRAFT. Not submitted.**
Solicitation: MARADMIN 540/26, Manpower Priority Research List (MPRL), due to
MP no later than 1 December 2026. Joint submission with MARFOREUR/AF.

This file holds the working reasoning. The submission itself is a .docx
filled on the MPRL Template supplied by the owner on 2026-11-24, at the length
of MP's fictional example. **The .docx is not kept in this repository and must
not be added to it:** the template carries the document property
`DISTRIBUTION: DoW COMMUNITY ONLY` and its author metadata names a person.
Same rule as constraint 2 for `canonical/`: limited-distribution material and
personal details are never published. The template allows **1 to 3** research questions, so the draft's
four became three: the MARFOREUR/AF command-order case moved inside RQ1. The
text below is superseded where it differs from the .docx.

Advocate names, phone numbers, and email addresses do not go in this file,
in a commit, or in a PR comment. They go on the template only.

---

## Before it goes

| # | Item | Owner | State |
|---|---|---|---|
| 1 | Download the MPRL Template and the fictional example. Re-fit the text to the template's fields and the example's length. | owner | **done 2026-11-24** |
| 2 | Confirm whether MARFOREUR/AF received the ETMS2 tasker. If yes, the submission goes through the ETMS2 response tab (para 8.c), not email. If no, email to the MPP-11 inbox named in para 8.d. | MARFOREUR/AF | open |
| 3 | Name the MARFOREUR/AF topic advocate and fill Advocate Name, Email, Phone in the .docx. The template has one advocate slot. Para 9.c commits this person to nine months of student support. | MARFOREUR/AF | open |
| 4 | The unconfirmed command-relevance sentence is **not** in the .docx. MARFOREUR/AF adds its own relevance line to section 2 if it wants one. | MARFOREUR/AF | optional |
| 5 | The command-order sample now sits inside RQ1. It depends on MARFOREUR/AF releasing its own orders to a student. If release is unlikely, strike "and of a sample of MARFOREUR/AF command orders" from RQ1 and the matching sentence in section 4 before submission. | MARFOREUR/AF | open |
| 6 | File name, para 6.d: `MARFOREURAF_AuthorityCurrency_YYYYMMDD`, dated the day it is sent. | owner | open |

---

## 6.a.1 Topic title

Authority Currency in Marine Corps Manpower Policy: Measuring Stale Citations
and Reissuance Lag

## 6.a.2 Problem statement and relevance

Marine Corps manpower policy is a hierarchy. Statute, DoD instructions,
SECNAV instructions, Marine Corps orders, and MARADMINs each name the
authority they implement. When a higher authority is reissued or cancelled,
the issuances beneath it are not updated in step, and no office measures how
large or how old the resulting gap is. A Marine, an IPAC, or a unit
administrator applying a message which cites a superseded order is either
applying terms the Marine Corps no longer holds, or re-deriving the current
authority by hand.

A read-only machine pass over 17,507 Marine Corps issuances (policy-as-data
project, 15 September 2026) found:

- 5,169 of 21,198 parsed references name a superseded edition of the
  issuance they cite. 3,997 of these point at 1000-series orders and
  instructions, the manpower series.
- 887 MARADMINs held as in force cite an issuance the same corpus holds as
  cancelled.

These figures are unverified machine output. No person has confirmed them
against the issuing authority's copy, and the parser left 19,793 further
references unread. The true size of the problem is therefore unknown. That
unknown is the decision gap this topic closes.

Relevance. The result tells MP and proponent divisions where directive
maintenance effort returns the most, and whether manpower terms in force
(eligibility, duration, amount, deadline) differ from the authority they rest
on. **[MARFOREUR/AF to confirm]** For a geographically dispersed component
command with small administrative staffs, distant from the proponent, a stale
citation costs more to resolve, because the current authority has to be
reconstructed locally.

## 6.a.3 Research questions

1. On a sample verified against issuing-authority copies, what share of
   in-force Marine Corps manpower issuances cite a superseded or cancelled
   authority, and how accurate is automated detection of it?
2. What is the distribution of lag between the reissuance or cancellation of
   a DoD, DON, or Marine Corps manpower authority and the update or
   cancellation of the issuances citing it? Which series and proponents carry
   the longest lag?
3. In a sample of stale citations, how often does the superseded edition
   differ from the current edition in a term a Marine is entitled to or
   required to meet? This separates stale citations with consequence from
   clerical ones.
4. (Optional, MARFOREUR/AF case.) In command-level orders and policy letters
   provided by MARFOREUR/AF, what share cite superseded service authority, and
   how does the rate compare with the service level?

Scope for a nine-month thesis: RQ1 to RQ3 run on public issuances alone. RQ4
runs only if MARFOREUR/AF documents are released to the student by month 2.

## 6.a.4 Data considerations

- **Source.** Publicly released issuances: MARADMINs and MCOs from
  marines.mil, DoD issuances from the WHS directives site, SECNAV instructions
  from the DON issuances site. No personnel records are needed.
- **Starting dataset.** The policy-as-data citation graph and revision index:
  issuance identifiers, titles, in-force status, and each citation with the
  paragraph it was read from. Machine output, marked unverified. The student
  verifies a sample against the issuing-authority copy, and the issuing
  authority's copy governs throughout.
- **Known limits.** Coverage bias: about half of all references were not
  parsed, mostly prose references and forms outside the citation grammar.
  The in-force status comes from the corpus, not from a Marine Corps system
  of record.
- **Personally identifiable information.** Issuances carry point-of-contact
  names, phone numbers, and email addresses. The dataset is delivered with
  contact details masked. No PII is needed for any question.
- **Restricted material (para 9.b).** Seven records carrying a limited
  distribution statement are excluded and never read. RQ1 to RQ3 need no
  classified or controlled data. RQ4 depends on MARFOREUR/AF command
  documents, whose distribution MARFOREUR/AF determines; any controlled
  material is handled under NPS data-access requirements.
- **Human subjects.** None. No question involves surveying or observing
  people.

## 6.a.5 Topic advocate information

On the template only. Two advocates:

- **Primary, MARFOREUR/AF.** Submitting organization. Command relevance,
  command documents for RQ4, feedback on completed research.
- **Technical, policy-as-data.** Dataset, method of citation extraction,
  background material, and the project's recorded defects in that method.
