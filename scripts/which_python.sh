#!/bin/bash
#SBATCH --job-name=which_python
#SBATCH --output=test.log  # 让每个任务有单独的日志
#SBATCH --time=08:00:00
#SBATCH --partition=cpucluster
#SBATCH --cpus-per-task=4

echo "=== 🐍 Checking Python Info ==="
which python
python --version

# 检查 Python site-packages 路径
echo "=== 📂 Python Site Packages ==="
python -c "import sys; print('\n'.join(sys.path))"

# 列出已安装的 Python 包
echo "=== 📦 Installed Python Packages ==="
python -m pip list || echo "pip not found"

echo "✅ All checks completed!"