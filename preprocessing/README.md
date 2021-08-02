# Preprocessing of Delphes output files

The Delphes output ROOT files need to have preprocessing applied to them before they can be run with MoMEMta.
This requires doing some simple event selection to aquire 4-momentum information for the particles of interest for MoMEMta to use later.
So the preprocessing will start with the detector level event information (Delphes output ROOT files) and will output event selection level information in ROOT `TTree`s.

## Dependencies

The assumption is that all pre-processing code is run inside of a `scailfin/delphes-python-centos:3.5.0` based Docker container given that is requires use of Delphes header files and ROOT.

## Running

To run the preprocessing now, inside of a`scailfin/delphes-python-centos:3.5.0` bind mount, run the `run_preprocessing.sh` Bash script and pass it two arguments: the path to the input Delphes ROOT file and the output file path.

For example,

```console
$ bash run_preprocessing.sh \
  /data/hepmc_output/delphes_output/delphes_output_nevent_10e4.root \
  test_output.root
```

## Current Structure

At the moment, the structure of the preprocessing files:

- `HistCollections.py`
- `SimpleAna.py`

are still based on the structure of the corresponding files in the USSC SCIPP [`mario-mapyde` project](https://gitlab.cern.ch/scipp/mario-mapyde).
At the time of writing, both these scripts are used for specific analyses and are not meant for generalized use as they require direct manipulation of the code.

* `HistCollections.py` requires the user to write a specific class that will detail the histograms as well as the `TTree` branch structure
* `SimpleAnay.py` then imports from `HistCollections` the `DelphesEvent` and `Hists` classes and then requires the user to define the event level cuts and write a the event selection critieria to determine what `TTree` branches to make and when to fill them.

## Generalizing Use

What would be better would be to create base utility classes and then have the user subclass those to create both their own histograms and branch selections as well as be able to define their own analysis selections.
This would give commonality in the core infrastructure and then additionally allow the user to easily define their analysis specific use cases without having to rewrite common boilerplate code.
