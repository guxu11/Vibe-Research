#!/bin/bash
#SBATCH --job-name=ollama_summary
#SBATCH --output=ollama_summary.log
#SBATCH --gres=gpu:1
#SBATCH --time=04:00:00
#SBATCH --partition=gpucluster
#SBATCH --cpus-per-task=4

module load cuda/11.8  # 加载 GPU 依赖

# 强制切换到正确的工作目录
cd ~/project/Vibe-Research/src || exit 1

# 激活 Python 虚拟环境
source ~/project/Vibe-Research/.venv/bin/activate
export PATH=$HOME/.local/bin:$PATH

# 确保 Python 运行正常
echo "🔍 Python path: $(which python3)" | tee -a make_summaries.log
python3 --version | tee -a make_summaries.log

# 启动 Ollama 服务器
nohup ollama serve > ollama_server.log 2>&1 & disown
sleep 5  

# 确保 Ollama 服务器启动成功
RETRIES=15
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "🔄 Ollama still starting..." | tee -a make_summaries.log
    sleep 4
    ((RETRIES--))
    if [ $RETRIES -le 0 ]; then
        echo "❌ Ollama failed to start!" | tee -a make_summaries.log
        exit 1
    fi
done

echo "✅ Ollama is ready!" | tee -a make_summaries.log

# 运行 Python 脚本
echo "🚀 Running Python script..." | tee -a make_summaries.log
python3 -u make_summaries.py 2>&1 | tee -a make_summaries.log

echo "✅ Python script execution finished." | tee -a make_summaries.log

