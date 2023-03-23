#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=0-00:00:40
module load python/3.8.6
module load gcccore/10.2.0
module load mpi4py/3.0.2-timed-pingpong
source ~/venvs/venv-3.8.6/bin/activate

mpirun python3 main.py --location /../../sal.json --data ../../smallTwitter.json
