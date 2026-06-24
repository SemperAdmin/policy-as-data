// load.node.ts
// Node-side I/O boundary: read the encoded rule store from disk and hand a
// typed RuleSet to the engine. Kept separate from engine.ts so the engine
// itself never touches the filesystem.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import type { RuleSet } from "./ruleset.ts";
import { asRuleSet } from "./ruleset.ts";

const RULES_PATH = fileURLToPath(
  new URL("../data/maradmin-051-23.rules.json", import.meta.url)
);

/** Load and validate the MARADMIN 051/23 rule set from data/. */
export function loadRuleSet(path: string = RULES_PATH): RuleSet {
  return asRuleSet(JSON.parse(readFileSync(path, "utf8")));
}
