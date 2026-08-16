#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"

exec python3 -m coolride_pq serve --host "${COOLRIDE_HOST:-127.0.0.1}" --port "${COOLRIDE_PORT:-8080}"
