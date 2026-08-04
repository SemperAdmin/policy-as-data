# branding/ — inherited, not owned

This project does not own the visual system. It inherits it.

    SEMPER-STYLE-GUIDE.md   the v1.2 token set, mirrored 2026-05-04
    semper-logo.jpg         the emblem the site ships

## Where the source of truth actually is

`SEMPER-STYLE-GUIDE.md` states its own provenance on line 3: the source of
truth is `src/app/globals.css` in the **SemperAdminPortal** repo, and this file
is a mirror of the v1.2 set. Treat it as read-only. When a token changes, it
changes there and is re-mirrored here — never the reverse, or the two drift and
neither is authoritative.

## Two companion files it names and this folder does not hold

The guide points at `semper-tokens.css` and `semper-tokens.json` as sitting
"next to this one". They are not here, and they were not in the folder this was
taken from. If you want the paste-ready CSS variables or the flat JSON export
for a Tailwind or Style Dictionary config, pull them from SemperAdminPortal.
Stated rather than quietly patched, because inventing them from the tables in
the guide would produce a third copy with no authority behind it.

## The shipped copy of the logo

`docs/semper-logo.jpg` is the copy the site serves, byte-identical to the one
here (`1895252971f8265ca10e67b736f1035e`). This folder holds the brand asset;
`docs/` holds the deployed one. Replacing the emblem means replacing both.

## What the site actually uses

The rendered pages carry the token values inline rather than importing a
stylesheet, so the guide is a register and a reference, not a build input. The
load-bearing values the renderers hardcode:

| | |
|---|---|
| USMC scarlet | `#B82230` |
| marine blue | `#0F1F3D` |
| parchment | `#F2E5BE` |
| brass | `#B89042` |

If those diverge from the guide, the guide is right and the renderers are
stale.
