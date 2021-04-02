import math
from pathlib import Path

import hist
import matplotlib
import matplotlib.pyplot as plt
import mplhep
import pylhe
from hist import Hist


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
    hist_range = [15, 200]  # GeV
    bin_width = 1  # GeV

    hist_1 = Hist(
        hist.axis.Regular(
            get_nbins(hist_range, bin_width),
            hist_range[0],
            hist_range[1],
            name="invariant_mass",
        ),
        storage=hist.storage.Weight(),
    )

    # Use the generator provided by pylhe to read the events.
    lhe_path = (
        Path.cwd()
        .joinpath("drell-yan_output")
        .joinpath("Events")
        .joinpath("run_01")
        .joinpath("unweighted_events.lhe.gz")
    )

    # Slow given LHE needs parsing
    for event in pylhe.readLHE(lhe_path):
        hist_1.fill(
            invariant_mass(event.particles[-1], event.particles[-2]),
            weight=event.eventinfo.weight,
        )

    matplotlib.use("AGG")  # Set non-GUI backend
    mplhep.set_style("ATLAS")

    fig, ax = plt.subplots()
    mplhep.histplot(hist_1, histtype="fill", ax=ax)
    ax.set_xlim(hist_range)

    ax.semilogy()
    ax.set_xlabel(r"$\ell\ell$ pair mass [GeV]")
    ax.set_ylabel(f"Count / [{bin_width} GeV]")

    ax.set_title("Drell-Yan invariant mass spectrum")
    fig.savefig("drell-yan-spectrum.png")
