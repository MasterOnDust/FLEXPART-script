# FLEXPART-script
Python script for setting up many backward FLEXPART simulations. 

## Discription:
- jobscript.py creates folder structure containing the specific inputfiles. In addition it creates a slurm job script for submiting to the queue. 
The job is submitted as an array job and which can be devided into sub array jobs, to avoid having to many jobs in the queue at once. Multiple simulations
can also be assign to each job.

## Usage:
First configure your flexpart simulation by editing settings.json file. You can also change the default settings in the params.json file. 
```
usage: jobscript.py [-h] [--absPath ABSPATH] [--edate EDATE] [--bdate BDATE] path

positional arguments:
  path                  Path json to file containting simulation settings

optional arguments:
  -h, --help            show this help message and exit
  --absPath ABSPATH, --ap ABSPATH
                        Absolute path to topdirectory where flexpart simulation will be created
  --edate EDATE, --ed EDATE
                        date of last flexpart run
  --bdate BDATE, --bd BDATE
                        date of fist flexpart run
```
To test your FLEXPART simulation is configured correctly, you can run a test simulation directly in one of the simulation directories, which has been created. 

### Contact

If you got any questions or want to contribute, please contact me at ovehaugv@outlook.com
