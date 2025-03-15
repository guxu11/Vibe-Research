#!/bin/bash
#SBATCH --job-name=gpt_summary
#SBATCH --output=gpt_fact_check_%A_%a.log
#SBATCH --time=12:00:00
#SBATCH --partition=cpucluster
#SBATCH --cpus-per-task=4
#SBATCH --array=0-3

cd ~/project/Vibe-Research/src || exit 1

source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

echo "🚀 Running Python script"

python3 -u fact_checking.py "${SLURM_ARRAY_TASK_ID}" "None"


echo "✅ Python script execution finished."