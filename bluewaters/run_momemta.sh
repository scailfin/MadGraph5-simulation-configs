#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

PROCESS_DIRECTORY="${1:-drell-yan}"

NUMBER_OF_JOBS=200
# Submit jobs
echo "# Submitting ${NUMBER_OF_JOBS} jobs"
echo ""
for n_job in $(seq 0 $((${NUMBER_OF_JOBS}-1)))
do
    # qsub -v: comma separated list of strings of the form variable or variable=value.
    qsub -v NUMBER_OF_STEPS="${NUMBER_OF_JOBS}",STEP_NUMBER="${n_job}" "${PROCESS_DIRECTORY}/momemta.pbs"
done
echo ""
echo "# Submitted ${NUMBER_OF_JOBS} jobs"
echo ""
echo '# Check status with: qstat -u $USER'
qstat -u "${USER}"
