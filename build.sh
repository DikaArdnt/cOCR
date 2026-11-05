#!/usr/bin/env bash
set -e

if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Python 3 tidak ditemukan di sistem." >&2
    exit 1
fi

$PYTHON_CMD build_tools/build_exe.py "$@"
