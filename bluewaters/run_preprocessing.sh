#!/bin/bash

if [ "${BASH_VERSION:0:1}" -lt 4 ]; then
    echo "ERROR: This script uses Bash version 4.0+ syntax. Your Bash version is ${BASH_VERSION} which is too old."
    echo "       Run: 'module load bash' to get a modern version on Blue Waters."
    exit 1
fi

PROCESS_DIRECTORY="${1:-drell-yan_ll}"
# qsub "${PROCESS_DIRECTORY}/preprocessing.pbs"

TOPOLOGY="ll"
PHYSICS_PROCESS="drell-yan_${TOPOLOGY}"
PROCESS_DIRECTORY="${1:-${PHYSICS_PROCESS}}"

USER_SCRATCH="/mnt/c/scratch/sciteam/${USER}"
OUTPUT_BASE_PATH="${USER_SCRATCH}/${PHYSICS_PROCESS}"

if [ -f delphes_filelist.txt ]; then
    rm delphes_filelist.txt
fi

find "${OUTPUT_BASE_PATH}"/delphes/*/ -name "delphes_output.root" | sort > delphes_filelist.txt

echo "# Submitting $(wc -l delphes_filelist.txt | awk '{print $1}') jobs"
echo ""
while IFS="" read -r line || [ -n "${line}" ]
do
    # qsub -v: comma separated list of strings of the form variable or variable=value.
    qsub -v INPUT_FILE="${line}" "${PROCESS_DIRECTORY}/preprocessing.pbs"
done < delphes_filelist.txt
echo ""
echo "# Submitted $(wc -l delphes_filelist.txt | awk '{print $1}') jobs"
echo ""
echo '# Check status with: qstat -u $USER'
qstat -u "${USER}"
