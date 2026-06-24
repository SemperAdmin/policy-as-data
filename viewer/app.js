// policy-as-data viewer
//
// Read-only visualization. It fetches the encoded data files and renders them:
//   - data/*.uslm.xml          -> the policy as a navigable, badged document
//   - data/*.authority.jsonld  -> the authority chain shown on click
//   - data/*.rules.json        -> the machine-readable value behind a provision
// No policy logic, no decisions. The data is the product; this only shows it.

const USLM_NS = "https://policy.usmc.mil/ns/uslm/1.0";

const DOCS = [
  {
    id: "/us/usmc/maradmin/2023/051",
    label: "MARADMIN 051/23",
    uslm: "../data/maradmin-051-23.uslm.xml",
    authority: "../data/maradmin-051-23.authority.jsonld",
    rules: "../data/maradmin-051-23.rules.json",
  },
  {
    id: "/us/usmc/maradmin/2023/129",
    label: "MARADMIN 129/23 · Clarification",
    uslm: "../data/maradmin-129-23.uslm.xml",
    authority: "../data/maradmin-129-23.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/maradmin/2022/523",
    label: "MARADMIN 523/22 · RC Leave",
    uslm: "../data/maradmin-523-22.uslm.xml",
    authority: "../data/maradmin-523-22.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dtm/2023/23-001",
    label: "DTM 23-001 · OSD",
    uslm: "../data/dtm-23-001.uslm.xml",
    authority: "../data/dtm-23-001.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dodi/1327.06",
    label: "DoDI 1327.06 · DoD",
    uslm: "../data/dodi-1327.06.uslm.xml",
    authority: "../data/dodi-1327.06.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/dod/dodd/5124.02",
    label: "DoDD 5124.02 · DoD",
    uslm: "../data/dodd-5124.02.uslm.xml",
    authority: "../data/dodd-5124.02.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/navy/asn-mra/2023/mplp-guidance",
    label: "ASN (M&RA) memo · Navy",
    uslm: "../data/asn-mra-2023-mplp-guidance.uslm.xml",
    authority: "../data/asn-mra-2023-mplp-guidance.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/navy/asn-mra/2021/retiree-council-response",
    label: "ASN Retiree Council memo (standalone)",
    uslm: "../data/asn-mra-2021-retiree-council-response.uslm.xml",
    authority: "../data/asn-mra-2021-retiree-council-response.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usc/10/701",
    label: "10 U.S.C. 701 · Statute",
    uslm: "../data/usc-10-701.uslm.xml",
    authority: "../data/usc-10-701.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usc/10/1052",
    label: "10 U.S.C. 1052 · Statute",
    uslm: "../data/usc-10-1052.uslm.xml",
    authority: "../data/usc-10-1052.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/mco/5000.12F",
    label: "MCO 5000.12F · Order",
    uslm: "../data/mco-5000-12F.uslm.xml",
    authority: "../data/mco-5000-12F.authority.jsonld",
    rules: null,
  },
  {
    id: "/us/usmc/mco/1050.3J",
    label: "MCO 1050.3J · Order",
    uslm: "../data/mco-1050-3J.uslm.xml",
    authority: "../data/mco-1050-3J.authority.jsonld",
    rules: null,
  },
];

const $ = (sel) => document.querySelector(sel);

const state = {
  authorityById: new Map(), // @id -> node
  ruleByCitation: new Map(), // citation identifier -> rule
  issuanceId: null,
};

function child(el, localName) {
  return [...el.children].find((c) => c.localName === localName) || null;
}
function children(el, localName) {
  return [...el.children].filter((c) => c.localName === localName);
}

async function loadDoc(doc) {
  $("#document").classList.add("loading");
  try {
    const [xmlText, authority, rules] = await Promise.all([
      fetch(doc.uslm).then((r) => r.text()),
      fetch(doc.authority).then((r) => r.json()),
      doc.rules ? fetch(doc.rules).then((r) => r.json()) : Promise.resolve(null),
    ]);

    state.authorityById = new Map(
      (authority["@graph"] || []).map((n) => [n["@id"], n])
    );
    state.ruleByCitation = new Map(
      (rules?.rules || []).map((r) => [r.citation.identifier, r])
    );

    const xml = new DOMParser().parseFromString(xmlText, "application/xml");
    if (xml.querySelector("parsererror")) throw new Error("XML parse error");
    const issuance = xml.getElementsByTagNameNS(USLM_NS, "issuance")[0];
    state.issuanceId = issuance.getAttribute("identifier");

    renderMeta(issuance);
    renderBody(issuance);
    resetPanel();
  } catch (err) {
    $("#doc-body").innerHTML = `<li class="err">Could not load ${doc.uslm}: ${err.message}.
      Serve the repo root over HTTP (see the README) — fetch() will not read file://.</li>`;
  }
}

function renderMeta(issuance) {
  const meta = child(issuance, "meta");
  const get = (n) => (child(meta, n)?.textContent || "").trim();
  const derives = children(meta, "derivesFrom").map((d) => d.getAttribute("href"));
  const when = get("dtg") || get("date");
  const signer = get("signer");
  $("#doc-meta").innerHTML = `
    <div class="subject">${escapeHtml(get("subject"))}</div>
    <div class="kv">
      ${issuance.getAttribute("issuanceType")} ·
      <code>${issuance.getAttribute("identifier")}</code> ·
      ${when} · ${get("originator")}${signer ? ` · signed ${signer}` : ""}
    </div>
    <div class="kv">derives authority from: ${derives.map((d) => `<code>${d}</code>`).join(" , ") || "—"}</div>`;
}

