#!/bin/bash

# Assumes running inside Docker image scailfin/delphes-python-centos:3.5.0
export ROOT_INCLUDE_PATH="/usr/local/venv/include"

# User input with default path
INPUT_PATH="${1:-delphes_output.root}"
python scripts/SimpleAna.py \
    --input "${INPUT_PATH}" \
    --output test.root \
    --lumi 1000.0 \
    --XS 0

unset ROOT_INCLUDE_PATH
