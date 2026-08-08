# 19. NIST usnistgov/ocr-pipeline - NOT APPLICABLE to this repository

Source: <https://code.nist.gov/repo/#/usnistgov/ocr-pipeline>, which is a
client-rendered view over <https://github.com/usnistgov/ocr-pipeline>.
Retrieved 2026-08-08. Publisher: National Institute of Standards and Technology.

**Retrieval note.** The `code.nist.gov` URL is a single-page application. Server
retrieval returns the unrendered template, with `{{ repo.name }}` and
`{{ repo.licenseInfo.spdxId }}` still in place. Everything below comes from the
GitHub README, which is the actual source of record. Cite the GitHub URL, not
the portal fragment, or the citation resolves to a template.

## What it is

> "Convert a corpus of PDF to clean text files on a distributed architecture"

Three stages: PDF to PNG with PythonMagick, PNG to TXT with Ocropy, then a
cleaning pass "in order to remove all trace of garbage strings." A master reads
input files into a Redis queue. Workers pull jobs off it. Input at `data.in`,
output at `data.out`.

Dependencies: ImageMagick, Ghostscript, Ocropy, NLTK English tokenizer, Redis
2.7 or later, `xvfb-run`. Python 2.7. Linux only.

## Why it does not apply here

`README.md` states the boundary plainly: this project was extracted from
GunnyBot, and "GunnyBot keeps the factory - acquisition, extraction, and the
full corpus." This repository owns the standard, the schema, the renderers, the
demonstration corpus, and the site. An OCR pipeline is factory equipment. It has
no read-path role, touches no schema, and produces nothing this repository would
accept, because everything it emits would enter at UNVERIFIED and this project
does not run extraction.

`HANDOFF.md` holds that line. Nothing in this source moves it.

## The finding that matters more than the verdict

**The stack is dead, and adopting it would be a defect.**

- Python 2.7 reached end of life on 1 January 2020. It has received no security
  patch since.
- Ocropy, the OCR engine, was superseded by OCRopus 3 / ocropus2 and then
  effectively abandoned. It is not a live project.
- PythonMagick has no maintained wheel for current Python.

Any 2026 pipeline solving the same problem would use Tesseract 5 with a modern
layout model, or a transformer-based document-understanding model, and would not
route through a PNG intermediate unless the source is genuinely scanned. This
source is a 2016-era reference architecture, not a component to install.

That said, the *architecture* is sound and its shape is worth keeping: a queue
between a reader and a pool of workers, with a distinct cleaning stage that is
separately testable. That is the correct decomposition, and it is the part to
carry to GunnyBot, not the code.

## Where it is genuinely relevant

`REFERENCES.md` records a live blocker in exactly this space:

> The PDF provided is a **scanned image** with no text layer; cannot extract
> here. Please paste the text.

That is `/us/dod/don/asn-mra/2023/mplp-guidance`, MARADMIN 051/23 reference (b),
blocked on OCR. This source is the right *category* of solution for that
blocker and the wrong *instance*. Solving it needs a current OCR path, run
inside GunnyBot, with output entering this repository at UNVERIFIED and
promoted only after line-by-line confirmation. The two-tier discipline already
covers that case and needs no change.

## License and reuse

NIST software is not subject to copyright in the United States under
17 U.S.C. 105, and the standard NIST statement grants use, copying, and
redistribution provided the notice is kept intact, with modified versions
required to carry notice of the change. Detail is in section 20. If any code
from this repository were ever vendored, that notice travels with it. Nothing is
vendored today.

## Verdict

**NOT APPLICABLE to this repository.** It is acquisition-side, and acquisition
belongs to GunnyBot. Recorded here so that the boundary is documented rather
than assumed, and so the dead-stack finding is not re-found.

## Confidence

0.9. README retrieved and quoted. End-of-life dates for Python 2.7 are matters
of record. Ocropy's abandonment is a characterisation from the absence of
maintenance rather than a maintainer statement, and is marked as such.
