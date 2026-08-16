#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${repo_dir}/src${PYTHONPATH:+:${PYTHONPATH}}"

python3 -m unittest discover -s "${repo_dir}/tests" -p "test_*.py" -v
bash "${repo_dir}/scripts/build_cpp.sh"
test_binary="${repo_dir}/build/coolride-core-test"

echo "Test host: $(uname -s) $(uname -m)"
if command -v file >/dev/null 2>&1; then
  file "${test_binary}"
  if [[ "$(uname -s)" == "Linux" ]] && ! file "${test_binary}" | grep -q "ELF"; then
    echo "Expected a native Linux ELF test binary. Check the CXX compiler setting." >&2
    exit 126
  fi
fi

"${test_binary}"
node --check "${repo_dir}/apps/ops-console/dist/main.js"

echo "All Python, C++ and browser-JavaScript checks passed."
