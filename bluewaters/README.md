# Running on NCSA Blue Waters

## Running with Torque

To submit jobs to run on PBS Torque, write a PBS submission file, and then submit the PBS job to Torque using `qsub`.

For example, `drell-yan_madgraph5.pbs` defines all the commands required to run the example MadGraph5 simulation for Drell-Yan defined in `configs/madgraph5/drell-yan.mg5` on Shifter inside a specified container.
So the PBS job file (`drell-yan_madgraph5.pbs`) is where you define what you want to have happen, and then you submit it with `qsub` just using a 1 line Bash script (`pbs_drell-yan_madgraph5.sh`) for easy of use and to make keeping track of workflows easier.

## Interactive Session

If you need to run an interactive session (which will be slower) you can first allocate resources on the `shifter` queue from Torque with `qsub`

```console
qsub -I -l gres=shifter -l nodes=1:ppn=8:xk -l walltime=03:00:00
```

Once the job has been submitted and the interactive prompt returns, you can run `aprun` commands directly, as seen in the `aprun_shifter_interactive.sh` example script.
