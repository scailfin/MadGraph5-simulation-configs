#!/bin/bash

# Ensure shifter enabled
module load shifter

if [ -d user_scratch ];then
  rm -rf user_scratch/*
fi

# $HOME is /u/sciteam/${USER}
aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image=neubauergroup/bluewaters-mg5_amc:3.1.1 \
    --volume=/mnt/a/"${HOME}"/user_scratch:/root/data \
    --volume=/mnt/a/"${HOME}":/mnt/a/"${HOME}" \
    --workdir=/root/data \
    -- /bin/bash -c 'mg5_aMC /mnt/a/'"${HOME}"'/MadGraph5-simulation-configs/configs/madgraph5/drell-yan.mg5'
