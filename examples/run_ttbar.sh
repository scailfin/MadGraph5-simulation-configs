#!/bin/bash

# Ensure required PDF set available
lhapdf get NNPDF23_lo_as_0130_qed

if [ -d ttbar-fully-leptonic_output ];then
  rm -rf ttbar-fully-leptonic_output
fi

mg5_aMC "$PWD/../configs/ttbar/ttbar-fully-leptonic.mg5"
