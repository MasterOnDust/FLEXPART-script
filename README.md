# FLEXPART-script
Python script for managing and setting up FLEXPART simulation

## Discription:
- flexpart_simulation.py , input parameters and settings for the flexpart, and settings for the 
slurm jobscript
- params.py , store the different input parameters set in flexpart_simulation.py
- jobscript creates folder structure containing the specific inputfiles ,
slurm job script and submit jobscript to queue.

## Usage:
First configure the flexpart simulation by copying the flexpart_setup.py file. The path to the flexpart_setup file has to be 
specified with the --path argument
```
 $python jobscript --h
 usage: jobscript.py [-h] [--test] [--testAndSubmit] [--path PATH] [--absPath ABSPATH]

optional arguments:
  -h, --help            show this help message and exit
  --test                Setup one simulation, for check if setting is correct without submiting
  --testAndSubmit, --ts
                        Setup one simulation and submit job
  --path PATH, --p PATH
                        Path to file containting simulation settings
  --absPath ABSPATH, --ap ABSPATH
                        Absolute path to topdirectory where flexpart simulation will be created
```
For testing jobscript.py --ts submit one 
flexpart simulation to the queue, and jobscript --test setup flexpart simulation without submitting to 
the jobqueue
