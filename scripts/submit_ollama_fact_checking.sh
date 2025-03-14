#!/bin/bash
#SBATCH --job-name=ollama_fact_checking
#SBATCH --output=ollama_summary_%A_%a.log  # 让每个任务有单独的日志
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --partition=gpucluster
#SBATCH --cpus-per-task=4
#SBATCH --array=0-3

cd ~/project/Vibe-Research/src || exit 1

# 激活 Python 虚拟环境
source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

# **绑定 GPU**
export CUDA_VISIBLE_DEVICES=$SLURM_ARRAY_TASK_ID
export OLLAMA_CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES

# **分配 Ollama 端口**
PORT=$((11434 + SLURM_ARRAY_TASK_ID))
export OLLAMA_HOST="127.0.0.1:${PORT}"

# **启动 Ollama 服务器**
nohup ollama serve > ollama_server_${SLURM_ARRAY_TASK_ID}.log 2>&1 & disown
sleep 5

# **等待 Ollama 启动**
RETRIES=15
while ! curl -s http://127.0.0.1:${PORT}/api/tags > /dev/null; do
    echo "🔄 Ollama still starting on port ${PORT}..."
    sleep 4
    ((RETRIES--))
    if [ $RETRIES -le 0 ]; then
        echo "❌ Ollama failed to start!"
        exit 1
    fi
done

echo "✅ Ollama is ready on ${PORT}!"

# **运行 Python 脚本**
echo "🚀 Running Python script with param: ${SLURM_ARRAY_TASK_ID} on GPU ${CUDA_VISIBLE_DEVICES}"
python3 -u fact_checking.py "${SLURM_ARRAY_TASK_ID}" "${OLLAMA_HOST}"

echo "✅ Python script execution finished."
