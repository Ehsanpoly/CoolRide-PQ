#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"

python3 -m unittest discover -s "${repo_dir}/tests" -p "test_*.py" -v
"${repo_dir}/scripts/build_cpp.sh"
"${repo_dir}/build/coolride-core-test"
node --check "${repo_dir}/apps/ops-console/dist/main.js"

echo "All Python, C++ and browser-JavaScript checks passed."
