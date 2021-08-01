#!/usr/bin/env python

# Derivative work from https://gitlab.cern.ch/scipp/mario-mapyde
# You can "safely" ignore the warnings about the missing dictionaries...

import argparse
import os
import re
import sys

import ROOT
from HistCollections import DelphesEvent, Hists

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", action="store", default="input.txt")
    parser.add_argument("--output", action="store", default="hist.root")
    parser.add_argument("--lumi", action="store", default=1000.0)  # 1 fb-1
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--XS", action="store", default=0)
    args = parser.parse_args()

    def strip_ansi_codes(s):
        """
        Remove ANSI color codes from the string.
        """
        return re.sub("\033\\[([0-9]+)(;[0-9]+)*m", "", s)

    # Environment setup
    if "ROOT_INCLUDE_PATH" not in os.environ:
        print(
            "\nERROR: export the shell variable ROOT_INCLUDE_PATH to be the include directory that contains Delphes files."
        )
        print(
            "       Example: The include directory from `find /usr/ -iname DelphesClasses.h`\n"
        )
        sys.exit(1)
    ROOT.gInterpreter.Declare('#include "classes/DelphesClasses.h"')
    ROOT.gInterpreter.Declare('#include "ExRootAnalysis/ExRootTreeReader.h"')
    ROOT.gSystem.Load("libDelphes.so")
    # Prevent the canvas from displaying
    ROOT.gROOT.SetBatch(True)

    reweightEvents = False
    XS = 0
    if float(args.XS) > 0:
        XS = float(strip_ansi_codes(args.XS))
        print(XS)
        reweightEvents = True

    chain = ROOT.TChain("Delphes")

    if args.input[-4:] == "root":
        print("Running over single root file:")
        print(f"   > {args.input}")
        chain.Add(args.input)
    else:
        print("Running over list of root files:")
        for line in open(args.input):
            print("   > " + line.rstrip("\n"))
            chain.Add(line.rstrip("\n"))

    numFiles = chain.GetNtrees()
    print(f"Loaded {numFiles} chains...")

    # a histogram for our output
    outfile = ROOT.TFile.Open(args.output, "RECREATE")

    # Book histograms
    all_events = Hists("all_events", outfile)
    # presel = Hists("presel", outfile)
    # SR = Hists("SR", outfile)
    # SR_jetbins=JetBins("SR_jetbins",outfile)

    weightscale = float(args.lumi) / numFiles
    # Loop through all events in chain to get the sum of weights before filling trees and hists
    # There should be a better way to do this....
    if reweightEvents:
        print("Computing sum of weights")
        entry = 0
        sumofweights = 0
        for event in chain:
            entry += 1

            if entry != 0 and entry % 10000 == 0:
                print(f"{entry} events processed for sum of weights")
                sys.stdout.flush()

            # wrapper around Delphes events to make some things easier
            delphes_event = DelphesEvent(event)
            sumofweights += delphes_event.weight

        # compute appropriate weights for each event
        weightscale *= XS / sumofweights

    # Loop through all events in chain
    print("Processing events")
    entry = 0

    for event in chain:
        entry += 1

        if entry != 0 and entry % 10000 == 0:
            print(f"{entry} events processed")
            sys.stdout.flush()

        # wrapper around Delphes events to make some things easier
        delphes_event = DelphesEvent(event)
        weight = delphes_event.weight * weightscale

        # fill histograms for all events
        all_events.fill(delphes_event, weight)

        # TODO: This is all analysis specific stuff that needs to get ripped out
        # # preselection: MET>120, >=2 jets
        # if delphes_event.met.Pt() < 150 or len(delphes_event.jets) < 2:
        #     continue
        # presel.fill(delphes_event, weight)

        # # SR: zero e/mu/tau, deltaeta>3, mjj>1 TeV, nJets==2
        # if len(delphes_event.tautags) != 0:
        #     continue
        # if len(delphes_event.elecs) != 0:
        #     continue
        # if len(delphes_event.muons) != 0:
        #     continue
        # if len(delphes_event.exclJets) < 2:
        #     continue
        # mjj = (delphes_event.exclJets[0].P4() + delphes_event.exclJets[1].P4()).M()
        # if mjj < 1000:
        #     continue
        # deta = abs(
        #     delphes_event.exclJets[0].P4().Eta() - delphes_event.exclJets[1].P4().Eta()
        # )
        # if deta < 3.0:
        #     continue

        # SR.fill(delphes_event, weight)
        # SR_jetbins.fill(de,weight)

    all_events.write()
    # presel.write()
    # SR.write()
    # SR_jetbins.write()
    outfile.Close()

    print("Done!")
