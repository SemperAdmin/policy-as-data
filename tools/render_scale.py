"""Render docs/scale.html: the same measurement across the full corpus.

The demonstration set is 56 documents, a size a person can check by hand. The
pain is 17,500 documents. This page shows what the same edge and currency
measurement returns across all of them, from a report-only run of
extract_authority.py over the full store: counts, identifiers, and titles for
the documents that appear in a list. No provision text, no rendered pages,
nothing written to the store it was measured from, and every record carrying
a limited distribution statement excluded from the count as from everything
else.

If config/scale_report.json is absent the page says so. A build must succeed
on a fresh clone with nothing else present, and the full corpus is not in the
clone, so the run is made by hand and its report committed. ACTION-REGISTER
6.3.
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
from render_currency import CSS, display  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "config" / "scale_report.json"
DOCS = ROOT / "docs"
OUT = DOCS / "scale.html"
E = html.escape

EXTRA = """
.tiles.six{grid-template-columns:1fr 1fr}
@media(min-width:52rem){.tiles.six{grid-template-columns:repeat(3,1fr)}}
details.grp{margin:8px 0;border:1px solid var(--border);border-radius:8px;padding:6px 12px;background:var(--card)}
details.grp summary{cursor:pointer;font-weight:700}
"""


def not_run() -> str:
    return (head("At scale", extra_css=CSS) + header("At scale", current="scale.html")
            + '''<main id="main"><h1>The same measurement, at scale</h1>
<p class="lede">Not yet run. The demonstration set is 56 documents. The same edge
and currency measurement can be made across the full corpus by a report-only
run of the extraction tool; when it has been, its counts appear here, produced
by the same code and never typed.</p>
<p class="note">Why it is a separate run: a build must succeed on a fresh clone
with nothing else present, and the full corpus is not in the clone.</p>
<footer><p>tools/render_scale.py. This site is an unofficial reference - the
issuing authority's copy governs.</p></footer></main></body></html>''')


def main() -> int:
    if not REPORT.exists():
        page = not_run()
    else:
        r = json.loads(REPORT.read_text(encoding="utf-8"))
        t = r["totals"]
        titles, status = r.get("titles", {}), r.get("status", {})
        gone = r.get("cites_superseded_detail", [])
        drift = r.get("drift_edges", [])
        counts = r.get("named_by_counts", {})
        top = r.get("named_by_top", {})
        n_gone_docs = len({d["citing"] for d in gone})
        n_drift_docs = len({d["citing"] for d in drift})
        by_target: dict = {}
        for d in gone:
            by_target.setdefault(d["target"], []).append(d)

        gone_blocks = ""
        for target, rows in sorted(by_target.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            body = "".join(
                f'<tr><td>{E(display(d["citing"]))}<div class="small">{E(titles.get(d["citing"], "")[:90])}</div></td>'
                f'<td class="small"><span title="{E(d["read_from"])}">{E(cite_words(d["read_from"]))}</span></td></tr>'
                for d in rows)
            gone_blocks += (
                f'<details class="grp"><summary>{len(rows)} in force cite {E(display(target))} '
                f'<span class="pill stale">{E(status.get(target, ""))}</span> '
                f'<span class="small">{E(titles.get(target, "")[:90])}</span></summary>'
                f'<table><tr><th>Document in force</th><th>Read from</th></tr>{body}</table></details>')

        top_rows = "".join(
            f'<tr><td>{E(display(k))}<div class="small">{E(titles.get(k, "")[:90])}</div></td>'
            f'<td>{counts.get(k, len(v))}</td>'
            f'<td><span class="pill {"stale" if status.get(k) in ("superseded", "cancelled") else ("gap" if k not in status else "")}">'
            f'{E(status.get(k, "not held"))}</span></td></tr>'
            for k, v in list(top.items())[:40])

        sc = r.get("status_counts", {})
        page = (head("At scale", extra_css=CSS + EXTRA) + header("At scale", current="scale.html")
                + f'''<main id="main">
<h1>The same measurement, at scale</h1>
<p class="lede">The demonstration set is 56 documents, a size a person can check
by hand. This is the same edge and currency measurement across the full corpus:
{t["docs"]:,} documents read, {t["quarantined"]:,} more excluded for carrying a
limited distribution statement, {t["edges"]:,} cited references. Counts and
identifiers only. No text was rendered and nothing was written to the store it
was measured from.</p>

<div class="tiles six">
<div class="tile"><div class="big">{n_gone_docs:,}</div><p>documents in force cite an
instruction the corpus holds as cancelled or superseded</p></div>
<div class="tile"><div class="big">{t["drift"]:,}</div><p>references name an edition
since superseded, of {t["edges"]:,}</p></div>
<div class="tile"><div class="big">{t["gaps"]:,}</div><p>references name something the
corpus does not hold at all</p></div>
<div class="tile"><div class="big">{t["docs"]:,}</div><p>documents measured</p></div>
<div class="tile"><div class="big">{len(counts):,}</div><p>distinct documents named as a
reference by another</p></div>
<div class="tile"><div class="big">{t["unparsed"]:,}</div><p>reference items the citation
grammar could not parse, counted rather than dropped</p></div>
</div>

<h2 id="gone">In force, citing an instruction that is not</h2>
<p class="lede">{n_gone_docs:,} documents in force, {len(gone):,} references, grouped by
the instruction cited. Each is a reason to open the issuing authority's copy,
not a determination.</p>
{gone_blocks or '<p class="small">None found.</p>'}

<h2 id="editions">Citing an edition since superseded</h2>
<p class="lede">{n_drift_docs:,} documents, {len(drift):,} references. The reference names
the edition the author had; a later edition has since issued. The list is in the
report; the page carries the count.</p>

<h2 id="depended">Most depended upon</h2>
<p class="lede">If one of these reissues, this many documents printed a reference
to it and would need review.</p>
<table><tr><th>Document</th><th>Named by</th><th>Status</th></tr>{top_rows}</table>

<p class="note">Status across the corpus: {", ".join(f"{E(str(k))} {v:,}" for k, v in sc.items())}.
Judged against the same revision index the demonstration set uses. Every count on
this page comes from the report the tool wrote; none is typed.</p>
<footer><p>Generated from config/scale_report.json by tools/render_scale.py. This
site is an unofficial reference - the issuing authority's copy governs.</p></footer>
</main></body></html>''')
    if OUT.exists():
        OUT.unlink()
    write_text(OUT, page)
    print(f"    wrote {OUT.relative_to(ROOT)} ({'from report' if REPORT.exists() else 'not yet run'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
