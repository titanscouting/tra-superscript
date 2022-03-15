#!/bin/bash
#
#SBATCH --job-name=tra-superscript
#SBATCH --output=slurm-tra-superscript.out
#SBATCH --ntasks=8
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=256
#SBATCH --mail-user=dsingh@imsa.edu
#SBATCH -p cpu-long

unset XDG_RUNTIME_DIR
/home/tools/anaconda3/bin/conda init
source ~/.bashrc
source activate base
cd competition
python superscript.py debug
