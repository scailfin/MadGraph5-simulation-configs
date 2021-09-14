# Running on NCSA Blue Waters

## Running with Torque

To submit jobs to run on Portable Batch System (PBS) Torque, write a PBS submission file, and then submit the PBS job to Torque using `qsub`.

For example, `drell-yan_ll/madgraph5.pbs` defines all the commands required to run the example MadGraph5 simulation for Drell-Yan defined in `configs/madgraph5/drell-yan_ll.mg5` on Shifter inside a specified container.
So the PBS job file (`drell-yan_ll/madgraph5.pbs`) is where you define what you want to have happen, and then you submit it with `qsub` just using a 1 command Bash script (`run_madgraph5.sh`) for easy of use and to make keeping track of workflows easier.

Once jobs are submitted they can be tracked in the batch system with

```console
qstat -u $USER
```

and to show only the jobs currently running use

```console
qstat -r -u $USER
```

After each stage you can move all the logs generated to the appropriate output directory using `move_logs.sh`

```console
bash move_logs.sh <physics_process> <stage>
# Example
# bash move_logs.sh drell_yan_ll madgraph
```

### Example: Drell-Yan

* Ensure there is a MadGraph5 steering script config at `configs/json/drell-yan_ll.json`
* One would then submit the Drell-Yan job with

```console
bash run_madgraph5.sh drell-yan_ll
```

to generate LHE and HEPMC2 simulation files

* Then once the MadGraph5 and PYTHIA8 simulation is done, run DELPHES on the HEPMC2 input with

```console
bash run_delphes.sh drell-yan_ll
```

* To then run the preprocessing needed for MoMEMta to run to move from detector level information to event level information, run

```console
bash run_preprocessing.sh drell-yan_ll
```

* After the preprocessing jobs have all finished, combine them into a single ROOT file for MoMEMta to use

```console
bash combine_preprocessing.sh drell-yan_ll
```

which will produce the file `/mnt/c/scratch/sciteam/${USER}/drell-yan_ll/preprocessing/combined_preprocessing_output.root`.

* To then finally run MoMEMta for the hypothesis described with the [MoMEMta-MaGMEE](https://github.com/MoMEMta/MoMEMta-MaGMEE) MadGraph5 plugin run

```console
bash run_momemta.sh drell-yan_ll
```

* Then to combine the output of the MoMEMta jobs use

```console
bash combine_momemta.sh drell-yan_ll
```

which will produce the file `/mnt/c/scratch/sciteam/${USER}/drell-yan_ll/momemta/combined_momemta_weights.root`.

## Interactive Session

If you need to run an interactive session (which will be slower) you can first allocate resources on the `shifter` queue from Torque with `qsub`

```console
qsub -I -l gres=shifter -l nodes=1:ppn=8:xk -l walltime=03:00:00
```

Once the job has been submitted and the interactive prompt returns, you can run `aprun` commands directly, as seen in the `aprun_shifter_interactive.sh` example script.
