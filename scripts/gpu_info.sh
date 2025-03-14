#!/bin/bash
#SBATCH --job-name=gpu_info
#SBATCH --output=ollama_summary_%A.log  # 让每个任务有单独的日志
#SBATCH --gres=gpu:1
#SBATCH --time=08:00:00
#SBATCH --partition=gpucluster
#SBATCH --cpus-per-task=4

nvidia-smi