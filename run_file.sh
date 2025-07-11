#!/bin/bash

source .venv/bin/activate
PYTHON=$(which python3)
echo "Using Python from: $PYTHON"

$PYTHON -u "$@" 
