#!/bin/bash
#SBATCH --job-name=ollama_summary
#SBATCH --output=ollama_summary_%A_%a.log  # 让每个任务有单独的日志
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH --partition=gpucluster
#SBATCH --cpus-per-task=4
#SBATCH --array=0-4  # 提交 5 个任务，参数从 0 到 4 变化

# 强制切换到正确的工作目录
cd ~/project/Vibe-Research/src || exit 1

# 激活 Python 虚拟环境
source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

# 确保 Python 运行正常
echo "🔍 Python path: $(which python3)" | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log
python3 --version | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log

# 启动 Ollama 服务器
nohup ollama serve > ollama_server_${SLURM_ARRAY_TASK_ID}.log 2>&1 & disown
sleep 5

# 确保 Ollama 服务器启动成功
RETRIES=15
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "🔄 Ollama still starting..." | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log
    sleep 4
    ((RETRIES--))
    if [ $RETRIES -le 0 ]; then
        echo "❌ Ollama failed to start!" | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log
        exit 1
    fi
done

echo "✅ Ollama is ready!" | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log

# 运行 Python 脚本，每个任务的第一个参数不同
echo "🚀 Running Python script with param ${SLURM_ARRAY_TASK_ID}..." | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log
python3 -u make_summaries.py ${SLURM_ARRAY_TASK_ID} 0 2>&1 | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log

echo "✅ Python script execution finished." | tee -a make_summaries_${SLURM_ARRAY_TASK_ID}.log
