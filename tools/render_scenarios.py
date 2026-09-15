"""Render docs/scenarios.html: the evaluator on fixed inputs, every line cited.

The evaluator existed only on the command line, so the one piece of the proof
that computes something was invisible on the site. This page runs
tools/evaluate.py in-process on the inputs in config/scenarios.json and shows
what it produces: each decision line with the paragraph it rests on, each
withheld line with the rule the ledger has not admitted, and what the engine
refuses by name. There is no browser-side logic - a JavaScript evaluator would
be a second implementation of the rules, and build.sh stage 17 already names
that trap. Inputs are fixed so the page is a build output like every other.

It is titled Scenarios, not Calculator. It demonstrates cited computation
against encoded rules. It is not an entitlement determination, and the page
says so. ACTION-REGISTER 5.6.
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
from evaluate import RULES_DEFAULT, evaluate, load_rules  # noqa: E402
from verify_status import LEDGER, POLICY  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "scenarios.json"
DOCS = ROOT / "docs"
OUT = DOCS / "scenarios.html"
FINDING_ANCHOR = "verification.html#findings-forfeiture-window"

E = html.escape

CSS = """
.sc{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 20px;margin:16px 0}
.sc h3{margin:0 0 4px;font:700 16px/1.3 inherit}
.sc .narr{color:var(--mutedfg);margin:0 0 10px}
.sc table{border-collapse:collapse;width:100%;font-size:14px;margin:8px 0}
.sc th,.sc td{text-align:left;padding:6px 10px;border-bottom:1px solid var(--muted);vertical-align:top}
.sc th{color:var(--mutedfg);font-size:11px;text-transform:uppercase;letter-spacing:.08em}
.sc .item{font-weight:700}
.sc .withheld{color:var(--mutedfg);font-style:italic}
.sc .cite{font-size:13px;color:var(--mutedfg)}
.sc .inputs{font-size:13px;color:var(--mutedfg)}
.note{border-left:3px solid var(--brass);padding:8px 0 8px 14px;margin:14px 0;color:var(--mutedfg);font-size:14px}
ul.refuse li{margin:4px 0;font-size:14px}
"""

STATE_WORD = {"VERIFIED": "confirmed by a person", "QUORUM_SHORT": "confirmed by one, needs a second",
              "INVALIDATED": "changed since confirmed", "REJECTED": "read and found wrong",
              "UNABLE": "source not obtainable", "UNVERIFIED": "not yet read by a person"}

RULE_WORD = {
    "MAX_PARENTAL_LEAVE_DAYS": "the maximum days",
    "ENTITLEMENT_WINDOW_DAYS": "the forfeiture window",
    "MIN_INCREMENT_DAYS": "the minimum increment",
    "MAX_INCREMENTS": "the maximum number of increments",
    "EVENT_PROXIMITY_MERGE_HOURS": "the merge window",
}


def rule_word(rid: str) -> str:
    return RULE_WORD.get(rid, rid.lower().replace("_", " "))


ITEM_WORD = {
    "authorized_total_days": "Days authorized in total",
    "remaining_days": "Days remaining",
    "forfeiture_date": "Unused leave forfeits after",
    "window_status": "Window",
    "multiple_events": "Multiple events",
    "proposed_increment": "Proposed increment",
}


def page_index() -> dict:
    """USLM document identifier -> policy page, read from the pages already
    rendered. Never from canonical/."""
    out = {}
    for f in DOCS.glob("policy-*.html"):
        m = re.search(r'<div class="ident">([^<]+)</div>', f.read_text(encoding="utf-8", errors="replace"))
        if m:
            out[m.group(1).replace(".", "_")] = f.name
    return out


def cite_link(identifier: str, label: str, pages: dict) -> str:
    """Link a provision identifier to its paragraph on the policy page when
    that page and anchor exist; otherwise the label alone."""
    doc, _, tail = identifier.partition("/p")
    page = pages.get(doc.replace(".", "_"))
    if page and tail:
        anchor = "p" + tail.replace("/", "-")
        text = (DOCS / page).read_text(encoding="utf-8", errors="replace")
        if f'id="{anchor}"' in text:
            return f'<a href="{E(page)}#{E(anchor)}">{E(label)}</a>'
    return E(label)


def scenario_html(sc: dict, result: dict, pages: dict) -> str:
    inputs = {k: v for k, v in result["scenario"].items() if v not in (None, 0) or k == "used_days"}
    inputs_txt = ", ".join(f"{k.replace('_', ' ')} {v}" for k, v in inputs.items())
    rows = []
    for line in result["decision"]:
        note = f' <span class="cite">({E(line["note"])})</span>' if line.get("note") else ""
        extra = ""
        if line["item"] == "forfeiture_date":
            extra = (f' <span class="cite">Computed as 365 days from the event; the source says '
                     f'one year. <a href="{FINDING_ANCHOR}">An open finding</a>.</span>')
        rows.append(f'<tr><td class="item">{E(ITEM_WORD.get(line["item"], line["item"]))}</td>'
                    f'<td>{E(str(line["value"]))}{note}{extra}</td>'
                    f'<td class="cite">{cite_link(line["identifier"], line["citation"], pages)}</td></tr>')
    for w in result["withheld"]:
        deps = ", ".join(
            f"{E(rule_word(d.split(' [')[0]))} ({E(STATE_WORD.get(d.split('[')[1].rstrip(']'), 'not confirmed'))})"
            if "[" in d else E(rule_word(d)) for d in w["withheld_because"])
        rows.append(f'<tr><td class="item">{E(ITEM_WORD.get(w["item"], w["item"]))}</td>'
                    f'<td class="withheld">Withheld. Rests on {deps}.</td>'
                    f'<td class="cite">would cite {cite_link(w["identifier"], w["citation"], pages)}</td></tr>')
    return (f'<div class="sc" id="{E(sc["id"])}"><h3>{E(sc["title"])}</h3>'
            f'<p class="narr">{E(sc["narrative"])}</p>'
            f'<p class="inputs">Inputs: {E(inputs_txt)}</p>'
            f'<table><tr><th>Line</th><th>Result</th><th>Rests on</th></tr>{"".join(rows)}</table></div>')


def main() -> int:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    rules, source, deviation = load_rules(RULES_DEFAULT, LEDGER, POLICY)
    pages = page_index()
    blocks, refusals, summary = [], [], None
    for sc in cfg["scenarios"]:
        result = evaluate(rules, source, deviation, **sc["args"])
        blocks.append(scenario_html(sc, result, pages))
        refusals = result["out_of_scope"]
        by_rule = result["verification"]["by_rule"]
        n_ok = sum(v == "VERIFIED" for v in by_rule.values())
        held = [rule_word(k) for k, v in by_rule.items() if v != "VERIFIED"]
        summary = (f"{n_ok} of {len(by_rule)} encoded values confirmed by a person"
                   + (f"; lines resting on {', '.join(held)} are withheld" if held else ""))
    dev = ""
    if deviation:
        dev = (f'<p class="note"><strong>One verifier is available.</strong> Since '
               f'{E(str(deviation["since"]))} a value is admitted on {deviation["reduced_to"]} '
               f'reading rather than the {deviation["reduced_from"]} the policy requires. '
               f'No figure on this page is an entitlement determination, and none reaches a '
               f'Marine under this deviation.</p>')
    refuse = "".join(f"<li>{E(r)}</li>" for r in refusals)
    page = (head("Scenarios", extra_css=CSS) + header("Scenarios", current="scenarios.html")
            + f'''<main id="main">
<h1>Scenarios</h1>
<p class="lede">Three fixed cases run through the rules encoded from
{E(source)}. Every line names the paragraph it rests on. A line that rests on a
value no person has yet confirmed against the issuing authority's copy is
withheld and says which value. This is a demonstration of cited computation,
not a calculator and not a determination of anyone's entitlement.</p>
<p class="note">Rules: {E(summary or "")}. The source paragraph for every value
is on <a href="policy-MARADMIN-2023-051.html">the message's page</a>; the
confirmation state of each is on <a href="verification.html#queue">the
verification queue</a>.</p>
{dev}
{"".join(blocks)}
<h2>What the engine refuses, by name</h2>
<p class="lede">Questions the encoded rules cannot answer are refused with the
reason, never estimated.</p>
<ul class="refuse">{refuse}</ul>
<footer><p>Generated from data/maradmin-051-23.rules.json and the attestation
ledger by tools/evaluate.py, the same code as the command line. This site is an
unofficial reference - the issuing authority's copy governs.</p></footer>
</main></body></html>''')
    if OUT.exists():
        OUT.unlink()
    write_text(OUT, page)
    print(f"    wrote {OUT.relative_to(ROOT)} ({len(cfg['scenarios'])} scenario(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
