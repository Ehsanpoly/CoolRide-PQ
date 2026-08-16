#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/coolride-pq-matplotlib}"
mkdir -p "${repo_dir}/generated" "${repo_dir}/docs/media" "${MPLCONFIGDIR}"

python3 -m coolride_pq simulate \
  --json "${repo_dir}/generated/reference-scenario.json" \
  --csv "${repo_dir}/generated/reference-scenario.csv"
python3 -m coolride_pq evidence \
  --json "${repo_dir}/generated/reference-evidence.json" >/dev/null
python3 "${repo_dir}/scripts/render_graphics.py" \
  "${repo_dir}/generated/reference-scenario.json" \
  "${repo_dir}/docs/media"

echo "Generated scenario, evidence and LinkedIn graphics."
