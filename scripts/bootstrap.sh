#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_dir="${repo_dir}/.venv"

python3 -m venv "${venv_dir}"
"${venv_dir}/bin/python" -m pip install --upgrade pip setuptools wheel
"${venv_dir}/bin/python" -m pip install -e "${repo_dir}"
npm --prefix "${repo_dir}/apps/ops-console" ci

echo "Activate with: source ${venv_dir}/bin/activate"
