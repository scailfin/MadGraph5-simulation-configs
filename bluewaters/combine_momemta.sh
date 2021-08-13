#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

PROCESS_DIRECTORY="${1:-drell-yan}"

qsub "${PROCESS_DIRECTORY}/combine_momemta.pbs"
echo ""
echo '# Check status with: qstat -u $USER'
qstat -u "${USER}"