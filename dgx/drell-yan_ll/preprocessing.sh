#!/bin/bash

INPUTS_DIR=/root/inputs
PHYSICS_PROCESS="${1:-drell-yan_ll}"

if [[ ! -d "outputs/${PHYSICS_PROCESS}/preprocessing" ]]; then
    mkdir -p "outputs/${PHYSICS_PROCESS}/preprocessing"
fi
cd "outputs/${PHYSICS_PROCESS}/preprocessing"

printf "\n# printenv:\n"
printenv
printf "\n\n"

export ROOT_INCLUDE_PATH="/usr/local/venv/include"

# User input with default path
INPUT_PATH="${2:-../delphes/delphes_output.root}"
OUTPUT_PATH=${3:-preprocessing_output.root}
# Lumi is currently set to a default value and should be updated to something
# more relevant
python "${INPUTS_DIR}"/preprocessing/scripts/SimpleAna.py \
    --input "${INPUT_PATH}" \
    --output "${OUTPUT_PATH}" \
    --lumi 1000.0 \
    --XS 0

unset ROOT_INCLUDE_PATH
