#!/bin/bash

# Ensure shifter enabled
module load shifter

# $HOME is /u/sciteam/${USER}
SHIFTER_IMAGE="neubauergroup/bluewaters-mg5_amc:3.1.1"
aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image="${SHIFTER_IMAGE}" \
    --volume=/mnt/a/"${HOME}"/user_scratch:/root/data \
    --volume=/mnt/a/"${HOME}":/mnt/a/"${HOME}" \
    --workdir=/root/data \
    -- /bin/bash -I
