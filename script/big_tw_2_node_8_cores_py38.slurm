#!/bin/bash
#SBATCH --account=COMP90024
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --output=big_2node8core_py38.txt
#SBATCH --time=0-00:15:00
module load python/3.8.6
module load gcccore/10.2.0
module load mpi4py/3.0.2-timed-pingpong

source ~/venvs/venv-3.8.6/bin/activate

mpirun python3 main.py --location /../../sal.json --data ../../bigTwitter.json
