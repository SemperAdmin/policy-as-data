"""A small Markdown-to-HTML converter, standard library only.

Enough for the finding files in verification/: headings, paragraphs, bullet
lists, pipe tables, fenced code, bold, inline code, and links. Nothing else is
attempted; an unrecognised construct renders as a paragraph of escaped text,
which is honest rather than clever. It exists so a finding written as a
Markdown file can appear on the site without a third-party dependency, which
the standalone-clone property in CLAUDE.md section 2.10 forbids.
"""

from __future__ import annotations

import html
import re

_INLINE = [
    (re.compile(r"`([^`]+)`"), lambda m: f"<code>{html.escape(m.group(1))}</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), lambda m: f"<strong>{m.group(1)}</strong>"),
    (re.compile(r"\[([^\]]+)\]\(([^)]+)\)"),
     lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>'),
]


def inline(text: str) -> str:
    # Escape first, then apply the inline rules to the escaped text. Code spans
    # are matched on the escaped form, so their content is escaped exactly once.
    out = html.escape(text, quote=False)
    for rx, fn in _INLINE:
        out = rx.sub(fn, out)
    return out


def render(md: str, heading_shift: int = 1) -> str:
    """Render Markdown to an HTML fragment. `heading_shift` demotes headings so
    a file's H1 becomes an H2 inside a page that already has an H1."""
    lines = md.replace("\r\n", "\n").split("\n")
    out, para, i = [], [], 0

    def flush():
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush()
            block = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            out.append(f"<pre><code>{html.escape(chr(10).join(block))}</code></pre>")
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            flush()
            level = min(6, len(m.group(1)) + heading_shift)
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|?$", lines[i + 1]):
            flush()
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            out.append("<table><tr>" + "".join(f"<th>{inline(h)}</th>" for h in header) + "</tr>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>"
                                 for r in rows) + "</table>")
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                item = re.sub(r"^\s*[-*]\s+", "", lines[i])
                i += 1
                # continuation lines are indented
                while i < len(lines) and lines[i].startswith("  ") and not re.match(r"^\s*[-*]\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            flush()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                item = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("   ") and not re.match(r"^\s*\d+\.\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                items.append(f"<li>{inline(item)}</li>")
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if ln.strip() in ("---", "***"):
            flush()
            out.append("<hr>")
            i += 1
            continue
        if not ln.strip():
            flush()
            i += 1
            continue
        para.append(ln.strip())
        i += 1
    flush()
    return "\n".join(out)


def title_of(md: str) -> str:
    for ln in md.split("\n"):
        m = re.match(r"^#\s+(.*)$", ln)
        if m:
            return m.group(1).strip()
    return ""
