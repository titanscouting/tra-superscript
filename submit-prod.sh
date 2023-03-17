#!/bin/bash
#
#SBATCH --job-name=tra-superscript
#SBATCH --output=PROD_slurm-tra-superscript.out
#SBATCH --ntasks=8
#SBATCH --time=24:00:00
#SBATCH --mem-per-cpu=256
#SBATCH --mail-user=dsingh@imsa.edu
#SBATCH -p cpu-long

cd competition
python superscript.py verbose
