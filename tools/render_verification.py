"""Render the verification queue and the process it belongs to.

Answers three questions on one page:

  1. What does the pipeline do, and where is the gate?
  2. What does a VERIFIED value look like, and what does an UNVERIFIED one look
     like, side by side, using real records rather than mock-ups?
  3. What still needs a human, and how does that human record their reading?

The page also captures a verification decision and produces a downloadable
attestation file. It does NOT write anything. A static site has no backend, so
the browser's job ends at producing a file; `tools/attest.py --ingest` is what
admits it, and it recomputes the hash rather than trusting the one in the file.

What this renderer must never do
--------------------------------
Reimplement the rules. Status, quorum, and verdicts come from verify_status.py
and reconcile.py by import. Three tools already disagreed with each other today
because a rule was decided in more than one place; a fourth in JavaScript would
be the same defect with a nicer font.

Nothing rendered here comes from `canonical/`, so no contact data can reach the
page. Verifier ids are opaque and the roster is never read.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reconcile import (  # noqa: E402
    CONCEPTS, UNITS, gather, load_units, reconcile,
)
from verify_status import (  # noqa: E402
    DATA, LEDGER, POLICY, derive, live_rule_assertions, load_ledger, load_policy,
)
from render_authority_chain import BRAND, BRAND_CSS, FAVICON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "verification.html"

E = html.escape

BADGE = {
    "VERIFIED": ("v-ok", "VERIFIED", "A named person read the issuing authority's copy and confirmed this."),
    "QUORUM_SHORT": ("v-part", "QUORUM SHORT", "Read and confirmed, but short of the independent readings this kind of claim requires."),
    "INVALIDATED": ("v-bad", "INVALIDATED", "Confirmed once, then the content changed. The earlier reading no longer applies."),
    "REJECTED": ("v-bad", "REJECTED", "A person read the source and says the encoding is wrong. A found defect."),
    "UNABLE": ("v-warn", "UNABLE", "A person tried and could not, usually because the source could not be obtained."),
    "UNVERIFIED": ("v-none", "UNVERIFIED", "Nobody has read the source against this record."),
}

CSS = """
:root{--color-usmc-scarlet:#B82230;--color-marine-blue:#0F1F3D;--color-marine-blue-100:#6B9BD2;
--color-parchment:#F2E5BE;--color-parchment-300:#FAF1D8;--color-brass:#B89042;--color-brass-300:#D4AF67;
--color-status-fresh:#2F8F5C;--color-status-aging:#C97D1F;--color-status-stale:#B83232;
--color-status-info:#2F5FA8;--color-background:#0A1424;--color-bg-elev:#11203F;--color-bg-sunken:#060E1A;
--color-foreground:#F2E5BE;--color-card:#11203F;--color-muted:#182A4D;--color-muted-foreground:#B5A988;
--color-border:#233A5C;--color-border-strong:#34507A;--color-ring-dark:#D4AF67;--color-neutral-950:#0F0C09;
--font-display:"Bebas Neue","Oswald",system-ui,sans-serif;--font-body:"Inter Variable","Inter",system-ui,sans-serif;
--font-mono:"JetBrains Mono Variable","JetBrains Mono","Cascadia Code",Menlo,monospace;
--radius-sm:6px;--radius-md:8px;--radius-lg:12px;
--shadow-card:0 1px 2px rgba(0,0,0,.4),0 0 0 1px rgba(242,229,190,.04);
--shadow-md:0 2px 4px rgba(0,0,0,.4),0 10px 28px rgba(0,0,0,.45);color-scheme:dark;}
*{box-sizing:border-box}
body{margin:0;background:var(--color-background);color:var(--color-foreground);font:400 15px/1.6 var(--font-body)}
a{color:var(--color-marine-blue-100)}a:hover{color:var(--color-brass-300)}
:focus-visible{outline:3px solid var(--color-ring-dark);outline-offset:2px;border-radius:2px}
.skip{position:absolute;left:-9999px}
.skip:focus{position:static;display:inline-block;padding:8px;background:var(--color-brass-300);color:var(--color-neutral-950)}
header.chrome,main,footer{max-width:60rem;margin:0 auto;padding:16px 24px}
header.chrome{margin-top:16px;border-radius:var(--radius-lg);border:1px solid var(--color-border);
background:var(--color-bg-elev);box-shadow:var(--shadow-md);display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.wordmark{font:400 28px/1.2 var(--font-display);letter-spacing:.04em;color:var(--color-parchment-300);
text-decoration:none;text-transform:uppercase}
.eyebrow{font:700 11px/1 var(--font-body);text-transform:uppercase;letter-spacing:.08em;
color:var(--color-muted-foreground)}
h1{font:400 40px/1.1 var(--font-display);letter-spacing:.02em;margin:24px 0 8px;text-transform:uppercase}
h2{font:400 26px/1.2 var(--font-display);letter-spacing:.02em;margin:36px 0 10px;text-transform:uppercase;
border-bottom:1px solid var(--color-border);padding-bottom:6px}
h3{font:700 14px/1.3 var(--font-body);text-transform:uppercase;letter-spacing:.06em;
color:var(--color-muted-foreground);margin:22px 0 8px}
.prose{max-width:70ch}
.card{background:var(--color-card);border:1px solid var(--color-border);border-radius:var(--radius-lg);
padding:16px 18px;margin:12px 0;box-shadow:var(--shadow-card)}
.mono{font-family:var(--font-mono);font-size:13px;word-break:break-all}
.muted{color:var(--color-muted-foreground)}
.badge{display:inline-block;padding:3px 11px;border-radius:9999px;font:700 11px/1.5 var(--font-body);
text-transform:uppercase;letter-spacing:.06em;border:1px solid}
.v-ok{border-color:var(--color-status-fresh);color:#8FE0B4}
.v-part{border-color:var(--color-status-aging);color:#F0C083}
.v-warn{border-color:var(--color-status-info);color:#9EC0F0}
.v-bad{border-color:var(--color-status-stale);color:#F09A9A}
.v-none{border-color:var(--color-border-strong);color:var(--color-muted-foreground)}
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch;margin:16px 0;padding:0;list-style:none}
.flow li{flex:1 1 150px;background:var(--color-bg-sunken);border:1px solid var(--color-border);
border-radius:var(--radius-md);padding:10px 12px}
.flow li.gate{border-color:var(--color-brass);background:#1b2440}
.flow .n{font:700 11px/1 var(--font-body);color:var(--color-brass-300);letter-spacing:.08em}
.flow .t{font:700 13px/1.35 var(--font-body);margin:4px 0 2px}
.flow .d{font-size:12px;color:var(--color-muted-foreground)}
.two{display:grid;grid-template-columns:1fr;gap:12px}
@media(min-width:52rem){.two{grid-template-columns:1fr 1fr}}
table{border-collapse:collapse;width:100%;font-size:14px;margin:10px 0}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--color-border);vertical-align:top}
th{font:700 11px/1.4 var(--font-body);text-transform:uppercase;letter-spacing:.06em;color:var(--color-muted-foreground)}
.withheld{color:var(--color-muted-foreground);font-style:italic}
label{display:block;font:700 12px/1.6 var(--font-body);text-transform:uppercase;
letter-spacing:.05em;color:var(--color-muted-foreground);margin-top:12px}
input,select,textarea{width:100%;padding:8px 10px;background:var(--color-bg-sunken);
color:var(--color-foreground);border:1px solid var(--color-border-strong);border-radius:var(--radius-sm);
font:400 14px/1.5 var(--font-body)}
button{margin-top:16px;padding:10px 18px;background:var(--color-brass);color:var(--color-neutral-950);
border:0;border-radius:var(--radius-sm);font:700 13px/1 var(--font-body);text-transform:uppercase;
letter-spacing:.06em;cursor:pointer}
button:hover{background:var(--color-brass-300)}
.note{border-left:3px solid var(--color-brass);padding:8px 0 8px 14px;margin:14px 0;
color:var(--color-muted-foreground);font-size:14px}
footer{border-top:1px solid var(--color-border);margin-top:48px;color:var(--color-muted-foreground);font-size:13px}
/* Small screens: the chrome stacks - wordmark row, page label, then nav links
   as wrapping pill targets (the inline margin-left:auto that right-aligns the
   first link on desktop needs the !important to release). Wide tables scroll
   in place instead of stretching the page, and long identifiers break. */
@media (max-width:640px){
header.chrome{align-items:center;column-gap:12px;row-gap:8px;padding:12px 16px}
.wordmark{font-size:22px}
header.chrome span{flex-basis:100%;order:2;font:700 11px/1 var(--font-body);
text-transform:uppercase;letter-spacing:.08em;color:var(--color-muted-foreground)}
header.chrome a:not(.wordmark){order:3;margin-left:0!important;
font:600 13px/1.1 var(--font-body);padding:8px 12px;
border:1px solid var(--color-border-strong);border-radius:9999px;
background:var(--color-muted);color:var(--color-parchment-300);
text-decoration:none}
table{display:block;overflow-x:auto}
code,h3{overflow-wrap:anywhere}
}
""" + BRAND_CSS

FLOW = [
    ("1", "Issuance", "The issuing authority publishes. Their copy governs, always.", False),
    ("2", "Encode", "A provision or a rule value is recorded with the paragraph it was read from.", False),
    ("3", "UNVERIFIED", "Everything machine-produced enters here. Nothing is assumed correct.", False),
    ("4", "A human reads", "A named person opens the authority's copy and compares. This step cannot be automated.", True),
    ("5", "Attest", "The reading is recorded against a hash of the exact content confirmed.", True),
    ("6", "VERIFIED", "Derived, never stored. If the content changes, the reading stops applying.", False),
    ("7", "Used", "Only verified values are compared or published. Unverified ones are withheld and say so.", False),
]


def badge(status: str) -> str:
    cls, label, _ = BADGE.get(status, BADGE["UNVERIFIED"])
    return f'<span class="badge {cls}">{E(label)}</span>'


def example_card(row: dict, ledger: dict) -> str:
    """One worked example, rendered the way the app treats it."""
    cls, label, meaning = BADGE.get(row["status"], BADGE["UNVERIFIED"])
    shown = row["status"] == "VERIFIED"
    records = [r for r in ledger.get(row["assertion"], []) if r.get("verifier")]
    who = ""
    if records:
        r = records[-1]
        who = (f'<p class="muted" style="font-size:13px;margin:6px 0 0">'
               f'Read by <strong>{E(str(r.get("verifier")))}</strong> on '
               f'{E(str(r.get("at", ""))[:10])}, against {E(str(r.get("verified_against", {}).get("edition") or "n/a"))}.'
               f'</p>')
    if shown:
        value = (f'<p style="font:700 30px/1.1 var(--font-display);margin:6px 0">'
                 f'{E(str(row.get("value")))} {E(str(row.get("unit")))}</p>')
    else:
        value = ('<p class="withheld" style="margin:6px 0">Value withheld. Not shown, '
                 'and not used in any comparison, until a person has read the source.</p>')
    src = ""
    if row.get("source_url"):
        src = (f'<p style="margin:6px 0 0;font-size:13px">'
               f'<a href="{E(row["source_url"])}" rel="noopener">Open the issuing authority\'s copy</a></p>')
    return f"""<div class="card">
{badge(row["status"])}
{value}
<p class="muted" style="margin:2px 0;font-size:13px">{E(str(row.get("citation") or ""))}</p>
<p class="mono muted" style="margin:2px 0">{E(row["assertion"])}</p>
{who}{src}
<p class="note" style="margin-top:12px">{E(meaning)}</p>
</div>"""


def render(data_dir: Path, ledger_path: Path, policy_path: Path,
           concepts_path: Path, units_path: Path) -> str:
    quorum, deviation = load_policy(policy_path)
    ledger = load_ledger(ledger_path)
    rows = derive(live_rule_assertions(data_dir), ledger, quorum)
    status = {r["assertion"]: r["status"] for r in rows}

    concepts = json.loads(concepts_path.read_text(encoding="utf-8"))["concepts"]
    table, refused = load_units(units_path)
    items = {i["assertion"]: i for i in gather(data_dir, status)}
    findings = reconcile(concepts, list(items.values()), table, refused)

    # The projection: what the same engine would say if every currently withheld
    # value had been read. Computed by the real reconcile(), not mocked up, so
    # the "after" a reader is shown is the answer they will actually get. It is
    # labelled a projection everywhere it appears - it is not a claim that the
    # values are correct, only that this is what admitting them would produce.
    projected_items = {a: {**i, "verification": "VERIFIED"} for a, i in items.items()}
    projected = reconcile(concepts, list(projected_items.values()), table, refused)
    projected_by_concept = {f["concept"]: f for f in projected}

    for r in rows:
        it = items.get(r["assertion"], {})
        r["value"], r["unit"] = it.get("value"), it.get("unit")
        r["source_url"] = it.get("source_url")

    counts: dict = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    ver = next((r for r in rows if r["status"] == "VERIFIED"), None)
    unver = next((r for r in rows if r["status"] != "VERIFIED"), None)

    flow = "".join(
        f'<li class="{"gate" if g else ""}"><span class="n">{n}</span>'
        f'<div class="t">{E(t)}</div><div class="d">{E(d)}</div></li>'
        for n, t, d, g in FLOW)

    legend = "".join(
        f"<tr><td>{badge(k)}</td><td>{E(v[2])}</td></tr>"
        for k, v in BADGE.items())

    # A literal middle dot, not the entity: this string passes through E()
    # at emission, which would turn "&middot;" into visible "&amp;middot;".
    summary = " · ".join(
        f"{E(k)} {v}" for k, v in sorted(counts.items()))

    dev = ""
    if deviation:
        dev = (f'<p class="note"><strong>Quorum deviation in force since '
               f'{E(str(deviation["since"]))}.</strong> {E(str(deviation["affects"]))} claims '
               f'require {deviation["reduced_to"]} independent reading(s) rather than '
               f'{deviation["reduced_from"]}. Reason: {E(str(deviation["reason"]))}</p>')

    queue_rows = "".join(
        f'<tr><td>{badge(r["status"])}</td>'
        f'<td><span class="mono">{E(r["assertion"])}</span><br>'
        f'<span class="muted" style="font-size:13px">{E(str(r.get("citation") or ""))}</span></td>'
        f'<td class="muted" style="font-size:13px">{E(str(r.get("detail") or ""))}</td></tr>'
        for r in rows)

    def finding_card(f, projection=False):
        tiers = "".join(
            f'<tr><td class="mono">{E(t_["tier"])}</td><td>{E(t_["stated"])}</td>'
            f'<td>{t_["canonical"]} {E(f["canonical_unit"])}</td>'
            f'<td class="muted" style="font-size:13px">{E(str(t_["citation_label"]))}</td></tr>'
            for t_ in f["tiers"])
        held = "".join(
            f'<tr><td class="mono">{E(w["tier"])}</td>'
            f'<td colspan="3" class="withheld">{E(w["reason"])}</td></tr>'
            for w in f["withheld"] + f["not_comparable"])
        cls = ("v-ok" if f["verdict"] == "AGREE" else
               "v-bad" if f["verdict"] == "DIVERGE" else "v-none")
        tag = ' <span class="badge v-warn">PROJECTION</span>' if projection else ""
        return (f'<div class="card"><span class="badge {cls}">{E(f["verdict"])}</span>{tag}'
                f'<h3 style="margin-top:8px">{E(f["label"])}</h3>'
                f'<p class="muted" style="font-size:13px">{E(f["detail"])}</p>'
                f'<table><tr><th>Tier</th><th>Stated</th><th>Normalised</th><th>Paragraph</th></tr>'
                f'{tiers}{held}</table></div>')

    find_rows = ""
    for f in findings:
        find_rows += finding_card(f)

    options = "".join(
        f'<option value="{E(r["assertion"])}" data-hash="{E(items.get(r["assertion"],{}).get("hash",""))}">'
        f'{E(r["assertion"])}</option>'
        for r in rows if r["status"] != "VERIFIED")

    # --- walkthrough on one claim ------------------------------------------
    # Prefer one still unread, so the reader sees work that is actually waiting.
    # Fall back to one already read, shown with that step reversed and labelled
    # as such. Either way the claim must carry a concept, or step 5 has nothing
    # to show changing.
    def _pick(unread: bool):
        return next((r for r in rows
                     if items.get(r["assertion"], {}).get("concept")
                     and (r["status"] != "VERIFIED") == unread), None)
    demo = _pick(True) or _pick(False) or (rows[0] if rows else None)
    demo_already_done = bool(demo) and demo["status"] == "VERIFIED"
    walkthrough = ""
    if demo:
        it = items.get(demo["assertion"], {})
        concept_of = it.get("concept")

        # Before and after are the SAME engine over the same corpus, with this
        # one claim's verification state flipped and every other claim left at
        # its real state. So the delta shown is exactly the delta this reading
        # causes - including the honest case where verifying it is not enough
        # because the other tier is also unread.
        def _with(assertion, state):
            forced = {a: (dict(i, verification=state) if a == assertion else i)
                      for a, i in items.items()}
            return {f["concept"]: f for f in
                    reconcile(concepts, list(forced.values()), table, refused)}

        before = _with(demo["assertion"], "UNVERIFIED").get(concept_of)
        after = _with(demo["assertion"], "VERIFIED").get(concept_of)
        sample = json.dumps({
            "assertion": demo["assertion"],
            "kind": "rule",
            "content_hash_seen": it.get("hash"),
            "verified_against": {
                "edition": "<the edition you opened>",
                "obtained": "<site, and the date you got it>",
                "url": None, "artifact_hash": None},
            "verifier": "V-002",
            "at": "<YYYY-MM-DD>T00:00:00+00:00",
            "method": "read-and-compare",
            "result": "VERIFIED", "note": "",
            "produced_by": "docs/verification.html",
        }, indent=2)
        src_link = (f'<p style="margin:6px 0 0;font-size:13px">'
                    f'<a href="{E(it["source_url"])}" rel="noopener">'
                    f'Open the issuing authority\'s copy</a></p>'
                    if it.get("source_url") else "")
        walkthrough = f"""
<h2>Walkthrough - one claim, end to end</h2>
<p class="muted">A live claim from this corpus. Nothing below is illustrative;
the "after" is produced by the same code that produces the "before".</p>

<h3>Step 1 &middot; Before - the claim is withheld</h3>
{'<p class="note">This claim has already been through the process. It is shown here with that step reversed, so the change is visible.</p>' if demo_already_done else ""}
<div class="card">
{badge(demo["status"])}
<p class="withheld" style="margin:6px 0">Value withheld. The record holds one,
but no person has read the source, so it is neither shown nor compared.</p>
<p class="muted" style="margin:2px 0;font-size:13px">{E(str(demo.get("citation") or ""))}</p>
<p class="mono muted" style="margin:2px 0">{E(demo["assertion"])}</p>
{src_link}
</div>
{finding_card(before) if before else ""}

<h3>Step 2 &middot; The reading</h3>
<div class="card">
<p style="margin:0">Open the issuing authority's copy. Find the cited paragraph.
Confirm it states this value, in these units, at that paragraph and not a
neighbouring one.</p>
<p class="note" style="margin-bottom:0">Do not confirm from the note on the
record, from another tier, or from memory. If the paragraph says something else,
answer <strong>rejected</strong> - a found defect is worth more than a
confirmation.</p>
</div>

<h3>Step 3 &middot; What the form produces</h3>
<p class="muted">The page writes no data. Filling the form below downloads
exactly this, and nothing leaves your browser.</p>
<div class="card"><pre class="mono" style="margin:0;white-space:pre-wrap">{E(sample)}</pre></div>

<h3>Step 4 &middot; Admitting it</h3>
<div class="card">
<p style="margin:0 0 8px">Put the file in <span class="mono">verification/incoming/</span>
and a maintainer runs:</p>
<p class="mono" style="margin:0">python tools/attest.py --ingest</p>
<p class="muted" style="font-size:13px;margin:8px 0 0">That step recomputes the
hash from the corpus and compares it with the one your browser saw. If they
differ, the record changed after you read it and the file is refused - the
reading has to happen again. Nothing is repaired silently.</p>
<p class="muted" style="font-size:13px;margin:6px 0 0">Then
<span class="mono">bash build.sh</span> regenerates this page and every page that
uses the value.</p>
</div>

<h3>Step 5 &middot; After - the value is in use</h3>
<p class="muted">What the same engine produces with this one claim read and
every other claim left exactly as it is. Marked a projection because it previews
the mechanism, not because the values are in doubt. If it still says
NOT_COMPARABLE, that is the honest answer: another tier is unread too, and one
reading is not enough.</p>
{finding_card(after, projection=True) if after else ""}
"""

    examples = ""
    if ver:
        examples += f'<div><h3>Verified - shown and used</h3>{example_card(ver, ledger)}</div>'
    if unver:
        examples += f'<div><h3>Unverified - withheld</h3>{example_card(unver, ledger)}</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{FAVICON}
<title>Verification - G.O.A.T.S. Policy Library</title>
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<header class="chrome">
<img src="semper-logo.jpg" alt="Semper Admin emblem" height="40" style="align-self:center">
{BRAND}<span class="eyebrow">Verification</span>
<a href="how-it-works.html" style="margin-left:auto">How it works</a>
<a href="policy-index.html">All policies</a>
<a href="authority-index.html">Authority chains</a>
<a href="sources.html">Sources</a>
</header>
<main id="main">
<h1>Verification</h1>
<div class="prose">
<p>Nothing here is trusted because a machine produced it. A value is used only
after a named person has opened the issuing authority's copy and confirmed it,
and that reading is bound to the exact content confirmed. If the content later
changes, the reading stops applying and the page says so.</p>
<p><strong>{E(summary)}</strong></p>
{dev}
</div>

<h2>The process</h2>
<p class="muted">Steps 4 and 5 are the ones a person does. Everything else is
mechanical.</p>
<ul class="flow">{flow}</ul>

<h2>What the states mean</h2>
<table><tr><th>State</th><th>Meaning</th></tr>{legend}</table>

<h2>How a value appears, verified and unverified</h2>
<p class="muted">Real records from this corpus, not mock-ups.</p>
<div class="two">{examples}</div>

{walkthrough}

<h2>Cross-tier comparison, as it stands now</h2>
<p class="muted">A value is compared with the authority above it only when both
sides have been read by a person. An unverified side is withheld and the
comparison is refused rather than guessed.</p>
{find_rows}

<h2>The queue</h2>
<table><tr><th>State</th><th>Claim</th><th>Detail</th></tr>{queue_rows}</table>

<h2>Validate a claim</h2>
<div class="prose">
<p>This page cannot write to the library. It produces an attestation file that a
maintainer admits with <span class="mono">python tools/attest.py --ingest</span>,
which recomputes the hash from the corpus rather than trusting the one in the
file. If they differ, the file is refused - that means the record changed after
you read it, and the reading has to happen again.</p>
<p class="note"><strong>Open the issuing authority's copy first.</strong> Do not
confirm from this page, from a note, or from memory. The link is on the claim.</p>
</div>
<form id="f" class="card" onsubmit="return mk(event)">
<label for="a">Claim</label>
<select id="a" required>{options}</select>
<label for="v">Your verifier id</label>
<input id="v" required placeholder="V-002" pattern="[A-Za-z0-9_-]{{2,32}}">
<label for="r">Your reading</label>
<select id="r"><option value="VERIFIED">Confirmed - the cited paragraph states this</option>
<option value="REJECTED">Rejected - the source says something else</option>
<option value="UNABLE">Unable - I could not obtain the source</option></select>
<label for="e">Edition you read</label>
<input id="e" required placeholder="e.g. DoWI 1327.06, Aug 7 2025, Change 1 Jun 30 2026">
<label for="o">Where and when you obtained it</label>
<input id="o" required minlength="12" placeholder="e.g. esd.whs.mil, PDF downloaded 2026-08-08">
<label for="d">Date you read it</label>
<input id="d" required type="date">
<label for="n">Note - required if rejected or unable</label>
<textarea id="n" rows="3"></textarea>
<button type="submit">Download attestation</button>
<p id="msg" class="muted" style="font-size:13px"></p>
</form>
</main>
<footer>
<p>Generated from the attestation ledger and the rule store. Verifier identities
are opaque ids; the roster that maps them to people is never published. This
site is an unofficial reference - the issuing authority's copy governs.</p>
<p><a href="index.html">Home</a> &middot;
<a href="accessibility.html">Accessibility statement</a></p>
</footer>
<script>
function mk(ev){{
  ev.preventDefault();
  var s=document.getElementById('a'), o=s.options[s.selectedIndex];
  var res=document.getElementById('r').value;
  var note=document.getElementById('n').value.trim();
  if(res!=='VERIFIED'&&!note){{
    document.getElementById('msg').textContent='A reason is required for rejected or unable.';
    return false;
  }}
  var rec={{
    assertion:s.value, kind:'rule',
    content_hash_seen:o.getAttribute('data-hash'),
    verified_against:{{edition:document.getElementById('e').value.trim(),
      obtained:document.getElementById('o').value.trim(), url:null, artifact_hash:null}},
    verifier:document.getElementById('v').value.trim(),
    at:document.getElementById('d').value+'T00:00:00+00:00',
    method:'read-and-compare', result:res, note:note,
    produced_by:'docs/verification.html'
  }};
  var name='attestation-'+rec.verifier+'-'+
    rec.assertion.replace(/[^A-Za-z0-9]+/g,'-').replace(/^-|-$/g,'')+'.json';
  var a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify(rec,null,2)],{{type:'application/json'}}));
  a.download=name; a.click(); URL.revokeObjectURL(a.href);
  document.getElementById('msg').textContent=
    'Saved '+name+'. Put it in verification/incoming/ and a maintainer runs '+
    'python tools/attest.py --ingest';
  return false;
}}
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default=str(DATA))
    ap.add_argument("--ledger", default=str(LEDGER))
    ap.add_argument("--policy", default=str(POLICY))
    ap.add_argument("--concepts", default=str(CONCEPTS))
    ap.add_argument("--units", default=str(UNITS))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    page = render(Path(args.data), Path(args.ledger), Path(args.policy),
                  Path(args.concepts), Path(args.units))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8", newline="\n")
    print(f"    wrote {out} ({len(page):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
