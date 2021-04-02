import math
from pathlib import Path

import pylhe
from ROOT import TH1F, TCanvas, gROOT, kTRUE


def invariant_mass(p1, p2):
    # c.f. https://github.com/scikit-hep/pylhe/blob/master/examples/zpeak.ipynb
    return math.sqrt(
        sum(
            (1 if mu == "e" else -1) * math.pow((getattr(p1, mu) + getattr(p2, mu)), 2)
            for mu in ["e", "px", "py", "pz"]
        )
    )


def get_nbins(hist_range, width):
    return int((hist_range[1] - hist_range[0]) / width)


if __name__ == "__main__":
    gROOT.SetBatch(kTRUE)

    hist_range = [15, 200]  # GeV
    bin_width = 1  # GeV

    hist_1 = TH1F(
        "invariant_mass",
        "Invariant Mass of Final State",
        get_nbins(hist_range, bin_width),
        hist_range[0],
        hist_range[1],
    )
    hist_1.SetFillColor(38)

    # Use the generator provided by pylhe to read the events.
    lhe_path = (
        Path.cwd()
        .joinpath("drell-yan_output")
        .joinpath("Events")
        .joinpath("run_01")
        .joinpath("unweighted_events.lhe.gz")
    )
    for event in pylhe.readLHE(lhe_path):
        hist_1.Fill(
            invariant_mass(event.particles[-1], event.particles[-2]),
            event.eventinfo.weight,
        )

    canvas = TCanvas()
    canvas.SetLogy()

    hist_1.Draw("BAR")
    hist_1.GetXaxis().SetTitle("lepton pair mass [GeV]")
    hist_1.GetYaxis().SetTitle(f"Count / [{bin_width} GeV]")
    canvas.SaveAs("drell-yan-spectrum_ROOT.png")
