#!/bin/bash --login

#SBATCH --job-name=MCMC_FMM

#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00

# Load modules and activate conda environment
ml purge
ml load Miniforge3
ml load powertools
conda activate UQ_Project

# Print job information
echo "Job started at $(date)"
echo "Running on host $(hostname)"

# Run the Python script
python MCMC_FMM_Inference.py --HS 20

# python MCMC_FMM_Inference_PostProcessing.py --HS 20

echo "Job finished at $(date)"