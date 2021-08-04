#!/bin/bash

PROCESS_DIRECTORY="${1:-drell-yan}"
qsub "${PROCESS_DIRECTORY}/madgraph5.pbs"
