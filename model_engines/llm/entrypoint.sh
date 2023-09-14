#!/bin/bash
/root/miniconda/envs/vllm_venv/bin/python -m vllm.entrypoints.api_server --host 0.0.0.0 --port $PORT --swap-space $SWAP_SPACE
