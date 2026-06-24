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
data/maradmin-051-23.uslm.xml          document-structure markup (USLM-aligned), stable @identifiers
data/maradmin-051-23.authority.jsonld  authority graph: provision -> issuance -> DoDI -> statute
data/maradmin-051-23.rules.json        machine-readable rule values extracted from the text, each cited
DATA_CONTRACT.md                       the read-only mandate and the verification legend
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
