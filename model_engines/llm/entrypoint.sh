#!/bin/bash
huggingface-cli login --token $HUGGINGFACE_KEY # login to huggingface for private model access
/root/miniconda/envs/vllm_venv/bin/python -m vllm.entrypoints.api_server --host 0.0.0.0 --port $PORT --swap-space $SWAP_SPACE
