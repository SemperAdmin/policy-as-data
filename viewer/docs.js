// docs.js
// The encoded corpus: one entry per document. Shared by the viewer (app.js) and
// the searchable table (table.js) so the document list never drifts between them.
// Paths are relative to the viewer/ pages, which resolve to repo /data at fetch.

export const DOCS = [
  {
    id: "/us/usmc/maradmin/2023/051",
    label: "MARADMIN 051/23",
    uslm: "../data/maradmin-051-23.uslm.xml",
    authority: "../data/maradmin-051-23.authority.jsonld",
    rules: "../data/maradmin-051-23.rules.json",
  },
  {
    id: "/us/usmc/maradmin/2023/129",
    label: "MARADMIN 129/23 · Clarification",
    uslm: "../data/maradmin-129-23.uslm.xml",
    authority: "../data/maradmin-129-23.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/maradmin/2022/523",
    label: "MARADMIN 523/22 · RC Leave",
    uslm: "../data/maradmin-523-22.uslm.xml",
    authority: "../data/maradmin-523-22.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dtm/2023/23-001",
    label: "DTM 23-001 · OSD",
    uslm: "../data/dtm-23-001.uslm.xml",
    authority: "../data/dtm-23-001.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dodi/1327.06",
    label: "DoDI 1327.06 · DoD",
    uslm: "../data/dodi-1327.06.uslm.xml",
    authority: "../data/dodi-1327.06.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dodd/5124.02",
    label: "DoDD 5124.02 · DoD",
    uslm: "../data/dodd-5124.02.uslm.xml",
    authority: "../data/dodd-5124.02.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/navy/asn-mra/2023/mplp-guidance",
    label: "ASN (M&RA) memo · Navy",
    uslm: "../data/asn-mra-2023-mplp-guidance.uslm.xml",
    authority: "../data/asn-mra-2023-mplp-guidance.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/navy/asn-mra/2021/retiree-council-response",
    label: "ASN Retiree Council memo (standalone)",
    uslm: "../data/asn-mra-2021-retiree-council-response.uslm.xml",
    authority: "../data/asn-mra-2021-retiree-council-response.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usc/10/701",
    label: "10 U.S.C. 701 · Statute",
    uslm: "../data/usc-10-701.uslm.xml",
    authority: "../data/usc-10-701.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usc/10/1052",
    label: "10 U.S.C. 1052 · Statute",
    uslm: "../data/usc-10-1052.uslm.xml",
    authority: "../data/usc-10-1052.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/mco/5000.12F",
    label: "MCO 5000.12F · Order",
    uslm: "../data/mco-5000-12F.uslm.xml",
    authority: "../data/mco-5000-12F.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/mco/1050.3J",
    label: "MCO 1050.3J · Order",
    uslm: "../data/mco-1050-3J.uslm.xml",
    authority: "../data/mco-1050-3J.authority.jsonld",
    rules: null,
  },
];
