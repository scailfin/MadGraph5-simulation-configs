#!/bin/bash

# Ensure shifter enabled
module load shifter

OUTPUT_DIR_NAME="drell-yan_output"
OUTPUT_DIR="/mnt/a/${HOME}/user_scratch/${OUTPUT_DIR_NAME}"
if [ -d "${OUTPUT_DIR}" ];then
  rm -rf "${OUTPUT_DIR}"
fi

# $HOME is /u/sciteam/${USER}
SHIFTER_IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image="${SHIFTER_IMAGE}" \
    --volume=/mnt/a/"${HOME}"/user_scratch:/root/data \
    --volume=/mnt/a/"${HOME}":/mnt/a/"${HOME}" \
    --workdir=/root/data \
    -- /bin/bash -c 'mg5_aMC /mnt/a/'"${HOME}"'/MadGraph5-simulation-configs/configs/madgraph5/drell-yan.mg5'
