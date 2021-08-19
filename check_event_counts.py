from pathlib import Path

import click
import uproot


@click.command()
@click.option(
    "-e",
    "--events",
    "events_path",
    default=Path("/tmp").joinpath("combined_preprocessing_output.root"),
    help="Path to the preprocessing events ROOT file.",
)
@click.option(
    "-w",
    "--weights",
    "weights_path",
    default=Path("/tmp").joinpath("combined_momemta_weights.root"),
    help="Path to the MoMEMta weights ROOT file.",
)
def check_event_counts(events_path, weights_path):
    preprocessing_tree = uproot.open(events_path)["event_selection/hftree"]
    preprocessing_nevents = preprocessing_tree.num_entries

    weights_tree = uproot.open(weights_path)["momemta"]
    weights_nevents = weights_tree.num_entries

    print(f"Number of preprocessing events: {preprocessing_nevents}")
    print(f"Number of weights: {weights_nevents}")
    if preprocessing_nevents != weights_nevents:
        print(
            f"\n# Event mismatch: preprocessing has {preprocessing_nevents-weights_nevents} more events than MoMEMta"
        )


if __name__ == "__main__":
    check_event_counts()
