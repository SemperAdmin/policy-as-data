# Policy as Data

Recasts Marine Corps policy as structured data, the way Congress publishes statute as [USLM](https://github.com/usgpo/uslm) XML, so that every provision has a stable identifier and the authority a policy rests on can be walked up to the Department of Defense instruction or statute behind it. Built for Marines, policy writers and developers who want to see how an issuance connects to what governs it.

**Live:** https://policy-as-data.app.cloud.gov
**Also:** https://semperadmin.github.io/policy-as-data/

## What it does

- Encodes each issuance as addressable provisions, with a stable identifier for every one.
- Opens every policy on one page showing where it sits (the authority ladder above it, one tier at a time, and the traffic below it), what came before (editions, change packages, supersession and reverse drift, each row naming the signal that produced it), and what it says (full text, with every reference a link to the policy it names).
- Traces five authority chains from statute to message, and shows a connection network of all 56 documents and 362 cited references.
- Reports currency: 85 of the 362 edges are drift findings, where a document cites an issuance that has since been superseded.
- Lists the policies in six indexes by issuance type and records on a sources page what the concept was built from.
- Keeps hand-verified and machine-produced encodings in separate tiers, so the two are never mistaken for each other.

### What this does not claim

- **Not USLM conformance.** USLM's own scope statement is that it "is not intended to model executive branch or judicial branch documents", and since version 2.1 a USLM document may not carry foreign-namespace elements. The XML here is a sibling vocabulary in its own namespace: it follows United States Legislative Markup conventions, extended to service issuances.
- **Not NIEM conformance.** The NIEM Naming and Design Rules allow only namespaces, schema documents, models and messages to conform, never a system. [conformance-matrix.md](conformance-matrix.md) section 6 carries the "consider NIEM first" assessment that DoDI 8320.07 requires.
- **Not an official reference.** The issuing authority's copy governs. Statute and Department of Defense records here are metadata-grade (identity, dates, supersession and reference lists transcribed from the authoritative source, with section text not ingested), and each says so on its face.

## Using it

Open the live site in a current browser. No account or CAC is needed. Start at the home page, pick a policy, and follow the links up or down the authority chain. Search works when the site is served over HTTP; opening the files directly from disk disables search only. The earlier read-only viewer is still available under `viewer/` and needs the repository root served over HTTP.

Machine-encoded content is stamped UNVERIFIED. Confirm anything you rely on against the issuing authority's copy.

## Privacy and security

- Data flow: nothing you enter leaves the browser. The pages make no requests to other sites. The only requests are same-site fetches of the site's own JSON (the search index, and the data files the viewer reads), and no pages load third-party scripts, fonts or images. Links to the Semper Admin Portal and to source documents leave the site only when you click them. The one feedback form named on the About page needs a .mil network.
- The verification page builds a record in your browser and offers it as a file download; nothing is uploaded.
- The pages use no cookies, `localStorage` or `sessionStorage`.
- The raw document store is not published, because it carries contact details transcribed from the source issuances. Masking happens at the export boundary, and a contact guard (`tools/contact_guard.py`) runs over the published site before every cloud.gov deploy. Do not add personal or controlled unclassified information to any published file.
- The hosting platforms (cloud.gov and GitHub Pages) keep standard web server access logs, such as IP address, time, requested page and browser type, for operations and security. Semper Admin does not add tracking of its own.

There is no separate privacy policy. See [Security](SECURITY.md) and [NOTICE](NOTICE), which also states what is licensed and what is excluded.

## Data

### Inputs and outputs

| | Where | What |
|---|---|---|
| Input | `canonical/` (not published) | The store of record: one JSON record per document, 56 in all. |
| Input | `config/`, `schema/`, `site/` | Spine definitions, the curated MOS family, id indexes, the JSON contract, the XSDs, the ontology, and the page fragments. |
| Input | `data/*.uslm.xml`, `data/*.authority.jsonld` | The hand-encoded VERIFIED tier. |
| Input | `verification/attestations.jsonl` | The ledger of what a human read and when. VERIFIED status is derived from it on every build. |
| Output | `data/exports/` | Machine-produced issuance XML, every provision stamped UNVERIFIED. |
| Output | `docs/` | The rendered site, including a DCAT-US 3.0 catalog (`docs/data.json`) and a search index. |

`canonical/` is not published, and the build reads it, so a fresh clone carries the standard, the schema, the tooling and the masked exports but not the store they were produced from. That is a stated gap, not an oversight.

### Contracts and references

- [DATA_CONTRACT.md](DATA_CONTRACT.md): the read-only mandate for anyone touching the hand-encoded artifacts in `data/`.
- [NAMESPACES.md](NAMESPACES.md): the identifier register, the allocated tokens and the period ruling.
- [NLDP-CONTRACT.md](NLDP-CONTRACT.md): the contract and the audit of the SemperScribe export.
- [REFERENCES.md](REFERENCES.md): every external authority the corpus cites and where it stands.
- [conformance-matrix.md](conformance-matrix.md): verdicts against each standard and issuance, with the text each turns on.
- [schema/README.md](schema/README.md): schema design, identifier scheme and verification semantics.
- [BUILD.md](BUILD.md): what each build stage does and what needs a decision.

### Two tiers, kept apart

`data/` holds documents encoded by hand and confirmed against the source. `data/dodi-1327.06.uslm.xml` carries 51 provisions marked VERIFIED, and nothing here overwrites it. `data/exports/` holds machine output, stamped UNVERIFIED because no human has confirmed it line by line. Promotion from one tier to the other is explicit and recorded; it never happens by a tool running.

The tiers use different namespaces, on purpose:

| | Namespace | Schema |
|---|---|---|
| `data/` | `https://policy.usmc.mil/ns/uslm/1.0` | `usmc-issuance-1.0.xsd` |
| `data/exports/` | `https://policy.usmc.mil/ns/usmc-issuance/2.0` | `usmc-issuance-2.0.xsd` |

These namespace URIs are identifiers only. They do not name a domain this project operates or an official Marine Corps address. Version 2.0 exists because 1.0 asked one `@status` attribute to carry two unrelated facts; 2.0 separates `@lifecycle` (is the policy in force) from `@verification` (has a human confirmed the extraction). A document can be active and UNVERIFIED, and most are.

### The disciplines

- **Cited and inferred are never conflated.** Every relationship carries its basis: `cited` means the source text states the link, `inferred` means resolution or hierarchy derived it. No edge is written without naming the paragraph it was read from.
- **A gap is stated, never closed.** Where the corpus does not hold a tier, the page says so and says why. Nothing is inferred from subject matter or numbering proximity.
- **A cited edition is never silently upgraded.** When a document names an issuance that has since been superseded, the edge keeps pointing at the edition the text names and reports the drift. `config/revision_index.json`, an index of identifiers known to exist beyond this corpus, is used only to decide whether a cited edition has been superseded.
- **Machine output is UNVERIFIED until a human says otherwise.** Verification is a promotion, and it is recorded.
- **The identifier excludes the period.** USLM reserves it for the file-format suffix, so `/us/dod/don/usmc/mco/1050.3j` would resolve as document `mco/1050` in format `3j`. Machine identifiers use `mco/1050_3j`; a reader still sees MCO 1050.3J everywhere.

## Rebuilding the site

The pipeline is Python 3 using the standard library, driven by `./build.sh` (Bash). The tooling is the 39 Python scripts in `tools/`, and every build stage is idempotent: each removes its own prior output before writing.

**Who can run a full rebuild.** `./build.sh` reads `canonical/`, which is not in the repository (it is listed in `.gitignore`). Only a maintainer who holds that store can rebuild the site. Running `./build.sh` in a fresh clone stops at its first stage.

**What a fresh clone can do.** It can check that the committed data and output are consistent, using the same three checks as `.github/workflows/validate.yml`. They need Python 3.12 (the version CI uses), `xmllint` (the `libxml2-utils` package) and, optionally, `rdflib` for the ontology and conformance checks:

```bash
pip install rdflib
python tools/validate.py
python tests/run_claims.py
python tools/build_stamp.py --check
```

`validate.py` checks the XML against the published schemas, `run_claims.py` runs the claims table in `tests/claims.json` (positive and negative claims, with the negatives as the gate) and writes nothing, and `build_stamp.py --check` fails if a build input changed after the last build. CI also re-runs the build stages that need no `canonical/` (`reconcile.py`, `check_logic.py` and the `render_*` scripts) and requires a clean working tree afterwards.

## Deployment

| Environment | URL | How |
|---|---|---|
| cloud.gov | https://policy-as-data.app.cloud.gov | Serves `docs/` only. `docs/manifest.yml` (staticfile buildpack) and the manual **Deploy to cloud.gov** workflow, which runs the validator and the contact guard, then `cf push` from `docs/`. The sandbox is managed by the private cloudgov-redeploy repository. |
| GitHub Pages | https://semperadmin.github.io/policy-as-data/ | Published from the repository root of `main`, so every file in the repository is served. The root `index.html` redirects to `docs/`. |

## Documentation

- [BUILD.md](BUILD.md): the build stages and what needs a decision.
- [schema/README.md](schema/README.md): the schema and ontology.
- [NOTICE](NOTICE): what is licensed, what carries no copyright, and what is excluded.

The contracts and references listed under Data are the rest of the developer documentation.

## Feedback and support

[Open an issue](https://github.com/SemperAdmin/policy-as-data/issues). Report security problems as described in [SECURITY.md](SECURITY.md).

## License and disclaimer

MIT (see [LICENSE](LICENSE) and [NOTICE](NOTICE)). The issuance text encoded here is United States Government material and no copyright is asserted over it; the MIT grant covers the encoding, tooling and schema.

> This is an independent tool built to help Marines with administrative
> work. It is not an official Department of the Navy or U.S. Marine Corps
> system and is not endorsed by, affiliated with, or approved by either.
> Always confirm requirements against the current governing orders.

## Part of Semper Admin

One of the tools in the Semper Admin suite. Start at the
[Semper Admin Portal](https://semper-admin-portal.app.cloud.gov) for the
full set.
