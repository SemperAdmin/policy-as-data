// table.js
// Searchable data table over the whole corpus. A QUERY PROJECTION of the
// structured store: it fetches every *.uslm.xml, walks the provision hierarchy,
// and flattens it to one row per provision — keeping the stable @identifier on
// every row. The structured store stays the source of truth; this is just a view.

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

// Walk one document's provisions into flat rows, recording depth and path.
function flatten(doc, issuance) {
  const out = [];
  const walk = (p, depth) => {
    const numEl = child(p, "num");
    const headingEl = child(p, "heading");
    const contentEl = child(p, "content");
    const text = contentEl
      ? children(contentEl, "p").map((x) => x.textContent.trim()).join(" ")
      : "";
    out.push({
      docId: doc.id,
      docLabel: doc.label,
      issuanceType: issuance.getAttribute("issuanceType"),
      identifier: p.getAttribute("identifier"),
      status: p.getAttribute("status"),
      level: p.getAttribute("level") || "",
      num: numEl ? numEl.textContent.trim() : "",
      heading: headingEl ? headingEl.textContent.trim() : "",
      text,
      depth,
    });
    for (const k of children(p, "paragraph")) walk(k, depth + 1);
  };
  for (const p of children(issuance, "paragraph")) walk(p, 0);
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
  render(rows);
  $("#total").textContent = rows.length;
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
        <td class="doc">${esc(r.docLabel)}</td>
        <td class="num">${esc(r.num)}</td>
        <td class="prov">${snippet(r)}<div class="cid">${esc(r.identifier)}</div></td>
        <td><span class="badge ${r.status}">${r.status}</span></td>
      </tr>`
    )
    .join("");
}

function applyFilter() {
  const q = $("#q").value.trim().toLowerCase();
  const statusFilter = $("#status-filter").value;
  let list = rows;
  if (statusFilter !== "ALL") list = list.filter((r) => r.status === statusFilter);
  if (q) {
    list = list.filter((r) =>
      (r.identifier + " " + r.docLabel + " " + r.heading + " " + r.text + " " + r.num)
        .toLowerCase()
        .includes(q)
    );
  }
  render(list);
}

$("#q").addEventListener("input", applyFilter);
$("#status-filter").addEventListener("change", applyFilter);
load();