function renderBody(issuance) {
  const body = $("#doc-body");
  body.innerHTML = "";
  for (const p of children(issuance, "paragraph")) body.appendChild(renderProvision(p));
}

function renderProvision(p) {
  const li = document.createElement("li");
  const id = p.getAttribute("identifier");
  const status = p.getAttribute("status");
  const numEl = child(p, "num");
  const num = numEl ? numEl.textContent.trim() : "";
  const heading = child(p, "heading")?.textContent.trim();
  const contentEl = child(p, "content");
  const paras = contentEl ? children(contentEl, "p").map((x) => x.textContent.trim()) : [];

  const row = document.createElement("div");
  row.className = "prov";
  row.dataset.id = id;
  row.innerHTML = `
    <div class="num">${num}</div>
    <div class="body">
      ${heading ? `<div class="heading">${heading}<span class="dot ${status}" title="${status}"></span></div>` : ""}
      ${paras.map((t) => `<p class="text">${escapeHtml(t)}</p>`).join("")}
      ${!heading && paras.length === 0 ? `<span class="dot ${status}"></span>` : ""}
    </div>`;
  row.addEventListener("click", (e) => {
    e.stopPropagation();
    selectProvision(id, status, heading, paras.join(" "));
  });
  li.appendChild(row);

  const kids = children(p, "paragraph");
  if (kids.length) {
    const ol = document.createElement("ol");
    ol.className = "children";
    for (const k of kids) ol.appendChild(renderProvision(k));
    li.appendChild(ol);
  }
  return li;
}

function selectProvision(id, status, heading, text) {
  document.querySelectorAll(".prov.selected").forEach((n) => n.classList.remove("selected"));
  document.querySelector(`.prov[data-id="${cssEscape(id)}"]`)?.classList.add("selected");

  const rule = state.ruleByCitation.get(id);
  const panel = $("#panel");
  panel.innerHTML = `
    <h2>Provision</h2>
    <div><span class="badge ${status}">${status}</span> ${heading ? `<strong>${heading}</strong>` : ""}</div>
    <div class="cid">${id}</div>
    <p class="prov-text">${escapeHtml(text) || "<em>(container provision)</em>"}</p>
    ${rule ? renderRule(rule) : ""}
    <h2>Authority chain</h2>
    ${renderChain(id)}`;
}

function renderRule(rule) {
  return `
    <h2>Extracted value</h2>
    <div class="rule-card">
      <div class="val">${rule.value} <small>${rule.unit}</small></div>
      <div class="rid">${rule.id} · <span class="badge ${rule.status}">${rule.status}</span></div>
      ${rule.note ? `<div class="note">${escapeHtml(rule.note)}</div>` : ""}
    </div>`;
}

// Build the chain: provision -> its issuance -> authorities above it, to statute.
function renderChain(provId) {
  const items = [];
  items.push(`<li><span class="lbl">${labelFor(provId)}</span>
    <span class="type">this provision</span></li>`);

  const seen = new Set();
  const walk = (nodeId, edgeLabel, edgeClass) => {
    if (!nodeId || seen.has(nodeId)) return;
    seen.add(nodeId);
    const node = state.authorityById.get(nodeId);
    const label = node?.label?.split(".")[0] || nodeId;
    const type = node ? typeOf(node) : "";
    items.push(`<li>
      ${edgeLabel ? `<span class="edge ${edgeClass}">${edgeLabel}</span> ` : ""}
      <span class="lbl">${label}</span>
      <span class="type">${type} · ${nodeId}</span></li>`);
    if (!node) return;
    for (const up of asArray(node.derivesAuthorityFrom)) walk(up, "cited", "cited");
    for (const up of asArray(node.inferredAuthorityFrom)) walk(up, "inferred", "inferred");
  };

  // Every provision inherits the authority of the issuance it belongs to.
  walk(state.issuanceId, "part of", "references");
  return `<ol class="chain">${items.join("")}</ol>`;
}

function labelFor(id) {
  return state.authorityById.get(id)?.label?.split(".")[0] || id;
}
function typeOf(node) {
  return (node["@type"] || "").replace("pol:", "");
}
function asArray(v) {
  return v == null ? [] : Array.isArray(v) ? v : [v];
}

function resetPanel() {
  $("#panel").innerHTML = `<p class="hint">Select any provision to see its
    verification status, its extracted machine-readable value, and its chain of
    authority up to statute.</p>`;
}

function escapeHtml(s) {
  return (s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}
function cssEscape(s) {
  return (window.CSS && CSS.escape) ? CSS.escape(s) : s.replace(/["\\]/g, "\\$&");
}

function buildPicker() {
  const nav = $("#doc-picker");
  DOCS.forEach((doc, i) => {
    const b = document.createElement("button");
    b.textContent = doc.label;
    b.addEventListener("click", () => {
      nav.querySelectorAll("button").forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      loadDoc(doc);
    });
    if (i === 0) b.classList.add("active");
    nav.appendChild(b);
  });
}

buildPicker();
loadDoc(DOCS[0]);
