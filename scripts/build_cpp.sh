#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${repo_dir}/build"
mkdir -p "${build_dir}"

compiler="${CXX:-g++}"
controller_binary="${build_dir}/coolride-controller"
test_binary="${build_dir}/coolride-core-test"
common=(
  -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror
  -I"${repo_dir}/core/cpp/include"
)

if ! command -v "${compiler}" >/dev/null 2>&1; then
  echo "C++ compiler not found: ${compiler}" >&2
  exit 127
fi

# Never execute a stale binary copied from another operating system or CPU.
rm -f "${controller_binary}" "${test_binary}"

"${compiler}" "${common[@]}" \
  "${repo_dir}/core/cpp/src/controller.cpp" \
  "${repo_dir}/core/cpp/src/cli.cpp" \
  -o "${controller_binary}"

"${compiler}" "${common[@]}" \
  "${repo_dir}/core/cpp/src/controller.cpp" \
  "${repo_dir}/core/cpp/tests/controller_test.cpp" \
  -o "${test_binary}"

echo "Built ${controller_binary}"
echo "Built ${test_binary}"
