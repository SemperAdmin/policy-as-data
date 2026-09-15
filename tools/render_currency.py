"""Render docs/currency.html: what rests on something that no longer exists.

The question a general asks first, in the words a general uses. Three tiers of
finding, strongest first:

1. A document in force today whose own reference list names an instruction
   this set holds as cancelled or superseded. The citation is real and cited;
   the thing cited is gone.
2. A document naming an edition that has since been superseded, judged against
   the revision index of everything known to exist. The reference is not wrong
   as written; it is out of date, and the edition now held is named beside it.
3. A document naming something this set does not hold at all. Status unknown,
   stated as a gap, never closed by inference.

Reads config/authority_report.json only. Rows are identifiers, statuses,
titles, and the paragraph a citation was read from. No provision text, so the
contact guard holds by construction. ACTION-REGISTER 6.1.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atomicio import write_text  # noqa: E402
from chrome import head, header  # noqa: E402
from render_authority_chain import cite_words  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "config" / "authority_report.json"
DOCS = ROOT / "docs"
OUT = DOCS / "currency.html"
E = html.escape

CSS = """
.big{font:400 40px/1 "Bebas Neue",Oswald,system-ui,sans-serif;color:var(--brass3);letter-spacing:.02em}
.tiles{display:grid;grid-template-columns:1fr;gap:12px;margin:12px 0}
@media(min-width:52rem){.tiles{grid-template-columns:1fr 1fr 1fr}}
.tile{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.tile p{margin:8px 0 0;font-size:14px;color:var(--mutedfg)}
table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--muted);vertical-align:top}
th{color:var(--mutedfg);font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.pill{display:inline-block;padding:2px 9px;border-radius:9999px;font:700 11px/1.6 inherit;border:1px solid var(--borders);background:var(--muted);color:var(--parch3);white-space:nowrap}
.pill.stale{border-color:var(--stale);color:#f3a3a3}
.pill.drift{border-color:var(--aging);color:#f0c489}
.pill.gap{border-color:var(--borders);color:var(--mutedfg)}
.small{font-size:13px;color:var(--mutedfg)}
.note{border-left:3px solid var(--brass);padding:8px 0 8px 14px;margin:14px 0;color:var(--mutedfg);font-size:14px}
"""


def display(doc_id: str) -> str:
    """Store key to the number a reader knows. MARADMIN-2023-051 -> MARADMIN 051/23."""
    prefix, _, rest = doc_id.partition("-")
    if prefix == "USC":
        m = re.match(r"T(\d+)(?:-S(.+))?$", rest)
        if m and m.group(2):
            return f"{m.group(1)} U.S.C. {m.group(2)}"
        if m:
            return f"Title {m.group(1)}, U.S.C."
    nice = {"DODI": "DoDI", "DODD": "DoDD", "DODFMR": "DoD FMR", "SECNAVM": "SECNAV M-"}.get(prefix, prefix)
    if prefix == "MARADMIN" and rest[:4].isdigit() and "-" in rest:
        y, n = rest.split("-", 1)
        return f"MARADMIN {n}/{y[2:]}"
    return f"{nice} {rest}".replace("M- ", "M-")


def link(doc_id: str, pages: set) -> str:
    page = f"policy-{doc_id}.html"
    if page in pages:
        return f'<a href="{E(page)}">{E(display(doc_id))}</a>'
    return E(display(doc_id))


def main() -> int:
    r = json.loads(REPORT.read_text(encoding="utf-8"))
    pages = {p.name for p in DOCS.glob("policy-*.html")}
    titles, status = r.get("titles", {}), r.get("status", {})
    t = r["totals"]
    gone = r.get("cites_superseded_detail", [])
    drift = r.get("drift_edges", [])
    n_gone_docs = len({d["citing"] for d in gone})
    n_drift_docs = len({d["citing"] for d in drift})

    gone_rows = "".join(
        f'<tr><td>{link(d["citing"], pages)}<div class="small">{E(titles.get(d["citing"], "")[:90])}</div></td>'
        f'<td>{link(d["target"], pages)}<div class="small">{E(titles.get(d["target"], "")[:90])}</div></td>'
        f'<td><span class="pill stale">{E(d["target_status"])}</span></td>'
        f'<td class="small"><span title="{E(d["read_from"])}">{E(cite_words(d["read_from"]))}</span></td></tr>'
        for d in gone)

    by_citing: dict = {}
    for d in drift:
        by_citing.setdefault(d["citing"], []).append(d)
    drift_rows = ""
    for citing, rows in sorted(by_citing.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        first = True
        for d in rows:
            holds = ", ".join(E(display(h)) for h in d["holds"]) or "an edition this set does not hold"
            drift_rows += (
                f'<tr>'
                + (f'<td rowspan="{len(rows)}">{link(citing, pages)}<div class="small">'
                   f'{E(titles.get(citing, "")[:90])}</div></td>' if first else "")
                + f'<td>{E(display(d["target"]))}</td>'
                f'<td class="small">{holds}</td>'
                f'<td class="small"><span title="{E(d["read_from"])}">{E(cite_words(d["read_from"]))}</span></td></tr>')
            first = False

    page = (head("Currency", extra_css=CSS) + header("Currency", current="currency.html")
            + f'''<main id="main">
<h1>What rests on something that no longer exists</h1>
<p class="lede">Every document here printed a reference list. Every row below is a
reference that still points at something, read from the paragraph that names
it. Nothing is inferred from subject or numbering; a citation exists on this
page only because the issuing authority printed it.</p>

<div class="tiles">
<div class="tile"><div class="big">{n_gone_docs}</div><p>documents in force today
cite an instruction this set holds as cancelled or superseded</p></div>
<div class="tile"><div class="big">{t["drift"]} of {t["edges"]}</div><p>references
name an edition that has since been superseded</p></div>
<div class="tile"><div class="big">{t["gaps"]}</div><p>references name something this
set does not hold. Status unknown, stated as a gap</p></div>
</div>

<h2 id="gone">In force, citing an instruction that is not</h2>
<p class="lede">The strongest finding this set produces. The citing document is
active. The cited one has been cancelled or superseded, and this set holds the
record that says so.</p>
<table><tr><th>Document in force</th><th>Cites</th><th>Which is</th><th>Read from</th></tr>
{gone_rows or '<tr><td colspan="4" class="small">None in this set.</td></tr>'}</table>

<h2 id="editions">Citing an edition since superseded</h2>
<p class="lede">{n_drift_docs} documents, {len(drift)} references. The reference is
not wrong as written; it names the edition the author had. Judged against the
revision index of {t.get("known", 0):,} identifiers known to exist, a later
edition has since issued. The cited edition is never silently upgraded; the
edition now held is named beside it.</p>
<table><tr><th>Document</th><th>Names</th><th>Now held as</th><th>Read from</th></tr>
{drift_rows or '<tr><td colspan="4" class="small">None in this set.</td></tr>'}</table>

<h2 id="unheld">Citing something this set does not hold</h2>
<p class="lede">{t["gaps"]} references, and the status of what they name is unknown
here. That is stated, not closed: the tool refuses to guess whether an
instruction it has never seen is still in force.
<a href="connections.html">The network</a> shows every one as an edge to a
document outside the set.</p>

<p class="note">This page compares the statuses and editions this set records. The
issuing authority's copy governs, and a row here is a reason to open it, not a
determination. Every count is produced by the build from the reference lists as
printed; none is typed.</p>
<footer><p>Generated from the authority report by tools/render_currency.py. This
site is an unofficial reference - the issuing authority's copy governs.</p></footer>
</main></body></html>''')
    if OUT.exists():
        OUT.unlink()
    write_text(OUT, page)
    print(f"    wrote {OUT.relative_to(ROOT)}: {n_gone_docs} in force citing gone, "
          f"{len(drift)} drift, {t['gaps']} unheld")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
