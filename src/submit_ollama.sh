#!/bin/bash
#SBATCH --job-name=ollama_summary
#SBATCH --output=ollama_summary_%A_%a.log  # 让每个任务有单独的日志
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --partition=gpucluster
#SBATCH --cpus-per-task=4
#SBATCH --array=0-4


cd ~/project/Vibe-Research/src || exit 1

source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

nohup ollama serve > ollama_server_${SLURM_ARRAY_TASK_ID}.log 2>&1 & disown
sleep 5

RETRIES=15
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "🔄 Ollama still starting..."
    sleep 4
    ((RETRIES--))
    if [ $RETRIES -le 0 ]; then
        echo "❌ Ollama failed to start!"
        exit 1
    fi
done

echo "✅ Ollama is ready!"

echo "🚀 Running Python script with params:"
python3 -u make_summaries.py

echo "✅ Python script execution finished."
