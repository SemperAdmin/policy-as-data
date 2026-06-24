// web/main.ts
// Minimal browser entry point. Fetches the encoded rule set, binds it to the
// engine, and renders a cited decision for a parental leave request.

import type { ParentalLeaveRequest, ParentalLeaveDecision } from "../src/types.ts";
import { asRuleSet } from "../src/ruleset.ts";
import { createEvaluator } from "../src/engine.ts";
import type { AuthorityGraph } from "../src/authority.ts";
import { asAuthorityGraph, provenanceFor } from "../src/authority.ts";

const $ = <T extends HTMLElement>(id: string): T => {
  const el = document.getElementById(id);
  if (!el) throw new Error(`Missing element #${id}`);
  return el as T;
};

let authority: AuthorityGraph;

async function boot(): Promise<void> {
  const [rulesRes, authRes] = await Promise.all([
    fetch("./data/maradmin-051-23.rules.json"),
    fetch("./data/maradmin-051-23.authority.jsonld"),
  ]);
  const ruleSet = asRuleSet(await rulesRes.json());
  authority = asAuthorityGraph(await authRes.json());
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
    .map((r) => {
      const prov = provenanceFor(
        authority,
        r.citation.identifier,
        r.citation.status
      );
      const chain = prov.asserted
        ? `<p class="chain">${prov.chain
            .map((n) => `<span>${n.label}</span>`)
            .join(" → ")}</p>`
        : `<p class="chain none">No authority chain asserted for this citation.</p>`;
      return `
      <li>
        <code>${r.code}</code>
        <p>${r.message}</p>
        <p class="cite">
          ${r.citation.label}
          <span class="cstatus ${r.citation.status}">${r.citation.status}</span>
          <br /><span class="cid">${r.citation.identifier}</span>
        </p>
        ${chain}
      </li>`;
    })
    .join("");
  out.innerHTML = `
    <h2>Decision ${badge}</h2>
    ${loud}
    <ol class="reasons">${reasons}</ol>`;
}

boot().catch((err) => {
  document.getElementById("result")!.textContent = String(err);
});
