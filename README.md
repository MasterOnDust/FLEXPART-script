# FLEXPART-script
Python script for setting up many backward FLEXPART simulations. 

## Discription:
- jobscript.py creates folder structure containing the specific inputfiles. In addition it creates a slurm job script for submiting to the queue. 
The job is submitted as an array job and which can be devided into sub array jobs, to avoid having to many jobs in the queue at once. Multiple simulations
can also be assign to each job.

## Usage:
First configure your flexpart simulation by editing settings.json file. 
```
usage: jobscript.py [-h] [--absPath ABSPATH] [--edate EDATE] [--path_to_forcing PATH_TO_FORCING] [--bdate BDATE] [--per_location] path

Python script for setting up flexpart backward simulations based on model settings specified in a json file. Can either setup the simulations in a per
time step config or per location config

positional arguments:
  path                  Path json to file containting simulation settings

optional arguments:
  -h, --help            show this help message and exit
  --absPath ABSPATH, --ap ABSPATH
                        Absolute path to topdirectory where flexpart simulation will be created
  --edate EDATE, --ed EDATE
                        date of last flexpart run
  --path_to_forcing PATH_TO_FORCING, --pf PATH_TO_FORCING
                        path to model forcing
  --bdate BDATE, --bd BDATE
                        date of fist flexpart run
  --per_location, --pl  setup a flexpart simulation for each location
```
To test your FLEXPART simulation is configured correctly, you can run a test simulation directly in one of the simulation directories, which has been created. The script creates sbatch scripts that can be submitted to the cluster by using:
```
find ./ -type f -name "*.sh" -exec sbatch {} \;

```

## Contact

If you got any questions or want to contribute, please contact me at ovehaugv@outlook.com
