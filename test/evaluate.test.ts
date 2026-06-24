// evaluate.test.ts
// Baseline behavior of the decision engine, run with Node's built-in test
// runner and native TypeScript type-stripping:
//   node --test --experimental-strip-types "test/*.test.ts"

import { test } from "node:test";
import assert from "node:assert/strict";

import type { ParentalLeaveRequest } from "../src/types.ts";
import type { RuleSet } from "../src/ruleset.ts";
import { evaluate } from "../src/engine.ts";
import { loadRuleSet } from "../src/load.node.ts";

const ruleSet = loadRuleSet();

/** The lead case: a single birth, 5 days requested, none used. */
function fiveDayRequest(): ParentalLeaveRequest {
  return {
    requestedDays: 5,
    daysAlreadyUsed: 0,
    events: [{ type: "BIRTH", date: "2026-06-01" }],
    leaveStartDate: "2026-06-15",
  };
}

test("the rule data matches the frozen contract values", () => {
  const byId = Object.fromEntries(ruleSet.rules.map((r) => [r.id, r]));
  assert.equal(byId["MAX_PARENTAL_LEAVE_DAYS"].value, 84);
  assert.equal(byId["MAX_PARENTAL_LEAVE_DAYS"].status, "VERIFIED");
  assert.equal(byId["ENTITLEMENT_WINDOW_DAYS"].value, 365);
  assert.equal(byId["MIN_INCREMENT_DAYS"].value, 7);
  assert.equal(byId["MIN_INCREMENT_DAYS"].status, "UNVERIFIED");
});

test("5-day request returns UNVERIFIED, not DENY (loud failure)", () => {
  const decision = evaluate(fiveDayRequest(), ruleSet);
  assert.equal(decision.outcome, "UNVERIFIED");
  assert.equal(decision.restsOnUnverifiedRule, true);
  assert.equal(decision.reasons.length, 1);
  assert.equal(decision.reasons[0].code, "BELOW_MIN_INCREMENT");
  // The binding reason names an unconfirmed source line.
  assert.equal(decision.reasons[0].citation.status, "UNVERIFIED");
});

test("over-cap request returns DENY on the VERIFIED 84-day rule", () => {
  const decision = evaluate(
    { ...fiveDayRequest(), requestedDays: 90 },
    ruleSet
  );
  assert.equal(decision.outcome, "DENY");
  assert.equal(decision.restsOnUnverifiedRule, false);
  assert.equal(decision.reasons[0].code, "EXCEEDS_84_DAY_CAP");
  assert.equal(decision.reasons[0].citation.status, "VERIFIED");
});

test("a confirmed cap violation denies even when the increment also fails", () => {
  // 3 days already used 84: total 87 > cap (verified DENY) AND 3 < 7 increment
  // (unverified). The confirmed rule binds; outcome is DENY, not UNVERIFIED.
  const decision = evaluate(
    { ...fiveDayRequest(), requestedDays: 3, daysAlreadyUsed: 84 },
    ruleSet
  );
  assert.equal(decision.outcome, "DENY");
  assert.equal(decision.restsOnUnverifiedRule, false);
});

test("a clean within-cap request APPROVEs with a citation", () => {
  const decision = evaluate(
    { ...fiveDayRequest(), requestedDays: 30 },
    ruleSet
  );
  assert.equal(decision.outcome, "APPROVE");
  assert.equal(decision.restsOnUnverifiedRule, false);
  assert.ok(decision.reasons.length >= 1);
  assert.equal(decision.reasons[0].citation.status, "VERIFIED");
});

test("flips to DENY once a human marks the increment rule VERIFIED", () => {
  // Logic does not change; only the rule's status does. This proves the
  // outcome is governed by the data's verification status, not by code.
  const verifiedRuleSet: RuleSet = {
    ...ruleSet,
    rules: ruleSet.rules.map((r) =>
      r.id === "MIN_INCREMENT_DAYS"
        ? {
            ...r,
            status: "VERIFIED",
            citation: { ...r.citation, status: "VERIFIED" },
          }
        : r
    ),
  };
  const decision = evaluate(fiveDayRequest(), verifiedRuleSet);
  assert.equal(decision.outcome, "DENY");
  assert.equal(decision.restsOnUnverifiedRule, false);
  assert.equal(decision.reasons[0].code, "BELOW_MIN_INCREMENT");
});

test("evaluate is deterministic for a fixed input", () => {
  const a = evaluate(fiveDayRequest(), ruleSet);
  const b = evaluate(fiveDayRequest(), ruleSet);
  assert.deepEqual(a, b);
});
