"""Render the sources page - what this was built from, and what was taken.

Every claim on this page was verified against a primary source on 2026-08-03
and is recorded with its verdict in conformance-matrix.md. Where a source was
considered and not used, it stays on the page with the reason. A provenance
page that lists only the influences that worked is a marketing page.

The content here is editorial, so it lives in the tool rather than being
derived from the store. The counts at the bottom are read from the store, so
the page cannot drift from what the corpus actually contains.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_authority_chain import BRAND, CSS, esc, load, FAVICON  # noqa: E402
from render_policy import EXTRA_CSS                        # noqa: E402

SOURCES_CSS = """
.grp{margin:34px 0 0}
.grp > p{color:var(--mutedfg);max-width:54rem}
.srcitem{border:1px solid var(--border);border-radius:12px;background:var(--card);
padding:16px 20px;margin:12px 0}
.srcitem h3{margin:0 0 2px;font:700 16px/1.35 inherit}
.srcitem h3 a{text-decoration:none}
.meta{font-size:13px;color:var(--mutedfg);margin:0 0 10px}
.took{margin:10px 0 0;padding:10px 0 0;border-top:1px solid var(--muted)}
.took dt{font:700 11px/1.6 inherit;text-transform:uppercase;letter-spacing:.09em;
color:var(--mutedfg)}
.took dd{margin:2px 0 10px}
.took dd:last-child{margin-bottom:0}
.where{font-size:13px}
.quote{border-left:3px solid var(--brass);padding:2px 0 2px 14px;margin:10px 0;
color:var(--parch3);font-style:normal}
"""

# status -> pill class
ST = {"live": "held", "dormant": "gap", "cancelled": "cancelled",
      "required": "cited", "not binding": "drift", "reference": ""}


def pill(cls, text):
    return f'<span class="pill {cls}">{esc(text)}</span>'


GROUPS = [
 {"title": "Structure and identity",
  "lede": "How a policy document becomes addressable data. These decided the "
          "shape of a record and the form of an identifier.",
  "items": [
   {"name": "United States Legislative Markup (USLM)",
    "url": "https://github.com/usgpo/uslm",
    "who": "U.S. Government Publishing Office", "status": "live",
    "version": "2.1.0, released 2024-08-22",
    "what": "The XML vocabulary Congress publishes statute in, and its "
            "referencing model for addressing a provision inside a document.",
    "took": [
     ("The referencing model",
      "Identifiers are a logical path rooted at the jurisdiction - "
      "<code>/us/usc/t10/s701</code> for statute, and by the same construction "
      "rule <code>/us/dod/don/usmc/mco/1050_3j</code> for a Marine Corps order. "
      "A citation resolves to chapter and verse, not to a whole document."),
     ("The small-level hierarchy",
      "Section, subsection, paragraph, subparagraph, clause, subclause, item. "
      "Our provision depths map onto it directly."),
     ("The versioning model",
      "Multiple versions of an element coexisting with start and end periods, "
      "rather than a new document per amendment."),
     ("What we did NOT take",
      "The namespace. USLM's own scope statement is that it "
      "&ldquo;is not intended to model executive branch or judicial branch "
      "documents,&rdquo; and since version 2.1 a USLM document may not contain "
      "foreign-namespace elements. Our XML is a sibling vocabulary in its own "
      "namespace. This library never claims to be USLM conformant."),
     ("A correction it forced",
      "USLM reserves the period for the file-format suffix, so "
      "<code>mco/1050.3j</code> is ambiguous - it reads as document "
      "<code>mco/1050</code> in format <code>3j</code>. Every identifier in the "
      "corpus was rewritten to use an underscore."),
    ],
    "where": ["Every identifier on every page", "policy-index.html",
              "schema/usmc-issuance-2.0.xsd"]},

   {"name": "S1000D",
    "url": "https://s1000d.org/",
    "who": "ASD, AIA, and ATA e-Business", "status": "live",
    "version": "Issue 6, September 2024",
    "what": "The international specification for technical publications built "
            "on a common source database. Thirty years of production use in "
            "defense, aviation, and shipbuilding.",
    "took": [
     ("Confirmation of the architecture",
      "S1000D reached the same design from the technical-publications side "
      "that we reached from the legislative side. Its Data Module is our "
      "canonical record, its Common Source DataBase is our canonical store, "
      "its Data Module Requirements List is our document set, and its "
      "issue-number and in-work counters are our VERIFIED and UNVERIFIED "
      "states. Two communities, same answer, independently."),
     ("Fragment-level cross-references",
      "S1000D addresses a fragment inside another data module by CODE rather "
      "than by location, so a reference survives the repository being "
      "reorganized. Our provision-path citations work the same way."),
     ("What we have not taken yet",
      "The information code - a controlled vocabulary of information KINDS "
      "rather than subjects - and the applicability model, where a declared "
      "property vocabulary and boolean expressions bind to arbitrary content "
      "nodes. Both are on the list."),
    ],
    "where": ["The provision tree on every policy page",
              "Reference lists that resolve to a target"]},

   {"name": "Standard Generalized Markup Language, ISO 8879",
    "url": "https://www.loc.gov/preservation/digital/formats/fdd/fdd000465.shtml",
    "who": "ISO/IEC JTC 1/SC 34, via the Library of Congress registry",
    "status": "reference", "version": "ISO 8879:1986",
    "what": "The ancestor of XML and the origin of separating content from "
            "presentation.",
    "took": [
     ("The founding principle",
      "Content and presentation are different things. A paragraph knows its "
      "own place in the hierarchy; how it is printed is a separate question. "
      "That is why the stored path is <code>p8/a/1/b</code> while the printed "
      "label is only <code>(b)</code>."),
     ("A lineage note worth knowing",
      "MIL-STD-2361, which set SGML requirements for Army doctrine "
      "publications, was cancelled in 2021. Its lineage now runs through "
      "MIL-STD-40051E. The idea outlived the standard that carried it."),
    ],
    "where": ["The printed view on every policy page, which shows only the "
              "local marker while the data carries the full path"]},
  ]},

 {"title": "Governance and conformance",
  "lede": "What the Department actually requires, verified against the "
          "issuances themselves rather than against summaries of them.",
  "items": [
   {"name": "DoW Digital Standards Strategy",
    "url": "https://www.dsp.dla.mil/",
    "who": "Defense Standardization Program Office", "status": "not binding",
    "version": "January 2026",
    "what": "The Department's stated direction for moving standards from "
            "documents to data.",
    "took": [
     ("The three-tier model",
      "Adapted from ISO/IEC SMART: human-readable, machine-readable, and "
      "machine-interpretable. This library produces all three - the rendered "
      "pages, the JSON and XML, and the tier vocabulary and authority graph "
      "that carry semantics."),
     ("An honest reading of its force",
      "It is not a mandate. Section II states the guidance "
      "&ldquo;is not intended to be prescriptive.&rdquo; There is no "
      "compliance date and no tasking table. We cite it as direction, never "
      "as an obligation."),
     ("The gap it exposes",
      "DoD requires structured XML for technical manuals and has committed to "
      "converting standards to XML. Policy issuances - the layer directing all "
      "of it - are governed by Word templates. DoWI 5025.01 was reissued "
      "20 January 2026, eight days after this strategy, with no "
      "machine-readability provision at all. That inconsistency is the reason "
      "this project exists, and it is stated in the Department's own "
      "documents."),
    ],
    "where": ["conformance-matrix.md section 4"]},

   {"name": "DoDI 8320.07",
    "url": "https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodi/832007p.pdf",
    "who": "DoD Chief Information Officer", "status": "required",
    "version": "3 August 2015, incorporating Change 1",
    "what": "The instruction governing data sharing, and the source of the "
            "&ldquo;consider NIEM first&rdquo; obligation.",
    "took": [
     ("A requirement we owed and had not met",
      "It requires that organizations &ldquo;perform a business case "
      "assessment to compare the suitability of NIEM to that of any potential "
      "alternative approaches&rdquo; and, where NIEM is not chosen, "
      "&ldquo;document the technical, fiscal, and operational reasons "
      "why.&rdquo; This library publishes an XML exchange. The assessment was "
      "missing. It is now written."),
     ("The conclusion it produced",
      "NIEM has no domain for policy, directives, or document management, and "
      "no vocabulary for a provision hierarchy inside a document - it models "
      "exchanges between systems, not the internal structure of a legal text. "
      "Considered, not adopted for the encoding, planned for the exchange "
      "layer when a partner system first consumes this corpus."),
    ],
    "where": ["conformance-matrix.md section 6"]},

   {"name": "NIEM, the National Information Exchange Model",
    "url": "https://niemopen.org/",
    "who": "OASIS Open", "status": "live",
    "version": "NIEM 6.0 and NDR 6.0, OASIS Standards, 28 November 2025",
    "what": "The federal common vocabulary for information exchange between "
            "organizations.",
    "took": [
     ("The extension point, for later",
      "<code>nc:DocumentType</code> carries 65 child properties, a meaningful "
      "set of them records-management oriented - effective date, expiration "
      "date, issue date, approval indicator, disposition authority. That is "
      "where a future exchange layer attaches."),
     ("A precision that matters in any briefing",
      "NDR 6.0 forecloses a claim people make casually: &ldquo;NIEM does not "
      "define conformance for applications, systems, databases, or tools. It "
      "is therefore impossible for any of these to properly claim NIEM "
      "conformance.&rdquo; Only namespaces, schema documents, models, and "
      "messages conform. This system never claims it."),
    ],
    "where": ["conformance-matrix.md section 6"]},

   {"name": "DON XML Naming and Design Rules",
    "url": "https://www.doncio.navy.mil/",
    "who": "Office of the DON Chief Information Officer", "status": "reference",
    "version": "Version 2.0, January 2005",
    "what": "The Department of the Navy's own rules for XML namespaces, "
            "versioning, and promotion between development and enterprise.",
    "took": [
     ("Namespace and version discipline",
      "The base-URN lineage rule, the major-versus-minor version rules, and "
      "the requirement that a change pass approval before entering a published "
      "copy. Our schema versioning and the staging-to-store promotion gate "
      "follow it."),
     ("The continuity mechanism",
      "A deleted rule is recorded with its reason rather than removed. Our "
      "namespace register does the same for retired identifier tokens."),
    ],
    "where": ["NAMESPACES.md", "The promotion report"]},

   {"name": "ASSIST and the Defense Standardization Program",
    "url": "https://assist.dla.mil/online/start/",
    "who": "Defense Logistics Agency", "status": "reference",
    "version": "DoDI 4120.24, 31 March 2022",
    "what": "The official source for DoD specifications and standards.",
    "took": [
     ("A cautionary finding, not a component",
      "ASSIST governs standards, not policy issuances, so it constrains "
      "nothing here. What it demonstrates is the problem: it is the "
      "authoritative index of DoD standards and it exposes no public API, no "
      "bulk data, and no machine-readable index. The Digital Standards "
      "Strategy makes fixing that a line of effort with no date attached."),
    ],
    "where": ["conformance-matrix.md section 5"]},
  ]},

 {"title": "Publication and cataloging",
  "lede": "How the corpus reaches a reader, and what federal law requires of "
          "the metadata that describes it.",
  "items": [
   {"name": "DCAT-US 3.0 and OMB M-25-05",
    "url": "https://resources.data.gov/resources/dcat-us3/",
    "who": "Office of Management and Budget, and the Federal CDO Council",
    "status": "required", "version": "M-25-05 issued 15 January 2025",
    "what": "The federal metadata standard for data catalogs, and the memo "
            "that requires it.",
    "took": [
     ("The catalog format",
      "M-25-05 rescinded and replaced M-13-13 and states the approved schema "
      "&ldquo;will conform to the United States profile of the W3C Data "
      "Catalog Vocabulary Version 3, known as the DCAT-US 3.0.&rdquo; Agency "
      "inventories are due in that format by 30 September 2026. The corpus "
      "emits a conformant catalog record."),
     ("Two details that break implementations",
      "The schema moved from JSON Schema Draft-04 to 2020-12, so an old "
      "validator gives a false pass. And <code>accessLevel</code> is not a "
      "v3.0 core field - <code>accessRights</code> carries that meaning."),
     ("A precision about its status",
      "DCAT-US 3.0 is promulgated and required, but its prose specification "
      "is still a Candidate Recommendation and its implementation guidance is "
      "labelled draft. Say &ldquo;required under M-25-05,&rdquo; not "
      "&ldquo;final.&rdquo;"),
    ],
    "where": ["data.json", "tools/emit_dcat.py"]},

   {"name": "GovInfo Developer Hub",
    "url": "https://www.govinfo.gov/developers",
    "who": "U.S. Government Publishing Office", "status": "live",
    "version": "current",
    "what": "GPO's access channel for federal publications and the schemas "
            "they are published against.",
    "took": [
     ("Statute text and its provenance",
      "The statute records in this corpus cite their exact granule URL in the "
      "provenance block, so a reader can go to the authoritative copy in one "
      "click."),
     ("Schema hosting",
      "Every adopted USLM version is hosted for offline validation against a "
      "pinned version."),
     ("What its MCP preview does not do",
      "GPO's Model Context Protocol preview offers two tools over GovInfo "
      "packages. It has no USLM awareness - no identifier resolution, no "
      "section-level extraction. It cannot resolve our references, and no "
      "resolver for USLM identifiers exists anywhere yet."),
    ],
    "where": ["The provenance block on every statute page"]},

   {"name": "Data.gov and CKAN",
    "url": "https://ckan.org/",
    "who": "General Services Administration", "status": "live",
    "version": "CKAN 2.11.2 at catalog.data.gov",
    "what": "The platform running the federal data catalog and its harvester.",
    "took": [
     ("The publication pattern",
      "Publish a catalog file at a stable public URL with no authentication, "
      "then register a harvest source. Nothing about the encoding changes."),
     ("A discipline it enforces",
      "The harvester reads the source verbatim: &ldquo;It does not correct "
      "typos, normalize field values, or fill in missing information.&rdquo; "
      "Whatever we publish is what appears. That is the same standard the "
      "publication gate already holds us to."),
    ],
    "where": ["data.json"]},
  ]},

 {"title": "Authoring",
  "lede": "The write side. A policy that is born as data never needs to be "
          "recovered from a PDF.",
  "items": [
   {"name": "Open XML SDK and the DOCX format",
    "url": "https://learn.microsoft.com/en-us/office/open-xml/open-xml-sdk",
    "who": "Microsoft, ECMA-376, ISO/IEC 29500", "status": "live",
    "version": "current",
    "what": "The API and file format for Word documents.",
    "took": [
     ("The authoring path",
      "This governs SemperScribe rather than this library. It matters because "
      "DoWI 5025.01 makes Word the production format for DoD issuances - "
      "&ldquo;the FP sends the MS Word file of the issuance ... to the "
      "Directives Division&rdquo; - and SECNAV M-5215.1 prescribes the "
      "typography down to the font. A tool that produces a compliant naval "
      "letter AND exports policy-as-data in one step has to speak Open XML "
      "properly."),
     ("The preservation posture",
      "The Library of Congress format description is the reference for what "
      "survives long term, which is the question behind all of this."),
    ],
    "where": ["SemperScribe, not this library"]},

   {"name": "SECNAV M-5215.1 and DoWI 5025.01",
    "url": "https://www.secnav.navy.mil/doni/",
    "who": "DON Directives and Records Management, and WHS Directives Division",
    "status": "required", "version": "September 2020 and 20 January 2026",
    "what": "The manuals governing how directives themselves are written, "
            "numbered, and formatted.",
    "took": [
     ("The numbering scheme",
      "The Standard Subject Identification Code is what makes a directive "
      "number meaningful rather than sequential, and it is why the corpus can "
      "group by subject series at all."),
     ("The printed convention we preserve exactly",
      "Standard naval letter format prints only the local marker - "
      "<code>(1)</code>, not <code>1.a.(1)</code>. Every page here honors "
      "that, while the data carries the full path underneath."),
     ("The gap they leave",
      "Neither contains the word XML. Both govern format and typography; "
      "neither requires structure. SECNAV M-5215.1 goes as far as "
      "&ldquo;Courier New 12 font is the only authorized font.&rdquo;"),
    ],
    "where": ["The printed view on every policy page", "SSIC-based grouping"]},
  ]},

 {"title": "Reasoning and rules",
  "lede": "How a policy becomes something a machine can act on rather than "
          "merely retrieve. This is the part still being built.",
  "items": [
   {"name": "Prot&eacute;g&eacute; and WebProt&eacute;g&eacute;",
    "url": "https://protege.stanford.edu/software/",
    "who": "Stanford Center for Biomedical Informatics Research",
    "status": "live", "version": "Desktop 5.6.9, released 7 March 2025",
    "what": "The reference editor for OWL 2 ontologies.",
    "took": [
     ("A tool held in reserve, deliberately",
      "The authority graph here is JSON-LD, not OWL, because asserting that "
      "one document cites another needs no description logic. Prot&eacute;g&eacute; "
      "earns its place when the ontology grows classes and inference - "
      "deriving that a provision is in force from the status of everything "
      "above it. Adopting it earlier would have been ceremony."),
    ],
    "where": ["Not yet used - recorded so the choice is visible"]},

   {"name": "IHMC KAoS",
    "url": "https://ontology.ihmc.us/index.html",
    "who": "Florida Institute for Human and Machine Cognition",
    "status": "dormant", "version": "last user guide January 2013",
    "what": "A framework for expressing policy as ontology so that "
            "applicability is decided by reasoning rather than string matching.",
    "took": [
     ("The conceptual model, and nothing else",
      "Policy as a constraint on a defined class of actions, and the division "
      "of policies into authorizations and obligations, each positive or "
      "negative. That framing is still the right one."),
     ("Why it is not a dependency",
      "The project is dormant. Last publication 2008, site frozen between "
      "2010 and 2012, download pages return 404, and it was distributed by a "
      "Java technology removed from the JDK in 2018. We list it because it "
      "shaped the thinking, and because a provenance page that hides the dead "
      "ends is not one."),
    ],
    "where": ["Read, not used"]},

   {"name": "LegalRuleML Core 1.0",
    "url": "https://www.oasis-open.org/standards/",
    "who": "OASIS", "status": "live",
    "version": "OASIS Standard, 8 September 2021",
    "what": "A vocabulary for representing legal and regulatory norms as "
            "machine-processable rules.",
    "took": [
     ("The next thing to adopt",
      "It carries deontic operators, defeasibility, temporal validity, "
      "jurisdiction, and - the property that matters most here - isomorphism, "
      "meaning a rule stays traceable to the provision that states it. That "
      "is the discipline this corpus already practices informally. When the "
      "decision engine generalizes past parental leave, this is the vocabulary "
      "to speak."),
    ],
    "where": ["Planned - the rules layer"]},
  ]},

 {"title": "Considered and set aside",
  "lede": "Listed with the reason, because knowing what was ruled out is part "
          "of knowing what a thing is.",
  "items": [
   {"name": "Standard Financial Information Structure",
    "url": "https://comptroller.war.gov/ODCFO/sfis.aspx",
    "who": "DoD Office of the Deputy Chief Financial Officer",
    "status": "reference", "version": "current",
    "what": "The DoD enterprise standard for financial data elements.",
    "took": [
     ("Nothing, and here is why",
      "It governs financial reporting elements. Nothing in this corpus is a "
      "financial transaction. The nearest adjacency is that MCO 1050.3J cites "
      "the DoD Financial Management Regulation - a policy document citing a "
      "financial regulation, which is not financial data."),
    ],
    "where": ["Not applicable"]},

   {"name": "Monterey Phoenix",
    "url": "https://nps.edu/web/monterey-phoenix",
    "who": "Naval Postgraduate School", "status": "live", "version": "current",
    "what": "A language and tool for modeling and reasoning about system and "
            "process behaviors, generating use-case variants automatically.",
    "took": [
     ("Nothing yet, but the fit is real",
      "It models processes, not data, so it constrains nothing about the "
      "encoding. Where it could earn a place is the publish-review-republish "
      "loop, which has real failure modes and whose absence is the thing that "
      "makes a public corpus stale within a quarter."),
    ],
    "where": ["Not applicable to the data model"]},
  ]},
]


def render(records, out_path):
    docs = len(records)
    provisions = sum(len(s.get("provisions") or [])
                     for r in records.values() for s in r.get("sections", []))
    edges = sum(len(r.get("relationships", {}).get("edge_meta") or [])
                for r in records.values())

    P = ['<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         FAVICON,
         '<title>Sources - Semper Admin Policy Library</title>',
         f"<style>{CSS}{EXTRA_CSS}{SOURCES_CSS}</style></head><body>",
         '<a class="skip" href="#main">Skip to main content</a>',
         f'<header class="chrome">{BRAND}<span>Sources</span>'
         '<a href="policy-index.html" style="margin-left:auto">All policies</a>'
         '<a href="authority-index.html">Authority chains</a></header>',
         '<main id="main">',
         '<h1>What this was built from</h1>',
         '<p class="lede">Every standard, specification, and issuance that '
         'shaped this library, and the specific element taken from each. '
         'Sources that were considered and set aside stay on the page with '
         'the reason - a provenance page that lists only the influences that '
         'worked is a marketing page.</p>',
         '<p class="lede">Every claim below was checked against a primary '
         'source rather than a summary of one. Where a specification is quoted, '
         'the words are its own.</p>']

    for grp in GROUPS:
        P.append(f'<div class="grp"><h2>{esc(grp["title"])}</h2>'
                 f'<p>{esc(grp["lede"])}</p>')
        for it in grp["items"]:
            P.append('<div class="srcitem">')
            P.append(f'<h3><a href="{esc(it["url"])}" rel="noopener">'
                     f'{it["name"]}</a></h3>')
            P.append(f'<p class="meta">{esc(it["who"])} &middot; '
                     f'{esc(it["version"])} '
                     f'{pill(ST.get(it["status"], ""), it["status"])}</p>')
            P.append(f'<p>{esc(it["what"])}</p>')
            P.append('<dl class="took">')
            for label, body in it["took"]:
                P.append(f'<dt>{esc(label)}</dt><dd>{body}</dd>')
            P.append('</dl>')
            P.append('<p class="where"><strong>Where it shows up:</strong> '
                     + " &middot; ".join(esc(w) for w in it["where"]) + '</p>')
            P.append('</div>')
        P.append('</div>')

    P.append('<h2>What the demonstration set contains</h2>')
    P.append(f'<div class="panel"><p>{docs} documents, {provisions:,} '
             f'addressable paragraphs, {edges} relationship edges. Every edge '
             f'is cited: it exists because the issuing authority printed the '
             f'reference on the document. Nothing is inferred from subject '
             f'matter or numbering.</p>'
             f'<p class="small">These counts are read from the canonical store '
             f'when this page is generated, so they cannot drift from what the '
             f'corpus actually holds.</p></div>')

    P.append('<h2>Standing honesty</h2>')
    P.append('<div class="panel"><p class="small">This library never claims '
             'USLM conformance - USLM excludes executive branch documents by '
             'design. It never claims NIEM conformance - the NIEM rules state '
             'that no system can. It cites the DoW Digital Standards Strategy '
             'as direction rather than obligation, because the strategy says '
             'it is not prescriptive. Statute and Department of Defense records '
             'here are metadata-grade: identity, dates, supersession, and '
             'reference lists are transcribed from the authoritative source, '
             'and section text is not ingested. Records are UNVERIFIED machine '
             'extractions until a human confirms them line by line. '
             'This library is an unofficial reference and the issuing '
             'authority\'s copy governs.</p></div>')
    P.append('<footer><p>Full conformance verdicts, with the specification '
             'text each one turns on, are in conformance-matrix.md. The '
             'identifier register is in NAMESPACES.md.</p></footer>'
             '</main></body></html>')

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(P))
    return sum(len(g["items"]) for g in GROUPS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", default="canonical_staging")
    ap.add_argument("--out", default="demo_site")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    records = load(args.store)
    n = render(records, os.path.join(args.out, "sources.html"))
    print(f"sources.html: {n} sources across {len(GROUPS)} groups, "
          f"counts read from {len(records)} records")


if __name__ == "__main__":
    main()
