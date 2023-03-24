#!/bin/bash
#SBATCH --account=COMP90024
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --output=1node8cores_py37.txt
#SBATCH --time=0-00:00:40
module load python/3.7.4
module load gcccore/8.3.0
module load mpi4py/3.0.2-timed-pingpong

source ~/venvs/venv-3.7.4/bin/activate

mpirun python3 main.py --location /../../sal.json --data ../../smallTwitter.json
