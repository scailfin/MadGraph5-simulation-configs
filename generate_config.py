import json
import multiprocessing
from pathlib import Path

import click


def json_to_mg5(config):
    mg5_str = ""

    options = config.get("options", None)
    if options:
        madevent_options = options.get("madevent", None)
        if madevent_options:
            mg5_str += "# MadEvent options"
            run_mode = madevent_options.get("run_mode", 2)
            mg5_str += "\n# 0=single core, 1=cluster, 2=multicore"
            mg5_str += f"\nset run_mode {run_mode}"
            nb_core = madevent_options.get(
                "nb_core", max(multiprocessing.cpu_count() - 2, 1)
            )
            mg5_str += f"\nset nb_core {nb_core}"

    mg5_str += f"\ngenerate {config['process']}"
    mg5_str += f"\noutput {config['output']}_output"
    mg5_str += f"\nlaunch {config['output']}_output"

    run_options = options.get("run", None)
    mg5_str += "\n# Set run card options"
    if "shower" in run_options:
        mg5_str += "\n  # Use PYTHIA8 for the shower/hadronization"
        mg5_str += f"\n  shower={run_options['shower']}"
    nevents = run_options.get("nevents", 1000)
    mg5_str += f"\n  # Generate {nevents:.1e} events"
    mg5_str += f"\n  set nevents {nevents}"
    iseed = run_options.get("iseed", 0)
    mg5_str += "\n  # Set random seed"
    mg5_str += f"\n  set iseed {iseed}"
    mg5_str += "\n"

    return mg5_str


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    help="Path to JSON configuration.",
)
@click.option(
    "-o",
    "--outpath",
    "output_path",
    help="Path to the output directory.",
)
@click.option(
    "-s",
    "--seed",
    "random_seed",
    type=int,
    help="Random seed (iseed) for MadGraph5 run_card.dat.",
)
def generate_config(config_path, output_path, random_seed):
    with open(Path(config_path).absolute()) as config_file:
        config = json.load(config_file)

    # Inject random seed if given at CLI
    if random_seed:
        config["options"]["run"]["iseed"] = random_seed

    if config["type"] == "madgraph5":
        output_config = json_to_mg5(config)
        file_extension = ".mg5"

    output_path = (
        Path(output_path).absolute()
        if output_path
        else Path.cwd().joinpath("configs", config["type"])
    )
    out_path = output_path.joinpath(config["output"] + file_extension)
    with open(out_path, "w") as outfile:
        outfile.write(output_config)


if __name__ == "__main__":
    generate_config()
