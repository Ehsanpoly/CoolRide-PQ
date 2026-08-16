#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ops_console_dir="${repo_dir}/apps/ops-console"
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

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm are required for the operations-console checks." >&2
  exit 127
fi

if [[ ! -f "${ops_console_dir}/package-lock.json" ]]; then
  echo "Missing ${ops_console_dir}/package-lock.json; commit the lock file." >&2
  exit 2
fi

typescript_compiler="${ops_console_dir}/node_modules/typescript/bin/tsc"
if [[ ! -f "${typescript_compiler}" ]]; then
  echo "TypeScript dependencies are absent; installing locked development dependencies."
  npm --prefix "${ops_console_dir}" ci --include=dev --no-audit --no-fund
fi

if [[ ! -f "${typescript_compiler}" ]]; then
  echo "TypeScript compiler was not installed at ${typescript_compiler}." >&2
  exit 127
fi

node "${typescript_compiler}" --noEmit -p "${ops_console_dir}/tsconfig.json"
node "${typescript_compiler}" -p "${ops_console_dir}/tsconfig.json"
node --check "${ops_console_dir}/dist/main.js"

echo "All Python, C++ and browser-JavaScript checks passed."
