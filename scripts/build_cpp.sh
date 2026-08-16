#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="${repo_dir}/build"
mkdir -p "${build_dir}"

compiler="${CXX:-g++}"
common=(
  -std=c++20 -O2 -Wall -Wextra -Wpedantic -Werror
  -I"${repo_dir}/core/cpp/include"
)

"${compiler}" "${common[@]}" \
  "${repo_dir}/core/cpp/src/controller.cpp" \
  "${repo_dir}/core/cpp/src/cli.cpp" \
  -o "${build_dir}/coolride-controller"

"${compiler}" "${common[@]}" \
  "${repo_dir}/core/cpp/src/controller.cpp" \
  "${repo_dir}/core/cpp/tests/controller_test.cpp" \
  -o "${build_dir}/coolride-core-test"

echo "Built ${build_dir}/coolride-controller"
