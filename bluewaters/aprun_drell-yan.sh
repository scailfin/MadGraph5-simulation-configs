#!/bin/bash

if [ -d user_scratch ];then
  rm -rf user_scratch/*
fi

aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image=neubauergroup/bluewaters-mg5_amc:3.1.1 \
    --volume=/mnt/a/u/sciteam/"${USER}"/user_scratch:/home/docker/data \
    --volume=/mnt/a/u/sciteam/"${USER}":/mnt/a/u/sciteam/"${USER}" \
    --workdir=/home/docker/data \
    -- /bin/bash -c 'mg5_aMC /mnt/a/u/sciteam/'"${USER}"'/MadGraph5-simulation-configs/configs/madgraph5/drell-yan.mg5'
