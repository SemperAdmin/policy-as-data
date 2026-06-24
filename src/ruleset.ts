// ruleset.ts
// Shape of the encoded rule store (data/maradmin-051-23.rules.json) and a
// typed accessor. This module describes the data the engine reads; it does NOT
// embed rule values. Values are loaded at the I/O boundary (Node: fs; browser:
// fetch) and injected into the engine, so evaluate() stays pure.

import type { VerificationStatus, Citation } from "./types.ts";

/** One encoded rule as stored in the rules JSON. */
export interface Rule {
  id: string;
  value: number;
  unit: string;
  status: VerificationStatus;
  citation: Citation;
  note?: string;
}

/** The full encoded rule store for one issuance. */
export interface RuleSet {
  source: {
    identifier: string;
    label: string;
    dtg: string;
    originator: string;
  };
  authorityChain: string[];
  rules: Rule[];
}

/** Stable identifiers for the rules this engine relies on. */
export type RuleId =
  | "MAX_PARENTAL_LEAVE_DAYS"
  | "ENTITLEMENT_WINDOW_DAYS"
  | "MIN_INCREMENT_DAYS"
  | "EVENT_PROXIMITY_MERGE_DAYS";

/**
 * Look up a rule by id. Throws if absent — a missing rule is a packaging
 * error, not a decision input, so it must fail loudly at load/eval time rather
 * than silently change an outcome.
 */
export function getRule(ruleSet: RuleSet, id: RuleId): Rule {
  const rule = ruleSet.rules.find((r) => r.id === id);
  if (!rule) {
    throw new Error(`Rule "${id}" is missing from the rule set.`);
  }
  return rule;
}

/**
 * Narrow an unknown parsed JSON value to a RuleSet, throwing on a shape that
 * cannot drive a decision. Keeps malformed data from reaching the engine.
 */
export function asRuleSet(value: unknown): RuleSet {
  const v = value as RuleSet;
  if (!v || typeof v !== "object" || !Array.isArray(v.rules)) {
    throw new Error("Rule data is not a valid RuleSet.");
  }
  return v;
}
