// policy-as-data viewer
//
// Read-only visualization. It fetches the encoded data files and renders them:
//   - data/*.uslm.xml          -> the policy as a navigable, badged document
//   - data/*.authority.jsonld  -> the authority chain shown on click
//   - data/*.rules.json        -> the machine-readable value behind a provision
// No policy logic, no decisions. The data is the product; this only shows it.

import { DOCS } from "./docs.js";

const USLM_NS = "https://policy.usmc.mil/ns/uslm/1.0";

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

async function loadDoc(doc, selectProvId) {
  $("#document").classList.add("loading");
  state.doc = doc;
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
    if (selectProvId) selectById(selectProvId);
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
  const iso = get("isoDate");
  const signer = get("signer");
  const source = state.doc?.source;
  $("#doc-meta").innerHTML = `
    <div class="subject">${escapeHtml(get("subject"))}</div>
    <div class="kv">
      ${issuance.getAttribute("issuanceType")} ·
      <code>${issuance.getAttribute("identifier")}</code> ·
      ${when}${iso ? ` <span class="iso">(${iso})</span>` : ""} · ${get("originator")}${signer ? ` · signed ${signer}` : ""}
      ${source ? ` · <a class="src" href="${source}" target="_blank" rel="noopener">source&nbsp;&#8599;</a>` : ""}
    </div>
    <div class="kv">derives authority from: ${derives.map((d) => refLink(d, labelFor(d))).join(" , ") || "—"}</div>`;
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
    ${renderChain(id)}
    ${renderRelated()}`;
}

// Outgoing reference-type links of the current issuance, as clickable links.
function renderRelated() {
  const node = state.authorityById.get(state.issuanceId);
  if (!node) return "";
  const groups = [
    ["references", "references"],
    ["clarifies", "clarifies"],
    ["supersedes", "supersedes"],
    ["amends", "amends"],
  ];
  const parts = [];
  for (const [key, label] of groups) {
    const ids = asArray(node[key]);
    if (ids.length) {
      parts.push(
        `<div class="rel"><span class="edge ${key}">${label}</span> ${ids
          .map((id) => refLink(id, labelFor(id)))
          .join(", ")}</div>`
      );
    }
  }
  return parts.length ? `<h2>Related documents</h2>${parts.join("")}` : "";
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
      <span class="lbl">${refLink(nodeId, label)}</span>
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

// Which encoded document owns an identifier (root id, or a provision under it).
function docForIdentifier(id) {
  if (!id) return null;
  return DOCS.find((d) => id === d.id || id.startsWith(d.id + "/")) || null;
}

// A clickable link if the identifier resolves to an encoded document; else plain.
function refLink(id, text) {
  const label = text || id;
  if (!docForIdentifier(id)) return `<code>${escapeHtml(id)}</code>`;
  return `<a class="reflink" data-ref="${escapeHtml(id)}" href="./index.html?doc=${encodeURIComponent(
    id
  )}" title="${escapeHtml(id)}">${escapeHtml(label)}</a>`;
}

// Scroll to a provision in the current document and select it.
function selectById(provId) {
  const row = document.querySelector(`.prov[data-id="${cssEscape(provId)}"]`);
  if (row) {
    row.scrollIntoView({ behavior: "smooth", block: "center" });
    row.click();
  }
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

const pickerButtons = new Map();

function buildPicker() {
  const nav = $("#doc-picker");
  DOCS.forEach((doc) => {
    const b = document.createElement("button");
    b.textContent = doc.label;
    b.addEventListener("click", () => selectDoc(doc));
    pickerButtons.set(doc.id, b);
    nav.appendChild(b);
  });
}

function selectDoc(doc, provId) {
  pickerButtons.forEach((b) => b.classList.remove("active"));
  pickerButtons.get(doc.id)?.classList.add("active");
  loadDoc(doc, provId);
}

// Follow a reference to another document (and optionally a provision within it).
function navigateTo(id) {
  const doc = docForIdentifier(id);
  if (!doc) return;
  const provId = id !== doc.id ? id : null;
  selectDoc(doc, provId);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// Delegated handler so every rendered reference link navigates in place.
document.addEventListener("click", (e) => {
  const a = e.target.closest(".reflink");
  if (a) {
    e.preventDefault();
    navigateTo(a.dataset.ref);
  }
});

function boot() {
  buildPicker();
  const params = new URLSearchParams(location.search);
  const docId = params.get("doc");
  const provId = params.get("prov");
  const doc = (docId && docForIdentifier(docId)) || DOCS[0];
  const target = provId || (docId && docId !== doc.id ? docId : null);
  selectDoc(doc, target);
}

boot();
