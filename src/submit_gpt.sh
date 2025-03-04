#!/bin/bash
#SBATCH --job-name=gpt_summary
#SBATCH --output=gpt_summary.log  # 让每个任务有单独的日志
#SBATCH --time=12:00:00
#SBATCH --partition=cpucluster
#SBATCH --cpus-per-task=5

cd ~/project/Vibe-Research/src || exit 1

source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

echo "🚀 Running Python script"

python3 -u make_summaries_with_GPT.py

echo "✅ Python script execution finished."