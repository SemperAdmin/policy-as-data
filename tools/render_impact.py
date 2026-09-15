"""Render docs/impact.html: if this document reissues, what names it.

The question three constituencies asked in three words: what does this affect.
For every document named as a reference by any other, the documents that name
it and the paragraph each read it from. Sorted by how many depend on it, so the
top of the page is the document whose reissue would touch the most.

A target this set does not hold still appears: seven documents name
SECNAV M-5210.1 and the set has never seen it. That is a finding about the
set, stated rather than hidden.

Reads config/authority_report.json only. Identifiers, statuses, titles, and
read-from paragraphs; no provision text. ACTION-REGISTER 6.2.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomicio import write_text  # noqa: E402
from chrome import head, header  # noqa: E402
from render_authority_chain import cite_words  # noqa: E402
from render_currency import CSS, display, link  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "config" / "authority_report.json"
DOCS = ROOT / "docs"
OUT = DOCS / "impact.html"
E = html.escape

EXTRA_CSS = """
details.dep{margin:6px 0;border:1px solid var(--border);border-radius:8px;padding:6px 12px;background:var(--card)}
details.dep summary{cursor:pointer;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap}
details.dep summary .n{font:400 26px/1 "Bebas Neue",Oswald,system-ui,sans-serif;color:var(--brass3);min-width:2.2em}
details.dep table{margin:8px 0 4px}
"""

STATUS_PILL = {"active": ("", "in force"), "superseded": ("stale", "superseded"),
               "cancelled": ("stale", "cancelled")}


def main() -> int:
    r = json.loads(REPORT.read_text(encoding="utf-8"))
    pages = {p.name for p in DOCS.glob("policy-*.html")}
    titles, status, named_by = r.get("titles", {}), r.get("status", {}), r.get("named_by", {})
    t = r["totals"]
    held = [k for k in named_by if k in status]
    unheld = [k for k in named_by if k not in status]

    def block(target: str) -> str:
        rows = named_by[target]
        st = status.get(target)
        cls, word = STATUS_PILL.get(st, ("gap", "not held in this set"))
        title = titles.get(target, "")
        body = "".join(
            f'<tr><td>{link(d["citing"], pages)}<div class="small">{E(titles.get(d["citing"], "")[:90])}</div></td>'
            f'<td class="small"><span title="{E(d["read_from"])}">{E(cite_words(d["read_from"]))}</span></td></tr>'
            for d in rows)
        return (f'<details class="dep" id="{E(target)}"><summary><span class="n">{len(rows)}</span>'
                f'<span>{link(target, pages)}</span><span class="pill {cls}">{E(word)}</span>'
                f'<span class="small">{E(title[:100])}</span></summary>'
                f'<table><tr><th>Named by</th><th>Read from</th></tr>{body}</table></details>')

    top = next(iter(named_by), None)
    page = (head("Impact", extra_css=CSS + EXTRA_CSS) + header("Impact", current="impact.html")
            + f'''<main id="main">
<h1>If this reissues, what breaks</h1>
<p class="lede">Every document below is named as a reference by at least one
other. Open one to see who names it and at which paragraph. A reissue of the
document at the top would touch {len(named_by[top]) if top else 0} others; each of
them printed the reference and inherits the change.</p>

<div class="tiles">
<div class="tile"><div class="big">{len(named_by)}</div><p>distinct documents named as a
reference across the set</p></div>
<div class="tile"><div class="big">{t["edges"]}</div><p>cited references, every one read
from a printed reference list</p></div>
<div class="tile"><div class="big">{len(unheld)}</div><p>of those named are not held in
this set at all. Their dependents are listed; their content is not</p></div>
</div>

<h2 id="held">Held in this set, most depended-upon first</h2>
{"".join(block(k) for k in held)}

<h2 id="unheld">Named but not held</h2>
<p class="lede">The set has never seen these. Their dependents are real and cited;
what a reissue would change in them is unknown here, and stated as such.</p>
{"".join(block(k) for k in unheld)}

<p class="note">Direction matters. This page answers "if X changes, who inherits
it." The <a href="currency.html">currency page</a> answers the reverse: "what
does X rest on that has already changed." Every policy page carries both for its
own document.</p>
<footer><p>Generated from the authority report by tools/render_impact.py. This
site is an unofficial reference - the issuing authority's copy governs.</p></footer>
</main></body></html>''')
    if OUT.exists():
        OUT.unlink()
    write_text(OUT, page)
    print(f"    wrote {OUT.relative_to(ROOT)}: {len(named_by)} targets, {len(unheld)} not held")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
