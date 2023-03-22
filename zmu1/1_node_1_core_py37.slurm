#!/bin/bash
#SBATCH --ntasks=1
module load python/3.7.4
module load gcccore/10.2.0
module load mpi4py/3.0.2-timed-pingpong

source ~/venvs/venv-3.7.4/bin/activate

srun -n 1 python3 main.py --location /../../sal.json --data ../../smallTwitter.json

##DO NOT ADD/EDIT BEYOND THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s
