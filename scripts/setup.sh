#!/bin/sh
set -eu
skill_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python_command=${PYTHON:-python3}
"$python_command" -m venv "$skill_root/.venv"
"$skill_root/.venv/bin/python" -m pip install -r "$skill_root/requirements.txt"
"$skill_root/.venv/bin/python" -c 'import swisseph; from zoneinfo import ZoneInfo; print("Runtime ready:", swisseph.version, ZoneInfo("Asia/Kolkata"))'
