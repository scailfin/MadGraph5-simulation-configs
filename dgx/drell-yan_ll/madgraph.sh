#!/bin/bash

INPUTS_DIR=/root/inputs
PHYSICS_PROCESS="drell-yan_ll"
CONFIG_NAME="${PHYSICS_PROCESS}.json"

if [[ ! -d "outputs/${PHYSICS_PROCESS}/madgraph" ]]; then
    mkdir -p "outputs/${PHYSICS_PROCESS}/madgraph"
fi
cd "outputs/${PHYSICS_PROCESS}/madgraph"

printf "\n# printenv:\n"
printenv
printf "\n\n"

python "${INPUTS_DIR}/generate_config.py" --help

echo ""

python "${INPUTS_DIR}"/generate_config.py \
        -c "${INPUTS_DIR}/configs/json/${CONFIG_NAME}" \
        --outpath $PWD \
        --seed 0

cat "${PHYSICS_PROCESS}.mg5"

echo ""

time mg5_aMC "${PHYSICS_PROCESS}".mg5
