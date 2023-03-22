#!/bin/bash
#SBATCH --ntasks=1
module load python/3.8.6
module load gcccore/10.2.0
source ~/venvs/venv-3.8.6/bin/activate

srun -n 1 python3 main.py --location /../../sal.json --data ../../smallTwitter.json

##DO NOT ADD/EDIT BEYOND THIS LINE##
##Job monitor command to list the resource usage
my-job-stats -a -n -s
