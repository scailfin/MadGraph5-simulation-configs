#!/bin/bash

# Run this inside of the directory for the hypothesis

# Ensure lhadpdf set exists
lhapdf get CT10nlo

if [[ -d MatrixElements ]];then
  rm -rf MatrixElements
fi
mkdir MatrixElements
pushd MatrixElements
# Generate the matrix Element with MadGraph5
mg5_aMC ../../configs/momemta/drell-yan.mg5
rm py.py
popd

# Build Matrix Element
# c.f. https://github.com/MoMEMta/MoMEMta-MaGMEE#usage
# Matrix Element namespace name defined in ../../configs/momemta/drell-yan.mg5
cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/local/venv \
    -S MatrixElements/pp_drell_yan \
    -B MatrixElements/pp_drell_yan/build
cmake MatrixElements/pp_drell_yan/build -L
cmake --build MatrixElements/pp_drell_yan/build \
    --clean-first \
    --parallel $(($(nproc) - 1))

# Example level build
if [ -d build ];then
  rm -rf build
fi
# Cleanup from failed runs
if [ -f core ]; then
  rm core
fi
cmake \
    -DCMAKE_INSTALL_PREFIX=/usr/local/venv \
    -S . \
    -B build
cmake build -L
cmake --build build \
    --clean-first \
    --parallel $(($(nproc) - 1))

INPUT_PATH="${1:-/home/feickert/workarea/MadGraph5-simulation-configs/preprocessing/preprocessing_output.root}"
OUTPUT_PATH="${2:-drell-yan_weights.root}"

# Current configuration in drell_yan.cxx requires running from top level of example dir
time ./build/drell-yan_example \
  --input "${INPUT_PATH}" \
  --output "${OUTPUT_PATH}"
