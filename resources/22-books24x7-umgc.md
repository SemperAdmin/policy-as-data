# 22. Books24x7 title via UMGC EZproxy - UNCONFIRMED, stub

Source, as supplied:

```
http://ezproxy.umgc.edu/login?url=http://library.books24x7.com.ezproxy.umgc.edu/library.asp?%5EB&bookID=166577
```

Attempted 2026-08-08. Platform: Skillsoft Books24x7, reached through University
of Maryland Global Campus EZproxy.

## No verdict is recorded

The link is an authenticated proxy redirect. It resolves only for a signed-in
UMGC account, and automated retrieval of authenticated URLs is refused. No
bibliographic metadata is recoverable from the URL itself: `bookID=166577` is a
vendor-internal key with no public resolver, and a search for it returned only
generic library guides for the platform.

**The title is unknown.** Nothing about the book's subject, author, edition, or
relevance can be stated, and nothing is inferred from the fact that it was
supplied alongside four policy-encoding sources.

## Why the link is unusable as a citation regardless of content

This is the finding that survives even after the book is identified, so record
it now.

1. **It is institution-scoped.** The `ezproxy.umgc.edu` prefix binds the link to
   one university's subscription. Any reader outside UMGC gets a login wall. A
   citation in a published artifact must resolve for the reader, and this one
   does not.
2. **It is session-scoped.** EZproxy login URLs are not durable. They break when
   the institution changes proxy configuration or when the vendor re-platforms.
3. **The platform is a moving target.** Books24x7 is a Skillsoft product and has
   been re-branded and re-hosted more than once. A vendor `bookID` is the least
   stable identifier available for a book.

**Rule for this project:** cite the book, not the proxy. A reference entry needs
title, author, publisher, year, edition, and ISBN or DOI. The EZproxy link may
sit beside those as a convenience note for you, never in place of them.

## Fill this in

Open the link and supply these. The entry gets written from them.

| Field | Value |
|---|---|
| Title | |
| Author(s) | |
| Publisher | |
| Year / edition | |
| ISBN | |
| Chapters relevant to this project | |
| Why it was added to the register | |

Once those exist, the review answers three questions and takes one pass:

- Does it assert anything about **markup, identifiers, or legal-document
  structure** that contradicts a ruling already in `NAMESPACES.md` or
  `conformance-matrix.md`? A contradiction is a finding. Agreement is not.
- Is it **primary or secondary**? A textbook is secondary by construction, so it
  can inform a design decision but can never be the text a verdict turns on.
  The standing rule is primary sources only.
- Is it **current**? Books24x7 carries a long backlist. A pre-2015 technical
  title on XML or data architecture is a historical reference, and section 11 of
  the conformance matrix already set the precedent for how those are handled:
  doctrinal ancestor, live descendants are what bind.

## Verdict

**UNCONFIRMED, stub.** Authenticated source, not retrievable. State: OPEN,
pending the table above.

## Confidence

Not applicable. No verdict was reached.
