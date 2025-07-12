#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv/bin/activate"
if [ -f "$VENV" ]; then
    echo "Activating virtual environment at $VENV"
    source "$VENV"
else
    echo "Error: Virtual environment not found at $VENV"
    exit 1
fi

PYTHON=$(which python3)
echo "Using Python from: $PYTHON"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <script.py> [args...]"
    exit 1
fi

SCRIPT="$SCRIPT_DIR/$1"
shift
if [ ! -f "$SCRIPT" ]; then
    echo "Error: Script '$SCRIPT' not found."
    exit 1
fi

set -euo pipefail

echo "Running script: $SCRIPT"
echo "Using arguments: $@"
$PYTHON -u "$SCRIPT" "$@"
