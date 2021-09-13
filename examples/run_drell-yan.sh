#!/bin/bash

# Ensure required PDF set available
lhapdf get NNPDF23_lo_as_0130_qed

if [ -d drell-yan_output ];then
  rm -rf drell-yan_output
fi

mg5_aMC "$PWD/../configs/drell-yan/drell-yan_ll.mg5"
