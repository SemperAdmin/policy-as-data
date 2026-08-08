# 20. NIST Software Portal, code.nist.gov - ADAPTED, and it surfaces a GAP

Sources:
<https://code.nist.gov/category/#/ALLSOFTWARE> (catalogue view),
<https://code.nist.gov/> (portal root),
<https://www.nist.gov/open/license> (the governing licensing statement).
Retrieved 2026-08-08. Publisher: National Institute of Standards and Technology.

**Retrieval note.** `code.nist.gov/category/#/ALLSOFTWARE` is a fragment route
in a single-page application. The fragment never reaches the server, so
automated retrieval of that URL returns the portal shell and nothing else. The
catalogue contents are **UNCONFIRMED**: no repository list was obtained. The
portal describes itself as "a hub for our open source projects" with "a full
catalog...updated regularly as repositories are added or modified." Treat
`#/ALLSOFTWARE` as a browser-only view and cite the portal root instead.

## The part that governs, and it is the licensing statement

NIST software is not subject to copyright protection in the United States under
17 U.S.C. 105, because it is prepared by officers or employees of the United
States Government as part of their official duties. The distribution statement
NIST requires:

> "NIST-developed software is provided by NIST as a public service. You may use,
> copy, and distribute copies of the software in any medium, provided that you
> keep intact this entire notice."

With, in substance:

- provided AS IS, no warranty of merchantability, fitness, or non-infringement
- no NIST liability for use or results
- derivative works permitted, and **modified versions must carry notice of the
  change, the date, and its nature**
- NIST must be acknowledged as the original source
- third-party components carry their own copyright and licensing statements
- copyright may still subsist in foreign jurisdictions

## The GAP this surfaces

**This repository ships no license and no notice of any kind.** A directory
walk on 2026-08-08 found no `LICENSE`, no `COPYING`, no `NOTICE`, no
`CITATION.cff`, and no `code.json` anywhere in the tree.

That matters because the repository is published. `docs/` is served by GitHub
Pages, `.nojekyll` and `docs/Staticfile` are present, and `deploy_cloudgov.bat`
targets cloud.gov. A published US Government work with no stated terms leaves
three questions open that a reuser cannot answer:

1. **Are the tools public domain or not?** The 23 scripts in `tools/` are the
   reusable asset. Their status is unstated. If they were produced as official
   duty they are 17 U.S.C. 105 material and should say so. If they were not,
   they need an actual license grant.
2. **What are the terms on the schema and the standard?** `usmc-issuance-2.0.xsd`
   and `NAMESPACES.md` are the artifacts most likely to be adopted by someone
   else. An unlicensed schema is one nobody in a compliance-sensitive
   organisation will adopt.
3. **Where does the not-authoritative disclaimer live as a term rather than as
   prose?** `README.md` says "Not an official reference. The issuing authority's
   copy governs." That is the right statement and it is currently a paragraph
   in a readme, not a notice attached to the artifacts.

**Fix.** Add a `LICENSE` stating the applicable terms, and a short `NOTICE`
carrying the not-authoritative disclaimer in the NIST AS-IS form. The NIST text
above is the closest working precedent for a US Government work published for
public reuse, and it is short enough to adapt directly. **State: OPEN.**

Second, smaller item: federal source-code inventories are published as a
`code.json` metadata file at the repository root, per the Federal Source Code
Policy. This project already emits DCAT-US for its data, per conformance matrix
section 7. Emitting `code.json` for its software is the same move on the other
axis, and `tools/emit_dcat.py` is the obvious place to put it. Not a
requirement here, because no agency inventory currently pulls this repository.
Recorded so the option is not re-discovered.

## What else transfers

**The catalogue-over-repositories pattern.** The NIST portal does not host
code. It catalogues repositories that live elsewhere, and refreshes as they
change. That is structurally what `docs/sources.html` does for this project's
concept sources, and what `config/revision_index.json` does for document
identity. The pattern is validated by a federal precedent, which is worth a
sentence in any submission.

**The disclaimer as a distribution condition.** NIST attaches its AS-IS
statement to the artifact, not to the website. This project attaches its
not-authoritative statement to every rendered page - `README.md` says "Every one
of them says so on its face" - but not to the exported XML. Every file in
`data/exports/` leaves the repository with no statement of authority on it. A
processing instruction or a header comment carrying the disclaimer would close
that, at near-zero cost.

## Verdict

**ADAPTED, and it surfaces one GAP.** The licensing model and the AS-IS
disclaimer pattern are directly copyable and should be copied. The GAP is this
repository's own absence of a license and notice, it is real, and it is open.

## Confidence

0.8. The licensing statement was retrieved from nist.gov and quoted, and the
absence of license files in this repository was verified by directory walk. The
`#/ALLSOFTWARE` catalogue contents were not retrieved and are marked
UNCONFIRMED. The `code.json` point is a recommendation, not an obligation, and
is stated as such.
