// table.js
// Searchable data table over the whole corpus. A QUERY PROJECTION of the
// structured store: it fetches every *.uslm.xml, walks the provision hierarchy,
// and flattens it to one row per provision — keeping the stable @identifier on
// every row, plus its document's type, ISO date, and source link. The structured
// store stays the source of truth; this is just a view.

import { DOCS } from "./docs.js";

const USLM_NS = "https://policy.usmc.mil/ns/uslm/1.0";
const $ = (sel) => document.querySelector(sel);

let rows = []; // the projection

function child(el, name) {
  return [...el.children].find((c) => c.localName === name) || null;
}
function children(el, name) {
  return [...el.children].filter((c) => c.localName === name);
}

function flatten(doc, issuance) {
  const meta = child(issuance, "meta");
  const mget = (n) => {
    const e = meta && child(meta, n);
    return e ? e.textContent.trim() : "";
  };
  const date = mget("isoDate");
  const type = issuance.getAttribute("issuanceType");
  const out = [];
  const walk = (p) => {
    const numEl = child(p, "num");
    const headingEl = child(p, "heading");
    const contentEl = child(p, "content");
    const text = contentEl
      ? children(contentEl, "p").map((x) => x.textContent.trim()).join(" ")
      : "";
    out.push({
      docId: doc.id,
      docLabel: doc.label,
      source: doc.source || "",
      type,
      date,
      identifier: p.getAttribute("identifier"),
      status: p.getAttribute("status"),
      num: numEl ? numEl.textContent.trim() : "",
      heading: headingEl ? headingEl.textContent.trim() : "",
      text,
    });
    for (const k of children(p, "paragraph")) walk(k);
  };
  for (const p of children(issuance, "paragraph")) walk(p);
  return out;
}

async function load() {
  const docs = await Promise.all(
    DOCS.map(async (doc) => {
      try {
        const xml = new DOMParser().parseFromString(
          await fetch(doc.uslm).then((r) => r.text()),
          "application/xml"
        );
        const issuance = xml.getElementsByTagNameNS(USLM_NS, "issuance")[0];
        return flatten(doc, issuance);
      } catch {
        return [];
      }
    })
  );
  rows = docs.flat();

  const types = [...new Set(rows.map((r) => r.type))].sort();
  const sel = $("#type-filter");
  for (const t of types) {
    const o = document.createElement("option");
    o.value = t;
    o.textContent = t;
    sel.appendChild(o);
  }

  $("#total").textContent = rows.length;
  applyFilter();
}

function esc(s) {
  return (s || "").replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
}

function snippet(r) {
  const body = r.heading
    ? `<strong>${esc(r.heading)}</strong>${r.text ? " — " + esc(r.text) : ""}`
    : esc(r.text);
  return body.length > 240 ? body.slice(0, 240) + "…" : body;
}

function render(list) {
  $("#shown").textContent = list.length;
  $("#tbody").innerHTML = list
    .map(
      (r) => `
      <tr>
        <td class="doc">${esc(r.docLabel)}
          <div class="docmeta">${esc(r.type)}${r.date ? " · " + r.date : ""}${
        r.source ? ` · <a href="${r.source}" target="_blank" rel="noopener">source&#8599;</a>` : ""
      }</div>
        </td>
        <td class="num">${esc(r.num)}</td>
        <td class="prov">${snippet(r)}<div class="cid">${esc(r.identifier)}</div></td>
        <td><span class="badge ${r.status}">${r.status}</span></td>
      </tr>`
    )
    .join("");
}

function applyFilter() {
  const q = $("#q").value.trim().toLowerCase();
  const status = $("#status-filter").value;
  const type = $("#type-filter").value;
  const sort = $("#sort").value;

  let list = rows;
  if (status !== "ALL") list = list.filter((r) => r.status === status);
  if (type !== "ALL") list = list.filter((r) => r.type === type);
  if (q) {
    list = list.filter((r) =>
      (r.identifier + " " + r.docLabel + " " + r.heading + " " + r.text + " " + r.num)
        .toLowerCase()
        .includes(q)
    );
  }
  if (sort === "date-asc") list = [...list].sort((a, b) => (a.date || "").localeCompare(b.date || ""));
  else if (sort === "date-desc") list = [...list].sort((a, b) => (b.date || "").localeCompare(a.date || ""));

  render(list);
}

for (const [id, evt] of [["q", "input"], ["status-filter", "change"], ["type-filter", "change"], ["sort", "change"]]) {
  $("#" + id).addEventListener(evt, applyFilter);
}
load();
