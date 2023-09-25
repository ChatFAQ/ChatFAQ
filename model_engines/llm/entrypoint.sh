#!/bin/bash
huggingface-cli login --token $HUGGINGFACE_KEY # login to huggingface for private model access

echo "Model name: $MODEL"

/root/miniconda/envs/vllm_venv/bin/python -m vllm.entrypoints.api_server --host $HOST --port $PORT --swap-space $SWAP_SPACE --model $MODEL --tokenizer $MODEL --tensor-parallel-size $NUM_GPUS ----gpu-memory-utilization $GPU_MEMORY_UTILIZATION
