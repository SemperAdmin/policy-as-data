// engine.ts
// Deterministic, cited decision engine for MARADMIN 051/23 parental leave.
//
// Honors the four hard constraints from types.ts:
//   1. Pure        - no I/O, no network, no clock, no model call in evaluate().
//   2. Deterministic - same (request, ruleSet) always yields the same decision.
//   3. Cited       - every reason carries a Citation.
//   4. Loud failure - when the binding constraint is an UNVERIFIED rule, the
//                     outcome is UNVERIFIED (not DENY, not APPROVE).

import type {
  ParentalLeaveRequest,
  ParentalLeaveDecision,
  DecisionReason,
  EvaluateParentalLeave,
} from "./types.ts";
import type { Rule, RuleSet } from "./ruleset.ts";
import { getRule } from "./ruleset.ts";

/** A failed check, tagged with the rule whose status governs the outcome. */
interface Violation {
  rule: Rule;
  reason: DecisionReason;
}

/** Build a DecisionReason that carries the governing rule's citation. */
function reasonFrom(rule: Rule, code: string, message: string): DecisionReason {
  return { code, message, citation: rule.citation };
}

/** Whole calendar days between two ISO 8601 dates (deterministic, no clock). */
function daysBetween(isoA: string, isoB: string): number {
  const msPerDay = 86_400_000;
  const a = Date.parse(isoA);
  const b = Date.parse(isoB);
  return Math.abs(Math.round((b - a) / msPerDay));
}

/**
 * Count distinct qualifying events after applying the proximity-merge rule:
 * events within `mergeDays` of the running anchor collapse into one event.
 * Deterministic: sorts by ISO date string before merging.
 */
function distinctEventCount(
  request: ParentalLeaveRequest,
  mergeDays: number
): number {
  const dates = request.events.map((e) => e.date).sort();
  if (dates.length <= 1) return dates.length;
  let count = 1;
  let anchor = dates[0];
  for (let i = 1; i < dates.length; i++) {
    if (daysBetween(anchor, dates[i]) > mergeDays) {
      count++;
      anchor = dates[i];
    }
  }
  return count;
}

/**
 * Evaluate a parental leave request against an injected rule set.
 *
 * Pure: all inputs arrive as arguments; nothing is read from disk, network,
 * or the clock. The rule set is passed in so the function never performs I/O.
 */
export function evaluate(
  request: ParentalLeaveRequest,
  ruleSet: RuleSet
): ParentalLeaveDecision {
  const cap = getRule(ruleSet, "MAX_PARENTAL_LEAVE_DAYS");
  const increment = getRule(ruleSet, "MIN_INCREMENT_DAYS");
  const proximity = getRule(ruleSet, "EVENT_PROXIMITY_MERGE_DAYS");

  const violations: Violation[] = [];
  const total = request.requestedDays + request.daysAlreadyUsed;

  // Cap check (VERIFIED rule). Total leave across the window must not exceed 84.
  if (total > cap.value) {
    violations.push({
      rule: cap,
      reason: reasonFrom(
        cap,
        "EXCEEDS_84_DAY_CAP",
        `Requested ${request.requestedDays} day(s) plus ${request.daysAlreadyUsed} already used totals ${total}, exceeding the ${cap.value}-day cap.`
      ),
    });
  }

  // Increment check (UNVERIFIED rule). A request below the minimum increment
  // would deny, but only this rule binds — and its source line is unconfirmed.
  if (request.requestedDays < increment.value) {
    violations.push({
      rule: increment,
      reason: reasonFrom(
        increment,
        "BELOW_MIN_INCREMENT",
        `Requested ${request.requestedDays} day(s) is below the ${increment.value}-day minimum increment.`
      ),
    });
  }

  const verified = violations.filter((v) => v.rule.status === "VERIFIED");
  const unverified = violations.filter((v) => v.rule.status === "UNVERIFIED");

  // A confirmed violation denies, regardless of any unconfirmed rule.
  if (verified.length > 0) {
    return {
      outcome: "DENY",
      reasons: verified.map((v) => v.reason),
      restsOnUnverifiedRule: false,
    };
  }

  // No confirmed violation, but an unconfirmed rule is the binding constraint.
  // Loud failure: the outcome is UNVERIFIED, not DENY.
  if (unverified.length > 0) {
    return {
      outcome: "UNVERIFIED",
      reasons: unverified.map((v) => v.reason),
      restsOnUnverifiedRule: true,
    };
  }

  // Nothing binds against the request: it is within the confirmed cap.
  const reasons: DecisionReason[] = [
    reasonFrom(
      cap,
      "WITHIN_84_DAY_CAP",
      `Requested ${request.requestedDays} day(s) plus ${request.daysAlreadyUsed} already used totals ${total}, within the ${cap.value}-day cap.`
    ),
  ];

  // When more than one qualifying event is present, the entitlement basis
  // depends on the proximity-merge rule, which is UNVERIFIED. Surface that the
  // approval rests on an unconfirmed rule rather than asserting a clean APPROVE.
  let restsOnUnverifiedRule = false;
  if (request.events.length > 1) {
    const distinct = distinctEventCount(request, proximity.value);
    reasons.push(
      reasonFrom(
        proximity,
        "EVENT_PROXIMITY_MERGE_APPLIED",
        `${request.events.length} qualifying events resolve to ${distinct} distinct event(s) under the ${proximity.value}-day proximity-merge rule.`
      )
    );
    restsOnUnverifiedRule = proximity.status === "UNVERIFIED";
  }

  return {
    outcome: restsOnUnverifiedRule ? "UNVERIFIED" : "APPROVE",
    reasons,
    restsOnUnverifiedRule,
  };
}

/**
 * Bind a rule set to produce a function matching the frozen EvaluateParentalLeave
 * contract (request -> decision). The returned closure performs no I/O.
 */
export function createEvaluator(ruleSet: RuleSet): EvaluateParentalLeave {
  return (request) => evaluate(request, ruleSet);
}
