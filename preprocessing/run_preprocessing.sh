#!/bin/bash

export INPUT_PATH="/data/hepmc_output/delphes_output/delphes_output_nevent_10e4.root"
python scripts/SimpleAna.py \
	--input "${INPUT_PATH}" \
	--output test.root \
	--lumi 1000.0 \
	--XS 0

unset INPUT_PATH
