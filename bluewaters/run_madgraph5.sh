#!/bin/bash

PROCESS_DIRECTORY="${1:-drell-yan}"
RANDOM_SEED=300
qsub "${PROCESS_DIRECTORY}/madgraph5.pbs"
