# Handoff - what GunnyBot keeps, what it gives up

Date: 2026-08-04. Companion to `D:\Coding\policy-as-data\MOVED.md`.

`policy-as-data` is now a standalone project. It carries its own 56-document
corpus, its own tooling, and its own build, and it runs with GunnyBot absent.
This note records the line between them so the two do not drift into being two
copies of the same thing.

---

## The line

**GunnyBot is the factory.** Acquisition, extraction, and the corpus at scale.

**policy-as-data is the standard and the product.** The schema, the vocabulary,
the encoding disciplines, the renderers, the demonstration corpus, and the
site.

A tool belongs to whichever side owns the question it answers. "How do I turn a
PDF into a record" is GunnyBot's. "What does a record mean, and how is it
rendered, exported, and verified" is policy-as-data's.

---

## GunnyBot keeps

Nothing was removed from `E:\GunnyBot`. It still has every tool. What changed
is which copy is authoritative.

| Tool | Why it stays here |
|---|---|
| `src/scrapers/`, `src/extractor.py`, `src/parser.py` | acquisition |
| `canonical_convert.py` | PDF and HTML to canonical record |
| `propagate_supersession.py` | needs the 17,514-record graph |
| `wire_mcpel_status.py` | MCPEL catalog authority, owner locks |
| `find_implementers.py` | needs the 14,018-message corpus to be useful |
| `promotion_report.py` | adjudicates changes to GunnyBot's store of record |
| `build_search.py`, `build_training_corpus.py`, `export_graph.py` | operate on the full corpus |
| the audit and probe scripts | forensic work against the big store |

Those two, `find_implementers.py` and `promotion_report.py`, were deliberately
left out of the new project. They are meaningless against 56 documents.

## policy-as-data now owns

These are the authoritative copies. When one of them needs a change, change it
there and copy back, not the reverse.

    provisions.py             the provision parser
    profile_readability.py    document category classification
    authority.py              the citation grammar
    extract_authority.py      cited authority edges
    reparse_provisions.py     rebuild trees from stored text
    ingest_authority_tiers.py the statute and DoD records
    normalize_identifiers.py  the period ruling
    backfill_subjects.py      Subj: recovery
    lineage.py                version history from four signals
    render_authority_chain.py
    render_policy.py
    render_connections.py
    render_sources.py
    export_issuance.py        usmc-issuance 2.0
    emit_dcat.py              DCAT-US 3.0
    verify_authority.py       the adversarial check
    atomicio.py               crash-safe record writes
    corrections.py            a tool replaces its own correction entry
    check_site.py             link, asset, anchor, and orphan check

    schema/policy_document.schema.json   0.5.0
    schema/usmc-issuance-2.0.xsd

    branding/                 the mirrored style guide and the emblem
    prototypes/editor.html    the retired authoring proof of concept

`atomicio.py`, `corrections.py`, and the patched `ingest_authority_tiers.py`
were copied back to `E:\GunnyBot\tools` on 2026-08-04, so both sides carry the
same six-file fix. They are not policy-as-data-specific - a torn record and a
corrections array that counts builds are worse at 17,514 documents than at 56.

### One tool is now forked on purpose

`build_search.py` exists on both sides and they are **not** the same tool. The
GunnyBot copy indexes the full 17,514-document corpus. The policy-as-data copy
indexes this project's 56 and builds its result links as `policy-<ID>.html`,
because the integrated pages no longer use the `<ID>.html` naming. Copying
either over the other breaks search on that side. This is the one place the
copy-back rule above does not apply.

## The coupling that remains, and it is deliberate

`policy-as-data/config/revision_index.json` holds 17,514 document identifiers
derived from GunnyBot's corpus. It carries **identifiers only** - no titles, no
text, no contacts.

It exists for one reason. Revision drift means a document cites an edition that
has been superseded. That is a fact about the world, not about how many
documents a project holds. Judged against the 56 records held here, drift
collapsed to 17 findings and the headline currency finding all but vanished.
Judged against the index, it is 85 and correct.

Regenerate it whenever GunnyBot's corpus changes:

    python -c "import os,json; json.dump(sorted(f[:-5] for f in os.listdir('canonical') if f.endswith('.json')), open('D:/Coding/policy-as-data/config/revision_index.json','w'))"

If that ever becomes unwanted, the alternative is to drop `--revision-index`
from the build. The tooling handles its absence by reporting less rather than
guessing, which is the right failure.

---

## Still open on the GunnyBot side

`promotion_report.md` is unchanged and still waiting: 16 records with moved
provision paths, 21,315 rewritten identifiers, 11 new top-tier records, none of
it promoted into `E:\GunnyBot\canonical`. The extraction did not touch that
decision. The staging directory holds the same records the new project now
carries, so approving the promotion brings GunnyBot's store into line with what
`policy-as-data` publishes.

If the promotion is declined, the two diverge and the new project's corpus
becomes the only place the corrected records exist. That is a legitimate
outcome, but it should be a decision rather than a drift.

---

## Folders awaiting your delete

The bridge that reaches your disk cannot delete, only move. Six folders hold
retired files:

    E:\GunnyBot\demo_site\_to_delete\              3 scratch files
    D:\Coding\policy-as-data\docs\_to_delete\      7 superseded pages
    D:\Coding\policy-as-data\docs\search\_to_delete_t\  1,332 stale index shards
    D:\Coding\policy-as-data\tools\_to_delete\     export_uslm.py, find_implementers.py, promotion_report.py
    D:\Coding\policy-as-data\data\exports\_to_delete\   14 stale .uslm.xml and .authority.jsonld
    D:\Coding\policy-as-data\.git\_to_delete\      a stale index.lock

The last one matters most. A stale `.git/index.lock` makes the next git command
fail with "Another git process seems to be running." It is out of `.git/` now,
but delete the folder.
