#!/bin/bash

INPUTS_DIR=/root/inputs
PHYSICS_PROCESS="drell-yan_ll"
CONFIG_NAME="${PHYSICS_PROCESS}.json"

if [[ ! -d "outputs" ]]; then
    mkdir -p outputs
fi
cd outputs

printf "\n# printenv:\n"
printenv
printf "\n\n"

python "${INPUTS_DIR}/generate_config.py" --help

python \
    "${INPUTS_DIR}"/generate_config.py \
        -c "${INPUTS_DIR}/configs/json/${CONFIG_NAME}" \
        --outpath $PWD \
        --seed 0

cat "${PHYSICS_PROCESS}.mg5"
time mg5_aMC "${PHYSICS_PROCESS}".mg5

# -- /bin/bash -c 'export PATH="/usr/local/venv/bin:${PATH}" && \
#     printf "\n# printenv:\n" && printenv && printf "\n\n" && \
#     python "${CODE_BASE_PATH}"/generate_config.py --help && \
#     echo "" && \
#     python "${CODE_BASE_PATH}"/generate_config.py -c "${CODE_BASE_PATH}/configs/json/${CONFIG_NAME}" --outpath $PWD --seed "${RANDOM_SEED}" && \
#     cat "${PHYSICS_PROCESS}".mg5 && \
#     echo "" && \
#     time mg5_aMC "${PHYSICS_PROCESS}".mg5'

