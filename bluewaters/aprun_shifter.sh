#!/bin/bash

aprun -b -N 1 -cc none \
  -- shifter \
    --clearenv \
    --image=neubauergroup/bluewaters-mg5_amc:3.1.1 \
    --volume=/mnt/a/u/sciteam/"${USER}"/user_scratch:/home/docker/data \
    --volume=/mnt/a/u/sciteam/"${USER}":/mnt/a/u/sciteam/"${USER}" \
    --workdir=/home/docker/data \
    -- /bin/bash -I
