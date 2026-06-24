// types.ts
// Frozen data contract for the policy-as-data proof of concept.
// Worked rule: MARADMIN 051/23, Military Parental Leave Program.
//
// READ-ONLY FOR THE IMPLEMENTING AGENT.
// Encoded rule VALUES live in data/maradmin-051-23.rules.json and are fixed
// inputs. Logic and UI may change. Rule values do not change without recorded
// human approval against a verified source line. See DATA_CONTRACT.md.

/** Whether the rule behind a value is confirmed against the issuance text. */
export type VerificationStatus = "VERIFIED" | "UNVERIFIED";

/** Source pointer carried by every decision and every reason. */
export interface Citation {
  /** Stable identifier for the provision, matching the USLM @identifier. */
  identifier: string; // e.g. "/us/usmc/maradmin/2023/051/p8"
  /** Human-readable locator. */
  label: string; // e.g. "MARADMIN 051/23, para 8"
  /** Verification state of the underlying source line. */
  status: VerificationStatus;
}

/** Qualifying event categories under the MPLP. */
export type QualifyingEventType =
  | "BIRTH"
  | "ADOPTION"
  | "LONG_TERM_FOSTER_PLACEMENT";

/** A single qualifying event tied to the leave entitlement. */
export interface QualifyingEvent {
  type: QualifyingEventType;
  /** ISO 8601 date, e.g. "2026-06-24". */
  date: string;
}

/** Input to the decision function. All fields required. No implicit defaults. */
export interface ParentalLeaveRequest {
  /** Days of parental leave requested in this single submission. */
  requestedDays: number;
  /** Parental leave days already used against this entitlement window. */
  daysAlreadyUsed: number;
  /** The qualifying event or events the entitlement derives from. */
  events: QualifyingEvent[];
  /** ISO 8601 date the requested leave would begin. */
  leaveStartDate: string;
}

/** Outcome categories. UNVERIFIED is a first-class result, not an error. */
export type DecisionOutcome = "APPROVE" | "DENY" | "UNVERIFIED";

/** One reason supporting the outcome. Always carries a citation. */
export interface DecisionReason {
  /** Stable machine code, e.g. "EXCEEDS_84_DAY_CAP". */
  code: string;
  /** Plain-language explanation for a human reader. */
  message: string;
  /** Source provision behind this reason. */
  citation: Citation;
}

/** Return shape of evaluate(). Deterministic for a given input. */
export interface ParentalLeaveDecision {
  outcome: DecisionOutcome;
  /** Non-empty. At least one reason for every outcome, including APPROVE. */
  reasons: DecisionReason[];
  /** True when any binding rule in this evaluation is UNVERIFIED. */
  restsOnUnverifiedRule: boolean;
}

/**
 * The decision function contract.
 *
 * Hard constraints the implementation honors:
 * 1. Pure. No I/O, no network, no model call inside this function.
 * 2. Deterministic. Same input returns the same output, every run.
 * 3. Every reason carries a citation. No bare APPROVE or DENY.
 * 4. Loud failure on unverified rules. When the binding constraint for a
 *    request is an UNVERIFIED rule, the outcome is UNVERIFIED, not DENY or
 *    APPROVE, and restsOnUnverifiedRule is true.
 */
export type EvaluateParentalLeave = (
  request: ParentalLeaveRequest
) => ParentalLeaveDecision;
