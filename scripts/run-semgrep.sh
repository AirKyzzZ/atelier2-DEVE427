#!/usr/bin/env bash
# Run the project's custom Semgrep ruleset (Atelier 4) and print a
# concise findings summary. Falls back to JSON output for CI use.
#
# Usage:
#   ./scripts/run-semgrep.sh           # human summary
#   ./scripts/run-semgrep.sh --json    # machine-readable JSON
#
# The custom rules live in semgrep.yml at the repo root and are
# intentionally narrower than the public Semgrep registry — they
# target the precise STRIDE findings of Atelier 4.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v semgrep >/dev/null 2>&1; then
  echo "semgrep is not installed. Install it with: brew install semgrep" >&2
  exit 1
fi

OUTPUT_JSON="${SEMGREP_OUTPUT:-/tmp/semgrep-tma.json}"

SEMGREP_NO_TELEMETRY=1 semgrep \
  --config semgrep.yml \
  --json \
  --metrics=off \
  --exclude=node_modules \
  --exclude=.next \
  --exclude=.contentlayer \
  --exclude=tests \
  --exclude=presentation \
  --exclude=docs \
  --exclude=.scannerwork \
  --exclude=public \
  --exclude=playwright-report \
  --exclude=test-results \
  app components lib hooks types middleware.ts env.mjs \
  > "$OUTPUT_JSON" 2>/dev/null || {
    echo "semgrep scan failed — see $OUTPUT_JSON" >&2
    exit 1
  }

if [[ "${1:-}" == "--json" ]]; then
  cat "$OUTPUT_JSON"
  exit 0
fi

python3 - "$OUTPUT_JSON" <<'PY'
import json, sys
from collections import Counter

with open(sys.argv[1]) as f:
    data = json.load(f)

findings = data.get("results", [])
print(f"Semgrep — {len(findings)} findings sur {len(data['paths']['scanned'])} fichiers scannés")
print()

if not findings:
    print("(aucune vulnérabilité custom détectée)")
    sys.exit(0)

by_class = Counter(f["extra"].get("metadata", {}).get("severity-class", "?")
                   for f in findings)
print("Sévérités :", dict(by_class))
print()

for i, f in enumerate(findings, 1):
    rule = f["check_id"].split(".")[-1]
    cls = f["extra"].get("metadata", {}).get("severity-class", "?")
    stride = f["extra"].get("metadata", {}).get("stride", "?")
    print(f"{i:2d}. [{cls:8s}] [{stride}]  {rule}")
    print(f"      {f['path']}:{f['start']['line']}")
    print()
PY
