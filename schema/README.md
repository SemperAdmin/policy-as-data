# Policy-as-data schema

The foundation: a schema and ontology for restricting policy into data. This is
the part that has to be right first — once the schema is correct, documents can
be run through it at scale and validated, rather than hand-built one at a time.

The model follows the House's [USLM](https://github.com/usgpo/uslm) (United
States Legislative Markup) approach to statute, and extends it **downward**
through the federal authority hierarchy to service-level issuances.

## Two layers

| File | Layer | What it defines |
|------|-------|-----------------|
| `usmc-issuance-1.0.xsd` | Document structure | The shape of one issuance: metadata, provisions, numbering, identifiers, verification status. |
| `authority-ontology.ttl` | Authority / provenance | The hierarchy of authority and the relationships (`derivesAuthorityFrom`, `partOf`, `governs`) that connect issuances and provisions across documents. |

A marked-up document (`data/*.uslm.xml`) validates against the XSD. Its
cross-document authority links (`data/*.authority.jsonld`) are written against
the ontology. The two share the path-style identifier scheme, so a provision in
the markup and its node in the authority graph are the same address.

## Authority hierarchy

Lower level number outranks higher; each level derives authority from the levels
above it.

| Level | Class | Example |
|-------|-------|---------|
| 1 | `Statute` | 10 U.S.C. 701 |
| 2 | `CodeOfFederalRegulations`, `ExecutiveOrder` | — |
| 3 | `DoDDirective`, `DoDInstruction`, `OpmIssuance` | DoDI 1327.06 |
| 4 | `NavyIssuance` | SECNAVINST |
| 5 | `MarineCorpsOrder`, `ServiceMessage` | MARADMIN 051/23 |

`derivesAuthorityFrom` is transitive: a MARADMIN that derives from a DoDI that
derives from a statute is, by inference, grounded in that statute.

Cited authority is kept distinct from inferred authority. `derivesAuthorityFrom`
and `references` record links the source text actually states (its REF lines);
`inferredAuthorityFrom` records a link inferred from the policy hierarchy but not
cited in the message. MARADMIN 051/23, for example, cites an OSD Directive-Type
Memorandum and an ASN memo (`derivesAuthorityFrom`) and two MCOs (`references`);
the connection from that DTM up to DoDI 1327.06 is `inferredAuthorityFrom`, so
an inference is never mistaken for a citation.

## Identifier scheme

Every issuance and every provision has a stable, path-style identifier:

```
/us/usmc/maradmin/2023/051            the issuance
/us/usmc/maradmin/2023/051/p8         paragraph 8
/us/usmc/maradmin/2023/051/p8/b/2     paragraph 8.b.(2)
/us/dod/dodi/1327.06                  the DoDI it derives from
/us/usc/10/701                        the statute at the top of the chain
```

The same identifier is used in the markup (`@identifier`), the authority graph
(`@id`), and any future citation. One address per provision, everywhere.

## Verification is structural, not optional

The XSD makes `@status` **required** on the issuance and on every provision.
A document cannot validate without declaring, for each provision, whether it is:

- `VERIFIED` — confirmed against the retrieved issuance text, or
- `UNVERIFIED` — present but the exact source line is not yet located.

This is the project's core discipline enforced by the schema itself: confirmed
policy and asserted policy are distinguishable on the face of the data, and you
cannot encode a provision while staying silent about which it is.

## Document types (v1.1)

v1.0 modeled the MARADMIN (naval message). v1.1 generalizes to other issuance
types in the corpus while staying backward compatible:

- `<num>` is **optional**, so named memo sections (Purpose, Applicability,
  Policy …) and containers (attachments, enclosures) need not be numbered.
- `<meta>` accepts `date` and `signer` (memos/orders) alongside `dtg` (messages).
- `@level` on a provision labels the structural unit it represents:
  `section`, `attachment`, `enclosure`, `chapter`, `appendix`, `part`,
  `paragraph`.

The encoded OSD DTM 23-001 exercises this: named sections, three attachments,
and a glossary, all under one schema. Marine Corps Orders (enclosures, chapters)
use the same constructs.

## Multi-level numbering

Naval-message paragraphs nest as 1 / a / (1) / (a). `<paragraph>` is recursive
to any depth, and `<num>` carries an explicit `@style`
(`arabic`, `alpha-lower`, `alpha-upper`, `paren-arabic`, `paren-alpha`,
`compound`) so the designator's form is data, not a rendering guess. How a
designator is displayed (e.g. underlined) is a downstream presentation concern,
deliberately kept out of the data layer.

## Validate

```bash
xmllint --noout --schema schema/usmc-issuance-1.0.xsd data/maradmin-051-23.uslm.xml
```

## Cross-document relationships

Relationships between issuances live in the authority graphs, not the markup.
Beyond `derivesAuthorityFrom`, the ontology defines `clarifies` and `supersedes`
for follow-on issuances. MARADMIN 129/23, for example, `clarifies` 051/23
without drawing authority from it — recorded in
`data/maradmin-129-23.authority.jsonld`.

## Scope today

The schema is the foundation; the marked-up MARADMINs are the worked corpus:

- `data/maradmin-051-23.uslm.xml` — MARADMIN 051/23 in full (78 provisions).
- `data/maradmin-129-23.uslm.xml` — MARADMIN 129/23, its clarification, in full.
- `data/dtm-23-001.uslm.xml` — OSD DTM 23-001 in full (93 provisions), a
  different document type proving the v1.1 generalization.

All validate against `usmc-issuance-1.0.xsd`, and every citation in
`data/maradmin-051-23.rules.json` resolves to a provision `@identifier` in the
markup. The next document is mechanical: encode to the same schema and identifier
scheme.
