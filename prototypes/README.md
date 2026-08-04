# prototypes/ — kept as reference, not developed

Nothing in this folder is part of the build, the site, or the product. It is
here so the reasoning behind a retired decision stays legible.

## editor.html — retired 2026-07-19

A single-page browser editor that composes a directive as a provision tree and
generates every paragraph path, printed label, and citation number **from
position**. The drafter never types a paragraph number.

It works, and it is a dead end on purpose.

**Why it is retired.** SemperScribe (package `naval-letter-generator`, Next.js
16 / React / TypeScript) already does all of this and more: MCO 5215.1K-correct
numbering including the 4-digit chapter mapping, directive templates with
mandatory Situation / Mission / Execution / Cancellation paragraphs,
mandatory-paragraph locking, portion marking, DOCX and PDF export, and a tested
8-level paragraph engine across 51 test suites. Rebuilding that here would be
waste.

`editor.html` served its purpose. It proved the numbering-from-structure
concept and de-risked the idea in an afternoon. **Do not develop it further.**

**What it proved, and what carries forward.** The two ladders are the same
convention offset by one, arrived at independently:

| SemperScribe level | prints | pipeline depth | path segment |
|---|---|---|---|
| 1 | `1.` | 0 | `pN` |
| 2 | `a` | 1 | `a` |
| 3 | `(1)` | 2 | `1` |
| 4 | `(a)` | 3 | `a` |
| 5 | cycles | 4 | roman |

That agreement is the hardest thing to get right in directive XML, and it needs
no reconciliation. The seam between authoring and this project is therefore one
export module, not a rewrite. `tools/nldp_to_canonical.py` is the unbuilt piece:
read SemperScribe's Naval Letter Data Package JSON, emit a 0.5.0 canonical
record, stamped UNVERIFIED and passed through the gates, ready for
`export_issuance.py`.

**Do not open this file expecting the site chrome.** Its header links to
`index.html` and `how-it-works.html` as siblings, which resolve only if it sits
in `docs/`. It is deliberately not in `docs/` — shipping a retired prototype as
a live page would misrepresent what this project offers. It also calls
`confirm()`, which no page in `docs/` does.
