# policy-as-data

Restricting Marine Corps policy and doctrine into structured data — the way
Congress publishes statute as [USLM](https://github.com/usgpo/uslm) (United
States Legislative Markup) XML.

The product is the **encoding itself**: a faithful, addressable representation
of an issuance, where every provision has a stable identifier and its authority
can be traced to the statute it derives from. This is not a tool that consumes
policy data; it is the discipline of turning policy *into* data.

The worked document is **MARADMIN 051/23**, Expansion of the Marine Corps
Military Parental Leave Program.

## Artifacts

```
schema/usmc-issuance-1.0.xsd           the schema: structure of one issuance (USLM-aligned)
schema/authority-ontology.ttl          the ontology: authority hierarchy + provenance relationships (OWL/RDF)
schema/README.md                       schema design, identifier scheme, verification semantics

data/maradmin-051-23.uslm.xml          MARADMIN 051/23, full document, marked up and schema-valid
data/maradmin-051-23.authority.jsonld  051/23 authority graph: provisions -> issuance -> DoDI -> statute
data/maradmin-051-23.rules.json        machine-readable rule values extracted from 051/23, each cited
data/maradmin-129-23.uslm.xml          MARADMIN 129/23 (Clarification to 051/23), full document
data/maradmin-129-23.authority.jsonld  129/23 authority graph, including `clarifies` -> 051/23

DATA_CONTRACT.md                       the read-only mandate and the verification legend
REFERENCES.md                          source backlog: authorities cited but not yet encoded
```

The schema is the foundation; the marked-up MARADMINs are the worked corpus that
exercises it. Validate the whole corpus — schema conformance, JSON
well-formedness, ontology parse, data-to-ontology conformance, and that every
citation resolves to a real provision — with:

```bash
python3 tools/validate.py
```

Or validate a single document against the schema directly:

```bash
xmllint --noout --schema schema/usmc-issuance-1.0.xsd data/maradmin-051-23.uslm.xml
```

## First principles

- **Faithful.** Nothing is encoded that is not in the source issuance. Wording,
  numbering, and hierarchy are preserved.
- **Addressable.** Every provision carries a stable identifier
  (e.g. `/us/usmc/maradmin/2023/051/p8`), shared across the markup and the
  authority graph.
- **Traceable.** Authority links run from a provision up through DoDI 1327.06
  to 10 U.S.C. 701.
- **Honest about confidence.** Every encoded value carries a verification
  status. `VERIFIED` means confirmed against the retrieved issuance text;
  `UNVERIFIED` means the source line is not yet located. See `DATA_CONTRACT.md`.
