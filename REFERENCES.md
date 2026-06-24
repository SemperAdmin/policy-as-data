# Reference manifest / source backlog

Every external authority the corpus cites, and where it stands. Regenerate the
live encoded-vs-needed split from the authority graphs:

```bash
python3 tools/list_references.py
```

Acquisition is human-in-the-loop: the environment cannot fetch these from
marines.mil / DoD / GPO sites (network policy + 403s), and the project's
discipline forbids encoding text that cannot be confirmed against the source.

## Encoded (11)

| Identifier | Document | Scope |
|---|---|---|
| `/us/usc/10/701` | 10 U.S.C. 701, Entitlement and accumulation of leave | subsections (a) and (h), full |
| `/us/usc/10/1052` | 10 U.S.C. 1052, Adoption expenses | (a)–(g), full |
| `/us/dod/dodd/5124.02` | DoD Directive 5124.02, USD(P&R) charter (authority for the DTM and DoDI) | **directive-level**: Purpose, Applicability, Definitions full; Responsibilities (Sec 4+) and enclosures not yet encoded |
| `/us/dod/dodi/1327.06` | DoDI 1327.06, Military Leave, Liberty, and Administrative Absence (current, Aug 7 2025; reissues the 2009 edition the corpus cites) | **instruction-level**: Purpose + full Section/paragraph structure; bodies not yet encoded. Parental leave at 3.11.c (ADPL) / 3.11.d (IDPL) |
| `/us/dod/dtm/2023/23-001` | OSD DTM 23-001, Expansion of the MPLP | full |
| `/us/navy/asn-mra/2023/mplp-guidance` | ASN (M&RA) Memorandum, DON Guidance for Expansion of the MPLP (17 Jan 2023) | full |
| `/us/usmc/maradmin/2023/051` | MARADMIN 051/23, Expansion of the MC MPLP | full |
| `/us/usmc/maradmin/2023/129` | MARADMIN 129/23, Clarification to 051/23 | full |
| `/us/usmc/maradmin/2022/523` | MARADMIN 523/22, RC Parental Leave changes | full (deepest numbering: 6 levels) |
| `/us/usmc/mco/5000.12F` | MCO 5000.12F CH-1, Parenthood and Pregnancy | **order-level**: CH-1 change order in full; policy Enclosure (2) (chapters + appendices A–D) not yet encoded |
| `/us/usmc/mco/1050.3J` | MCO 1050.3J, Leave, Liberty and Administrative Absence | **order-level**: front matter (Situation/Cancellation/Mission); Enclosure (1) regulations not yet encoded |

The parental-leave chain is anchored end to end:
`10 U.S.C. 701(h)` → `DTM 23-001` → `MARADMIN 051/23` (clarified by `129/23`).
Every document type is now represented: statute, DoD memorandum, Marine Corps
Order, and naval message (MARADMIN).

## Partially encoded — large policy bodies pending

The two Marine Corps Orders are encoded at the order level. Their substantive
policy enclosures are large and mostly tangential to parental leave (pregnancy /
PFT standards; general leave-and-liberty administration); the chapter bodies are
queued for fuller encoding if needed.

## Still needed (1)

| Identifier | Document | Issue |
|---|---|---|
| `/us/navy/asn-mra/2021/reserve-policy-board` | ASN (M&RA) memo, 26 Mar 2021 (523/22 ref c) | not yet provided |

Note: DoDI 1327.06 is encoded from the current (Aug 7, 2025) edition; the node
records that it reissues the June 16, 2009 edition cited by the 2023-era
documents. The deep section bodies (incl. 3.11.c ADPL / 3.11.d IDPL) are queued
for fuller encoding.

## Still needed (2)

| Identifier | Document | Why blocked |
|---|---|---|
| `/us/navy/asn-mra/2023/mplp-guidance` | ASN (M&RA) Memorandum, DON MPLP Guidance (17 Jan 2023), MARADMIN 051/23 ref (b) | The PDF provided is a **scanned image** with no text layer; cannot extract here. Please paste the text. |
| `/us/dod/dodd/5124.02` | DoD Directive 5124.02, USD(P&R) | Authority under which DTM 23-001 is issued; not yet provided. |
