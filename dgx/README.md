# Running on NCSA DGX

## Notes

Note that Docker is running as `root` so if you want to follow along with its CPU and memeory useage instead of running

```console
$ htop -u $USER
```

you need to run

```console
$ htop -u root
```

## Running

As running on DGX is more focused on interactivity than scale, only one run of a workflow stage witll be executed at a time, so there is no need for combination of runs.
There is then a "run" control script for each stage (e.g. `run_madgraph.sh`) that parameterizes a set of workflow scipts for a given physics process.
For example, given the following directory structure

```console
$ tree -L 2
.
├── drell-yan_ll
│   ├── delphes.sh
│   ├── madgraph.sh
│   ├── momemta.sh
│   └── preprocessing.sh
├── README.md
├── run_delphes.sh
├── run_madgraph.sh
├── run_momemta.sh
└── run_preprocessing.sh

1 directory, 9 files
```

running

```console
$ bash run_madgraph.sh drell-yan_ll
```

will launch MadGraph5 generation of the processes configured in `drell-yan_ll/madgraph.sh` and place its run artifacts under `outputs/drell-yan_ll/madgraph`.

### Example

To run the full workflow for the existing `drell-yan_ll` process a user would simply execute the workflow stages in order.
The stages are necessarily blocking.

1. Generate MadGraph5 configuration files and run MadGraph5 + PYTHIA8

```console
$ bash run_madgraph.sh drell-yan_ll
```

2. Take the PYTHIA8 output and simulate interactions with the ATLAS detector with Delphes

```console
$ bash run_delphes.sh drell-yan_ll
```

3. Take the Delphes output (detector level simulation) and preform simple preprocessing to get event level simulation

```console
$ bash run_preprocessing.sh drell-yan_ll
```

4. Take the event level simulation ROOT files and the physics hypothesis (configured in `drell-yan_ll/momemta.sh`) and run MoMEMta to generate the MoMEMta weights for each event.

```console
$ bash run_momemta.sh drell-yan_ll
```
