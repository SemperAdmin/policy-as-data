# policy-as-data

Structured-data representation of policy and doctrine, with a deterministic, cited decision engine. Proof of concept on one Marine Corps administrative rule.

The worked rule is **MARADMIN 051/23** (Military Parental Leave Program). The
engine reads policy encoded as data, returns a decision with a citation for
every reason, and — when the binding rule is not yet confirmed against the
issuance text — refuses to bluff: it returns `UNVERIFIED` rather than a
confident wrong `DENY` or `APPROVE`. See [`DATA_CONTRACT.md`](./DATA_CONTRACT.md)
for the read-only data mandate and the verification legend.

## Layout

```
data/    encoded policy: rules (JSON), document structure (USLM XML), authority graph (JSON-LD)
src/     types.ts (frozen contract), engine.ts (pure evaluate), ruleset.ts, load.node.ts
test/    behavior of the engine (Node built-in test runner)
web/     minimal browser UI (main.ts)
index.html
```

The data in `data/` is a fixed input. Logic and UI change; encoded rule values
do not change without recorded human approval against a verified source line.

## Quickstart

Requires Node 22.6+ (uses native TypeScript type-stripping for tests).

```bash
npm install        # one dev dependency set: typescript + @types/node
npm test           # run the engine tests
npm run dev        # build the web bundle and serve at http://localhost:8000
```

## The lead case

A 5-day request is below the asserted 7-day minimum increment. That increment
rule (`MIN_INCREMENT_DAYS`) is `UNVERIFIED` — its source line is not yet
located — so the engine returns **`UNVERIFIED`**, names the unconfirmed rule,
and sets `restsOnUnverifiedRule: true`. It flips to `DENY` only after a human
marks the rule `VERIFIED` in the data. No code change is needed for that flip;
the outcome is governed by the data's verification status.
