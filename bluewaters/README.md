# Running on NCSA Blue Waters

Upon logging into Blue Waters, and cloning the configs repo to the home area, allocate resources on the `shifter` queue from Torque with `qsub`

```console
qsub -I -l gres=shifter -l nodes=1:ppn=8:xk -l walltime=03:00:00
```

Once the job has been submitted and the interactive prompt returns, you can `cd` to the `bluewaters` directory and run the Bash script that will guide the simulation.
