#!/bin/bash

# Stop Ray if it is running
/.venv/bin/ray stop

# Clean up Ray temporary files on the head node
rm -rf /tmp/ray/*
rm -rf /tmp/ray/session_latest

/.venv/bin/ray start --head --port 6375 --num-cpus 0 --num-gpus 0 --dashboard-host 0.0.0.0

modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
