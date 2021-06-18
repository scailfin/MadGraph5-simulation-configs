#!/bin/bash

# Ensure shifter enabled
module load shifter

# $HOME is /u/sciteam/${USER}
aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image=neubauergroup/bluewaters-mg5_amc:3.1.1 \
    --volume=/mnt/a/"${HOME}"/user_scratch:/root/data \
    --volume=/mnt/a/"${HOME}":/mnt/a/"${HOME}" \
    --workdir=/root/data \
    -- /bin/bash -I
