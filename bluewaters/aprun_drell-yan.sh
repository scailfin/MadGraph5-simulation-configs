#!/bin/bash

# Ensure shifter enabled
module load shifter

OUTPUT_DIR="drell-yan_output"
OUTPUT_BASE_PATH="/mnt/a/${HOME}/user_scratch"
OUTPUT_PATH="${OUTPUT_BASE_PATH}/${OUTPUT_DIR}"
if [ -d "${OUTPUT_PATH}" ];then
  rm -rf "${OUTPUT_PATH}"
fi

# $HOME is /u/sciteam/${USER}
SHIFTER_IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image="${SHIFTER_IMAGE}" \
    --volume="${OUTPUT_BASE_PATH}":/root/data \
    --volume=/mnt/a/"${HOME}":/mnt/a/"${HOME}" \
    --workdir=/root/data \
    -- /bin/bash -c 'mg5_aMC /mnt/a/'"${HOME}"'/MadGraph5-simulation-configs/configs/madgraph5/drell-yan.mg5'
