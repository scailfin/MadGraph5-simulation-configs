#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

TOPOLOGY="ll"
PHYSICS_PROCESS="drell-yan_${TOPOLOGY}"
PROCESS_DIRECTORY="${1:-${PHYSICS_PROCESS}}"

USER_SCRATCH="/mnt/c/scratch/sciteam/${USER}"
OUTPUT_BASE_PATH="${USER_SCRATCH}/${PHYSICS_PROCESS}"

if [ -f hepmc_filelist.txt ]; then
    rm hepmc_filelist.txt
fi
# If the .hepmc.gz file has been unzipped already then it no longer exists and just the .hepmc file remains
find "${OUTPUT_BASE_PATH}"/madgraph/*/"${PHYSICS_PROCESS}"_output/Events/run_01/ -name "tag_1_pythia8_events.hepmc*" | sort > hepmc_filelist.txt

echo "# Submitting $(wc -l hepmc_filelist.txt | awk '{print $1}') jobs"
echo ""
while IFS="" read -r line || [ -n "${line}" ]
do
    # qsub -v: comma separated list of strings of the form variable or variable=value.
    qsub -v INPUT_FILE_PATH="${line}" "${PROCESS_DIRECTORY}/delphes.pbs"
done < hepmc_filelist.txt
echo ""
echo "# Submitted $(wc -l hepmc_filelist.txt | awk '{print $1}') jobs"
echo ""
echo '# Check status with: qstat -u $USER'
qstat -u "${USER}"
