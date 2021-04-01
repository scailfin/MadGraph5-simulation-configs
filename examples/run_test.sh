#!/bin/bash

# Ensure required PDF set available
lhapdf get NNPDF23_lo_as_0130_qed

if [ -d drell-yan_test ];then
  rm -rf drell-yan_test 
fi

mg5_aMC drell-yan_test.mg5
