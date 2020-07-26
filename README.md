# FLEXPART-script
Python script for managing and setting up FLEXPART simulation

## Discription:
- flexpart_simulation.py , input parameters and settings for the flexpart, and settings for the 
slurm jobscript
- params.py , store the different input parameters set in flexpart_simulation.py
- jobscript creates folder structure containing the specific inputfiles ,
slurm job script and submit jobscript to queue.

## Usage:
First configure the flexpart simulation in flexpart_simulation.py, then the simulation is submited to the
jobqueue by typing python jobscript.py. For testing jobscript.py --ts submit one 
flexpart simulation to the queue, and jobscript --test setup flexpart simulation without submitting to 
the jobqueue
