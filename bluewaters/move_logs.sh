#!/bin/bash

physics_process="${1}"
if [ -z "${physics_process}" ]; then
    echo "# ERROR: physics process must be defined"
    exit 1
fi

stage="${2}"
if [ -z "${stage}" ]; then
    echo "# ERROR: stage must be defined"
    exit 1
fi

LOG_DIR="/mnt/c/scratch/sciteam/${USER}/${physics_process}/${stage}/logs"
mkdir -p "${LOG_DIR}"

mv "${stage}".*.bw.{out,err} "${LOG_DIR}/"
