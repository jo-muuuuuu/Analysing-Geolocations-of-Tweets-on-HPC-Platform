#!/bin/bash
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --output=2node8core.txt
#SBATCH --time=0-00:15:00
module load python/3.7.4
module load gcccore/10.2.0
module load mpi4py/3.0.2-timed-pingpong
source ~/venvs/venv-3.7.4/bin/activate

mpirun python3 main.py --location /../../sal.json --data ../../bigTwitter.json
