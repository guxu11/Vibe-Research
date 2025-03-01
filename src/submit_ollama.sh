#!/bin/bash
#SBATCH --job-name=ollama_summary    # Job name
#SBATCH --output=ollama_summary.log  # Log output file
#SBATCH --gres=gpu:1                 # Request 1 GPU
#SBATCH --time=04:00:00               # Maximum run time: 4 hours
#SBATCH --partition=gpucluster        # Run on the GPU cluster
#SBATCH --cpus-per-task=4             # Allocate 4 CPU cores

# Start Ollama server in the background
echo "Starting Ollama server..."
ollama serve > ollama_server.log 2>&1 &

# Wait for Ollama to be ready
sleep 5  # Give some time for the server to initialize

# Ensure Ollama uses GPU
export OLLAMA_ACCELERATE=1
export OLLAMA_NUM_GPU_LAYERS=100  # Allow more layers to utilize GPU acceleration

# Run the Python script
python3 make_summaries.py

