#!/bin/bash
#SBATCH --account=COMP90024
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=1
#SBATCH --output=scenario_3.txt
#SBATCH --time=0-02:30:00
module load python/3.7.4
module load gcccore/8.3.0
module load mpi4py/3.0.2-timed-pingpong

source ~/venvs/venv-3.7.4/bin/activate

for i in {1..10}
do
  mpirun python3 ../code/main.py --location /../../sal.json --data /../../bigTwitter.json
  my-job-stats -a -n -s
done
