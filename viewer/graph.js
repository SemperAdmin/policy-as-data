// graph.js
// Reference graph across the whole corpus. Reads every *.authority.jsonld, builds
// the cross-document network, and lays it out by authority level (statute at top,
// Marine Corps at the bottom). Edges are typed: cited / inferred authority go
// upward; references / supersedes / clarifies / amends are adjacent. Nodes that
// are encoded documents link into the viewer. Reads the JSON-LD, never a table.

import { DOCS } from "./docs.js";

const $ = (sel) => document.querySelector(sel);

const TYPE_LEVEL = {
  Statute: 1, PublicLaw: 1,
  CodeOfFederalRegulations: 2, ExecutiveOrder: 2,
  DoDDirective: 3, DoDInstruction: 3, DirectiveTypeMemorandum: 3, Memorandum: 3, OpmIssuance: 3,
  NavyIssuance: 4,
  MarineCorpsOrder: 5, ServiceMessage: 5,
};
const LEVEL_NAME = { 1: "Statute", 2: "CFR / Executive Order", 3: "DoD", 4: "Department of the Navy", 5: "Marine Corps", 6: "Referenced (not encoded)" };

const AUTHORITY_EDGES = [
  ["derivesAuthorityFrom", "cited"],
  ["inferredAuthorityFrom", "inferred"],
  ["references", "references"],
  ["supersedes", "supersedes"],
  ["clarifies", "clarifies"],
  ["amends", "amends"],
];

const docRootIds = new Set(DOCS.map((d) => d.id));
const asArray = (v) => (v == null ? [] : Array.isArray(v) ? v : [v]);
const short = (label, id) => (label ? label.split(",")[0].split(".")[0].trim() : id);
const esc = (s) => (s || "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function build() {
  const nodes = new Map(); // id -> {id, label, type, level, encoded}
  const edges = [];

  const register = (id, label, type, canonical) => {
    const level = TYPE_LEVEL[type] || 6;
    const existing = nodes.get(id);
    if (!existing || canonical) {
      nodes.set(id, { id, label: label || existing?.label || id, type: type || existing?.type || "", level, encoded: docRootIds.has(id) });
    }
  };

  await Promise.all(
    DOCS.map(async (doc) => {
      let graph;
      try {
        graph = (await fetch(doc.authority).then((r) => r.json()))["@graph"] || [];
      } catch {
        return;
      }
      for (const n of graph) {
        const t = (n["@type"] || "").replace("pol:", "");
        if (t === "Provision" || t === "Decision") continue; // issuance-level only
        register(n["@id"], n.label, t, n["@id"] === doc.id);
        for (const [key, kind] of AUTHORITY_EDGES) {
          for (const target of asArray(n[key])) {
            edges.push({ from: n["@id"], to: target, kind });
          }
        }
      }
    })
  );

  // Make sure every edge endpoint exists as a node.
  for (const e of edges) {
    for (const id of [e.from, e.to]) if (!nodes.has(id)) register(id, id, "", false);
  }

  layout([...nodes.values()], edges);
}

function layout(nodeList, edges) {
  const W = 1180;
  const levels = [...new Set(nodeList.map((n) => n.level))].sort((a, b) => a - b);
  const rowGap = 150;
  const top = 64;
  const pos = new Map();

  levels.forEach((lvl, li) => {
    const row = nodeList.filter((n) => n.level === lvl).sort((a, b) => short(a.label, a.id).localeCompare(short(b.label, b.id)));
    row.forEach((n, i) => {
      pos.set(n.id, { x: (W * (i + 1)) / (row.length + 1), y: top + li * rowGap, n });
    });
  });

  const H = top + (levels.length - 1) * rowGap + 80;
  const bw = 168, bh = 46;

  // Edges first (under the nodes).
  const edgeSvg = edges
    .map((e) => {
      const a = pos.get(e.from), b = pos.get(e.to);
      if (!a || !b) return "";
      return `<line x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" class="ed ${e.kind}" />`;
    })
    .join("");

  // Row labels on the left.
  const rowLabels = levels
    .map((lvl, li) => `<text x="6" y="${top + li * rowGap - bh / 2 - 6}" class="rowlbl">${esc(LEVEL_NAME[lvl] || "")}</text>`)
    .join("");

  const nodeSvg = [...pos.values()]
    .map(({ x, y, n }) => {
      const label = esc(short(n.label, n.id));
      const cls = `node ${n.encoded ? "enc" : "ext"}`;
      const inner = `
        <rect x="${(x - bw / 2).toFixed(1)}" y="${(y - bh / 2).toFixed(1)}" width="${bw}" height="${bh}" rx="7" class="${cls}" />
        <text x="${x.toFixed(1)}" y="${(y - 3).toFixed(1)}" class="nlbl">${label}</text>
        <text x="${x.toFixed(1)}" y="${(y + 12).toFixed(1)}" class="ntype">${esc(n.type)}${n.encoded ? "" : " · not encoded"}</text>
        <title>${esc(n.label)}\n${esc(n.id)}</title>`;
      return n.encoded
        ? `<a href="./index.html?doc=${encodeURIComponent(n.id)}">${inner}</a>`
        : `<g>${inner}</g>`;
    })
    .join("");

  $("#graph").innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Reference graph">
    ${rowLabels}${edgeSvg}${nodeSvg}
  </svg>`;
  $("#count").textContent = `${pos.size} documents · ${edges.length} references`;
}

build();
