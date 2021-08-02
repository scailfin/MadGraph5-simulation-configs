#!/bin/bash

# Assumes running inside Docker image scailfin/delphes-python-centos:3.5.0
export ROOT_INCLUDE_PATH="/usr/local/venv/include"

# User input with default path
INPUT_PATH="${1:-delphes_output.root}"
OUTPUT_PATH=${2:-preprocessing_output.root}
# Lumi is currently set to a default value and should be updated to something
# more relevant
python scripts/SimpleAna.py \
    --input "${INPUT_PATH}" \
    --output "${OUTPUT_PATH}" \
    --lumi 1000.0 \
    --XS 0

unset ROOT_INCLUDE_PATH
