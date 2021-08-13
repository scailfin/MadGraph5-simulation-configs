#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

PROCESS_DIRECTORY="${1:-drell-yan_ll}"
qsub "${PROCESS_DIRECTORY}/preprocessing.pbs"
