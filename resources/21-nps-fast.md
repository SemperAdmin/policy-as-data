# 21. NPS FAST, fast.mfr.nps.edu - UNCONFIRMED

Source: <https://fast.mfr.nps.edu/>
Attempted 2026-08-08. Apparent publisher: Naval Postgraduate School, Monterey.

## No verdict is recorded

Retrieval failed twice, on both `https://fast.mfr.nps.edu/` and
`https://fast.mfr.nps.edu`. The host's `robots.txt` could not be fetched or
parsed, so the fetcher refused the request. No page content was obtained.

Public search returned nothing that names this host or expands the acronym.
Searches run: the bare hostname in quotes, FAST plus Naval Postgraduate
School, FAST plus NPS plus acquisition, and FAST plus NPS plus Marine Corps and
force structure. Every result resolved to unrelated NPS pages - admissions, the
Acquisition Research Program, Monterey Phoenix, the Marines-at-NPS page - and
none to this subdomain.

**Nothing is inferred from the URL.** `FAST` has at least a dozen live
expansions in the naval and DoD space, and `mfr` reads as either an
organisational abbreviation or Memorandum For Record. Guessing between them and
writing a verdict on the guess would violate the standing rule that anything not
confirmed against an authoritative source is marked UNCONFIRMED rather than
assumed.

## What would discharge this row

Any one of these, and the review takes ten minutes:

1. Open the site in a browser and paste the landing-page text, the About page,
   and any documentation or API link.
2. State what the acronym expands to and which NPS organisation runs it.
3. Confirm whether it is publicly reachable at all, or CAC-gated. A CAC-gated
   tool is a different verdict from a public one, because a gated source cannot
   be a citable authority for a published artifact regardless of its content.

## The questions the review will ask once it is reachable

Recorded now so the second pass is short.

- Does it hold **documents** or **structure**? A document repository competes
  with, or feeds, `canonical/`. A structure or force-data tool is a different
  axis and most likely NOT APPLICABLE, the way Monterey Phoenix was in
  conformance matrix section 15.
- Does it expose **stable identifiers** for anything it holds? If it does, they
  need checking against the `NAMESPACES.md` grammar for collision, particularly
  in the `/us/dod/don/usmc/` space.
- Is there an **API or bulk export**? Human-in-the-loop acquisition is the
  current constraint recorded in `REFERENCES.md`, and a machine-readable naval
  source would relax it.
- What is its **authority status**? An NPS-hosted tool is a research product,
  not an issuing authority. Nothing from it can promote a record to VERIFIED,
  because verification means confirmed against the issuing authority's copy.

## Verdict

**UNCONFIRMED.** No content retrieved. No verdict recorded. State: OPEN, pending
the input named above.

## Confidence

Not applicable. Confidence is scored on verdicts, and no verdict was reached.
The retrieval failure itself is a matter of record and was reproduced.
