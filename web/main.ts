// web/main.ts
// Minimal browser entry point. Fetches the encoded rule set, binds it to the
// engine, and renders a cited decision for a parental leave request.

import type { ParentalLeaveRequest, ParentalLeaveDecision } from "../src/types.ts";
import { asRuleSet } from "../src/ruleset.ts";
import { createEvaluator } from "../src/engine.ts";

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
};

async function boot(): Promise<void> {
  const response = await fetch("./data/maradmin-051-23.rules.json");
  const ruleSet = asRuleSet(await response.json());
  const evaluate = createEvaluator(ruleSet);

  const form = $<HTMLFormElement>("request-form");
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const request: ParentalLeaveRequest = {
      requestedDays: Number($<HTMLInputElement>("requestedDays").value),
      daysAlreadyUsed: Number($<HTMLInputElement>("daysAlreadyUsed").value),
      events: [
        {
          type: $<HTMLSelectElement>("eventType").value as
            ParentalLeaveRequest["events"][number]["type"],
          date: $<HTMLInputElement>("eventDate").value,
        },
      ],
      leaveStartDate: $<HTMLInputElement>("leaveStartDate").value,
    };
    render(evaluate(request));
  });

  // Evaluate the pre-loaded 5-day lead case on first paint.
  form.requestSubmit();
}

function render(decision: ParentalLeaveDecision): void {
  const out = $<HTMLDivElement>("result");
  const badge = `<span class="badge ${decision.outcome}">${decision.outcome}</span>`;
  const loud = decision.restsOnUnverifiedRule
    ? `<p class="loud">This decision rests on an <strong>UNVERIFIED</strong> rule.
       The system will not return DENY or APPROVE until a human confirms the
       source line.</p>`
    : "";
  const reasons = decision.reasons
    .map(
      (r) => `
      <li>
        <code>${r.code}</code>
        <p>${r.message}</p>
        <p class="cite">
          ${r.citation.label}
          <span class="cstatus ${r.citation.status}">${r.citation.status}</span>
          <br /><span class="cid">${r.citation.identifier}</span>
        </p>
      </li>`
    )
    .join("");
  out.innerHTML = `
    <h2>Decision ${badge}</h2>
    ${loud}
    <ol class="reasons">${reasons}</ol>`;
}

boot().catch((err) => {
  document.getElementById("result")!.textContent = String(err);
});
