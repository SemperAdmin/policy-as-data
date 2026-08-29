# 29. SigmaKEE - EVALUATE, blocked by row 28

Sources: <https://sigmakee.dev/>, <https://github.com/ontologyportal/sigmakee>,
<https://github.com/ontologyportal/sigma-rs>. Retrieved 2026-08-20.

## What it is, confirmed

| | |
|---|---|
| sigmakee.dev | browser-hosted SUMO browser, editor, and theorem prover, the `sigmakee-rs` prover compiled to WebAssembly, running locally in the browser with no server |
| Self-description | **dev build**, stated on the page |
| Features named | symbol and documentation search, knowledge base exploration, an Ask/Tell prover interface, an editor for contributing changes, diagnostic and audit tools |
| sigmakee, upstream | Java, **GPL-3.0**, 6,402 commits, Ant build, jUnit, install guides for Linux, MacOS, Windows, Docker |
| sigmakee README requirement | **at least 16 GB RAM** |
| sigma-rs | Rust rewrite, **GPL-3.0**, SUO-KIF parser, validator, and prover interface, LMDB storage in conjunctive normal form, WASM bindings published as the `sigmakee` npm package, nightly test runs against current SUMO |

## What the facts mean

The 16 GB figure is the operative constraint on the Java tool and it is stated
by the maintainers, not inferred. The WebAssembly build removes the server
requirement. It does not remove the memory question, it relocates it into the
reader's browser tab.

A page describing itself as a dev build has told you its own service level. It
belongs in a browser for reading, never in a pipeline, and never behind a
citation that has to resolve in five years.

## Use it now, at zero cost

Before any adoption decision on row 28, open `Law.kif` in the hosted browser and
read `confersObligation` and `holdsRight` in context with their axioms. That
costs nothing, commits nothing, and answers the only question worth answering
early, which is whether SUMO's deontic vocabulary reaches Marine Corps issuance
structure or stops short of it.

## Verdict

**EVALUATE**, and blocked by row 28. Tooling for a knowledge base the project
has not adopted is not a separate decision. If SUMO is declined, this row closes
with it.

GPL-3.0 on the tooling is a cleaner fact than the licensing contradiction on the
knowledge base, and it still constrains any distribution of a modified build.

Confidence 0.75. Licenses, languages, commit counts, and the RAM requirement
were read directly. The hosted prover was not exercised against a real query.
