import json
from pathlib import Path

import click


def json_to_mg5(config):
    mg5_str = f"generate {config['process']}"
    mg5_str += f"\noutput {config['output']}_output"
    mg5_str += f"\nlaunch {config['output']}_output"

    options = config["options"]
    if "shower" in options:
        mg5_str += "\n  # Use PYTHIA8 for the shower/hadronization"
        mg5_str += f"\n  shower={options['shower']}"
    nevents = options.get("nevents", 1000)
    mg5_str += f"\n  # Generate {nevents:.1e} events"
    mg5_str += f"\n  set nevents {nevents}"
    mg5_str += "\n"

    return mg5_str


@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    help="Path to JSON configuration.",
)
def generate_config(config_path):
    config_path = Path().cwd().joinpath(config_path)
    with open(config_path, "r") as config_file:
        config = json.load(config_file)

    if config["type"] == "madgraph5":
        output_config = json_to_mg5(config)
        file_extension = ".mg5"

    out_path = (
        Path()
        .cwd()
        .joinpath("configs", config["type"], config["output"] + file_extension)
    )
    with open(out_path, "w") as outfile:
        outfile.write(output_config)


if __name__ == "__main__":
    generate_config()
