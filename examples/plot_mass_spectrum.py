import math
from pathlib import Path

import hist
import mplhep
import numpy as np
import pylhe
from hist import Hist
from matplotlib.figure import Figure
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


def plot_ROOT():
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
        .joinpath("drell-yan_test")
        .joinpath("Events")
        .joinpath("run_01")
        .joinpath("unweighted_events.lhe")
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
    canvas.SaveAs("drell-yan-spectrum.png")


if __name__ == "__main__":
    hist_range = [15, 200]  # GeV
    bin_width = 1  # GeV

    # TODO: Use weights
    hist_1 = Hist(
        hist.axis.Regular(
            get_nbins(hist_range, bin_width),
            hist_range[0],
            hist_range[1],
            name="invariant_mass",
        )
    )

    # Use the generator provided by pylhe to read the events.
    lhe_path = (
        Path.cwd()
        .joinpath("drell-yan_test")
        .joinpath("Events")
        .joinpath("run_01")
        .joinpath("unweighted_events.lhe")
    )
    _weights = []
    for event in pylhe.readLHE(lhe_path):
        hist_1.fill(
            invariant_mass(event.particles[-1], event.particles[-2]),
        )
        _weights.append(event.eventinfo.weight)

    weights = np.array(_weights)

    fig = Figure(figsize=(7, 5))
    ax = fig.subplots()

    mplhep.set_style("ATLAS")

    # mplhep.histplot(hist_1, w2=weights, histtype="fill", ax=ax)
    mplhep.histplot(hist_1, histtype="fill", ax=ax)
    ax.set_xlim(hist_range)

    ax.semilogy()
    ax.set_xlabel(r"$\ell\ell$ pair mass [GeV]")
    ax.set_ylabel(f"Count / [{bin_width} GeV]")
    # ax.set_title("Drell-Yan invariant mass spectrum")
    ax.set_title("Drell-Yan")
    fig.savefig("drell-yan-matplotlib.png")
