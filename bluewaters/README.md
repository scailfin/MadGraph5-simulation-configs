# Running on NCSA Blue Waters

## Interactive Session

If you need to run an interactive session (which will be slower) you can first allocate resources on the `shifter` queue from Torque with `qsub`

```console
qsub -I -l gres=shifter -l nodes=1:ppn=8:xk -l walltime=03:00:00
```

Once the job has been submitted and the interactive prompt returns, you can run `aprun` commands directly, as seen in the `aprun_shifter_interactive.sh` example script.
