# Reference manifest / source backlog

Every external authority the corpus cites, and where it stands. Regenerate the
live encoded-vs-needed split from the authority graphs:

```bash
python3 tools/list_references.py
```

Acquisition is human-in-the-loop: the environment cannot fetch these from
marines.mil / DoD / GPO sites (network policy + 403s), and the project's
discipline forbids encoding text that cannot be confirmed against the source.

## Encoded (5)

| Identifier | Document |
|---|---|
| `/us/usc/10/701` | 10 U.S.C. 701, Entitlement and accumulation of leave — subsections (a) and (h) in full (the statutory basis of the parental-leave chain) |
| `/us/usc/10/1052` | 10 U.S.C. 1052, Adoption expenses — (a)–(g) in full (defines "qualified adoption agency") |
| `/us/dod/dtm/2023/23-001` | OSD DTM 23-001, Expansion of the MPLP — full |
| `/us/usmc/maradmin/2023/051` | MARADMIN 051/23, Expansion of the MC MPLP — full |
| `/us/usmc/maradmin/2023/129` | MARADMIN 129/23, Clarification to 051/23 — full |

The parental-leave chain is now anchored end to end:
`10 U.S.C. 701(h)` → `DTM 23-001` → `MARADMIN 051/23` (clarified by `129/23`).

## Received, queued for encoding (4)

Authentic text in hand; encoded next. The schema (v1.1/v1.2) already supports
their structures (enclosures, chapters, deep numbering).

| Identifier | Document | Note |
|---|---|---|
| `/us/usmc/mco/1050.3J` | MCO 1050.3J, Regulations for Leave, Liberty and Administrative Absence | 56 pp; enclosure with chapters |
| `/us/usmc/mco/5000.12F` | MCO 5000.12F CH-1, Parenthood and Pregnancy | 47 pp; enclosure with chapters/appendices |
| `/us/dod/dodi/1327.06` | DoDI 1327.06, Leave and Liberty Policy and Procedures (2009) | 76 pp; text extracted |
| `/us/usmc/maradmin/2022/523` | MARADMIN 523/22, RC Parental Leave changes | another MARADMIN; very deep numbering (to 6 levels) |

## Still needed (2)

| Identifier | Document | Why blocked |
|---|---|---|
| `/us/navy/asn-mra/2023/mplp-guidance` | ASN (M&RA) Memorandum, DON MPLP Guidance (17 Jan 2023), MARADMIN 051/23 ref (b) | The PDF provided is a **scanned image** with no text layer; cannot extract here. Please paste the text. |
| `/us/dod/dodd/5124.02` | DoD Directive 5124.02, USD(P&R) | Authority under which DTM 23-001 is issued; not yet provided. |
