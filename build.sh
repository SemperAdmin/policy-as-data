#!/usr/bin/env bash
#
# Build the policy-as-data site and machine outputs from this project's own
# corpus. No other project needs to be present.
#
# Every stage is idempotent. Running twice produces identical counts, because
# each stage removes its own prior output before writing.
#
# Layout this assumes, and nothing else:
#   canonical/      the corpus of record for this project, one JSON per document
#   config/         spines, the curated family manifest, the local id index
#   schema/         the JSON contract and the published XSD
#   docs/           the rendered site (GitHub Pages serves this)
#   data/exports/   the XML the site is derived from
#
set -euo pipefail
cd "$(dirname "$0")"

SRC=canonical
IDX=config/store_ids.json
CFG=config/spines.json
FAM=config/mos-family-manifest.json
SITE=docs

echo "### 1  refresh the local id index"
python3 - <<'PY'
import os, json
ids = sorted(f[:-5] for f in os.listdir("canonical") if f.endswith(".json"))
json.dump(ids, open("config/store_ids.json", "w"), indent=1)
print(f"    {len(ids)} record(s)")
PY

echo "### 2  rebuild provision trees from stored section text"
python3 tools/reparse_provisions.py --src "$SRC" --out "$SRC" | tail -2

echo "### 3  mint the statute and DoD tier records"
python3 tools/ingest_authority_tiers.py --out "$SRC" | tail -2

echo "### 4  extract cited authority edges"
python3 tools/extract_authority.py --src "$SRC" --out "$SRC" \
        --store-index "$IDX" --revision-index config/revision_index.json \
        --report config/authority_report.json | head -5

echo "### 5  normalize identifiers (remove the period USLM reserves)"
python3 tools/normalize_identifiers.py --src "$SRC" --out "$SRC" | tail -1

echo "### 6  recover subjects from naval letter front matter"
python3 tools/backfill_subjects.py --src "$SRC" --out "$SRC" | tail -1

echo "### 7  authority chain pages"
python3 tools/render_authority_chain.py --store "$SRC" --out "$SITE" --config "$CFG" \
        | grep -E "seed=|index ->"

echo "### 8  integrated policy pages and type indexes"
python3 tools/render_policy.py --store "$SRC" --out "$SITE" --config "$CFG" --families "$FAM" \
        | head -6

echo "### 9  connection network"
python3 tools/render_connections.py --store "$SRC" --out "$SITE"

echo "### 10 sources page"
python3 tools/render_sources.py --store "$SRC" --out "$SITE"

echo "### 11 issuance XML, validated against the published schema"
python3 tools/export_issuance.py --src "$SRC" --out data/exports --validate | tail -7

echo "### 12 DCAT-US 3.0 catalog"
python3 tools/emit_dcat.py --store "$SRC" --out "$SITE/data.json" \
        --base-url https://semperadmin.github.io/policy-as-data | head -2

echo "### 13 search index, from this project's own corpus"
python3 tools/build_search.py --src "$SRC" --out "$SITE/search"

echo "### 14 verify"
python3 tools/verify_authority.py "$SRC" "$IDX" | tail -3

echo "### 15 verification status, derived from the attestation ledger"
# Reads two inputs and writes nothing, so it is idempotent by construction.
# Fails the build only on INVALIDATED - an attestation whose content changed
# since a human confirmed it. QUORUM_SHORT and UNVERIFIED are reported, not
# fatal; most of the corpus is unverified and that is stated, not hidden.
#
# MOVE THIS AHEAD OF STAGE 7 when per-provision verification badges are
# rendered. A badge is a published claim, and publishing a stale one is the
# defect this stage exists to prevent.
python3 tools/verify_status.py --fail-on-invalidated | tail -4

echo "### 16 cross-tier rule reconciliation"
# Compares values carrying the same concept across authority tiers. Reads
# data/*.rules.json, config/rule_concepts.json, config/units.json, and the
# attestation ledger; writes one report. Idempotent: same inputs, same bytes.
#
# A value that is not VERIFIED is withheld and the verdict becomes
# NOT_COMPARABLE - decision B1, 2026-08-08. Until the DoD tier of the parental
# leave concept is read and attested, this stage reports NOT_COMPARABLE and
# that is the correct output, not a failure.
python3 tools/reconcile.py --out config/reconciliation.json | tail -6

echo "### 17 verification page - queue, worked examples, and the process"
# Renders from the ledger and the rule store by importing verify_status and
# reconcile. It does not re-decide status, quorum, or verdicts; a fourth
# implementation of those rules is how they drift apart.
python3 tools/render_verification.py

echo "### 18 check the site actually works"
python3 tools/check_site.py "$SITE" index.html | tail -12
