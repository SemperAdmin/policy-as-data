# Reference manifest / source backlog

Every external authority the corpus cites, and whether it is encoded yet. This
is the acquisition backlog: the `NEED` rows are documents whose authentic text
would let us encode them and deepen provenance.

Regenerate the live list from the authority graphs:

```bash
python3 tools/list_references.py
```

Why this exists: the environment cannot fetch these from marines.mil / DoD sites
(network policy + 403s), and the project's discipline forbids encoding text we
cannot confirm against the source. So acquisition is a human-in-the-loop step.

## Encoded (3)

| Identifier | Document |
|---|---|
| `/us/usmc/maradmin/2023/051` | MARADMIN 051/23, Expansion of the MC Military Parental Leave Program — full |
| `/us/usmc/maradmin/2023/129` | MARADMIN 129/23, Clarification to MARADMIN 051/23 — full |
| `/us/dod/dtm/2023/23-001` | OSD DTM 23-001, Expansion of the MPLP — full (the DoD authority 051/23 implements) |

## Received, queued for encoding (2)

Source text in hand; large documents, encoded next. The schema (v1.1) now
supports their structure (enclosures, chapters, From/To/Ref/Encl headers).

| Identifier | Document |
|---|---|
| `/us/usmc/mco/1050.3J` | MCO 1050.3J, Regulations for Leave, Liberty and Administrative Absence (56 pp) |
| `/us/usmc/mco/5000.12F` | MCO 5000.12F CH-1, Marine Corps Policy Concerning Parenthood and Pregnancy (47 pp) |

## Need source text (8)

Ordered by how much each unlocks. Paste the verbatim body of any of these (the
way you did 051/23 and 129/23) and I will encode it to the schema and validate.

| # | Identifier | Document | Why it matters |
|---|---|---|---|
| 1 | `/us/usmc/mco/1050.3J` | **MCO 1050.3J**, Regulations for Leave, Liberty and Administrative Absence | Standing USMC leave order (ref d). A different document *type* than a MARADMIN — the best stress-test of whether the schema generalizes. |
| 2 | `/us/usmc/mco/5000.12F` | **MCO 5000.12F CH-1**, Marine Corps Policy Concerning Parenthood and Pregnancy | Standing order (ref c); 051/23 points into "enclosure (1), chapter 2, paragraph 16" of it — tests enclosures/chapters in the schema. |
| 3 | `/us/osd/dtm/2023/expansion-mplp` | **OSD/USD(P&R) Directive-Type Memorandum**, Expansion of the MPLP (4 Jan 2023) | Ref (a); the DoD authority 051/23 derives from. Closes the cited authority chain above the Marine Corps. |
| 4 | `/us/navy/asn-mra/2023/mplp-guidance` | **ASN (M&RA) Memorandum**, DON Guidance for Expansion of the MPLP (17 Jan 2023) | Ref (b); the Navy-level authority. |
| 5 | `/us/dod/dodi/1327.06` | **DoDI 1327.06**, Leave and Liberty Policy and Procedures | The standing DoD instruction. Currently the DTM→DoDI link is `inferredAuthorityFrom`; the real text would let us confirm or correct it. |
| 6 | `/us/usc/10/701` | **10 U.S.C. 701**, Entitlement to leave | The statute at the top. Available as USLM XML from the GPO bulk-data repository — if you can drop the section text, it anchors the chain in real statute. |
| 7 | `/us/usc/10/1052` | **10 U.S.C. 1052** (qualified adoption agency) | Cited in 051/23 para 6.c. Not yet a graph node; add when its text is available. |
| 8 | `/us/usmc/maradmin/2022/523` | **MARADMIN 523/22**, Forthcoming Changes to Reserve Component Parental Leave Policy | Ref (e); related MARADMIN. Lower priority. |

## Located sources (fetch is blocked here — paste needed)

Searched for each. The environment can find these URLs but cannot retrieve their
bodies (marines.mil, esd.whs.mil, govinfo.gov, and law.cornell.edu all return
HTTP 403 to the fetch relay), so the verbatim text has to be pasted in.

| # | Document | Located at |
|---|---|---|
| 1 | MCO 1050.3J | `marines.mil/Portals/1/Publications/MCO 1050.3J.pdf` |
| 2 | MCO 5000.12F CH-1 | marines.mil Publications / MCPEL (exact PDF link unconfirmed) |
| 3 | OSD/USD(P&R) DTM, Expansion of the MPLP (4 Jan 2023) | not on a public portal — you hold it |
| 4 | ASN (M&RA) memo, DON MPLP Guidance (17 Jan 2023) | not on a public portal — you hold it |
| 5 | DoDI 1327.06 | `esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/132706p.pdf` |
| 6 | 10 U.S.C. 701 | uscode.house.gov / govinfo.gov / law.cornell.edu |
| 7 | 10 U.S.C. 1052 | uscode.house.gov / govinfo.gov / law.cornell.edu |
| 8 | MARADMIN 523/22 | marines.mil News/Messages |

**Version caveat for DoDI 1327.06:** 051/23 references the edition titled
"Leave and Liberty Policy and Procedures" (16 Jun 2009, incorporating changes).
The current esd.whs.mil PDF is a 2025 reissue retitled "Military Leave, Liberty,
and Administrative Absence" — a different document. For faithful provenance to
051/23, send the 2009 edition.

## What is most useful to send next

- **To prove the schema generalizes:** an MCO (#1 or #2) — a structurally
  different document than a MARADMIN.
- **To complete the parental-leave authority chain end to end:** the DTM (#3)
  and ASN memo (#4).
- **Or simply the next MARADMIN** you want in the corpus — it does not have to be
  on this list.
