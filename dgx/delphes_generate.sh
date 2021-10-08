#!/bin/bash

BASE_PREFIX="/root/data"
INPUTS_DIR=/root/inputs
PHYSICS_PROCESS="drell-yan_ll"

if [[ ! -d "outputs/delphes" ]]; then
    mkdir -p outputs/delphes
fi
cd outputs/delphes

INPUT_FILE_PATH="${BASE_PREFIX}/outputs/madgraph/${PHYSICS_PROCESS}_output/Events/run_01/tag_1_pythia8_events.hepmc"

printf "\n# printenv:\n"
printenv
printf "\n\n"

printf "# Unzip HEPMC file if needed\n\n" && \
if [ -f "${INPUT_FILE_PATH}.gz" ]; then
    gunzip "${INPUT_FILE_PATH}.gz"
fi

time DelphesHepMC2 \
    /usr/local/venv/cards/delphes_card_ATLAS.tcl \
    delphes_output.root \
    "${INPUT_FILE_PATH}"
