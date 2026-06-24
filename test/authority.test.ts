// authority.test.ts
// Provenance resolution over the authority graph.
//   node --test --experimental-strip-types "test/*.test.ts"

import { test } from "node:test";
import assert from "node:assert/strict";

import { resolveAuthorityChain, provenanceFor } from "../src/authority.ts";
import { loadAuthorityGraph } from "../src/load.node.ts";

const graph = loadAuthorityGraph();

test("the cap provision resolves to the full chain, statute-first", () => {
  const chain = resolveAuthorityChain(graph, "/us/usmc/maradmin/2023/051/p8");
  assert.deepEqual(
    chain.map((n) => n.id),
    [
      "/us/usc/10/701",
      "/us/dod/dodi/1327.06",
      "/us/usmc/maradmin/2023/051",
      "/us/usmc/maradmin/2023/051/p8",
    ]
  );
  assert.equal(chain[0].label, "10 U.S.C. 701");
});

test("an unconfirmed citation resolves to no provenance", () => {
  const p = provenanceFor(
    graph,
    "/us/usmc/maradmin/2023/051/UNCONFIRMED",
    "UNVERIFIED"
  );
  assert.equal(p.asserted, false);
  assert.equal(p.chain.length, 0);
});

test("the window provision is not yet asserted in the authority graph", () => {
  // Known gap: rules.json cites /p8/b/2, but the authority @graph only models
  // /p8. The resolver surfaces the gap honestly rather than inventing a chain.
  const chain = resolveAuthorityChain(graph, "/us/usmc/maradmin/2023/051/p8/b/2");
  assert.equal(chain.length, 0);
});

test("resolution is deterministic", () => {
  const a = resolveAuthorityChain(graph, "/us/usmc/maradmin/2023/051/p8");
  const b = resolveAuthorityChain(graph, "/us/usmc/maradmin/2023/051/p8");
  assert.deepEqual(a, b);
});
