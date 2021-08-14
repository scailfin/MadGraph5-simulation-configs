#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

PROCESS_DIRECTORY="${1:-drell-yan_ll}"
TOTAL_NEVENTS=1000000
# This should be taken from the JSON config
EVENTS_PER_JOB=10000

# build seed array
n_jobs=$(("${TOTAL_NEVENTS}" / "${EVENTS_PER_JOB}"))
random_seeds=()
for n_step in $(seq 0 $((${n_jobs}-1)))
do
    random_seeds+=($(("${EVENTS_PER_JOB}" * (1+"${n_step}") )))
done

echo "# Submitting ${n_jobs} jobs"
echo ""
for random_seed in "${random_seeds[@]}"
do
    # qsub -v: comma separated list of strings of the form variable or variable=value.
    qsub -v RANDOM_SEED="${random_seed}" "${PROCESS_DIRECTORY}/madgraph5.pbs"
done
echo ""
echo "# Submitted ${n_jobs} jobs"
echo ""
echo '# Check status with: qstat -u $USER'
qstat -u "${USER}"
