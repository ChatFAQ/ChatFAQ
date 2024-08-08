#!/bin/bash

export RAY_task_events_max_num_task_in_gcs=100

/.venv/bin/ray start --head --port 6375 --metrics-export-port=8080 --num-cpus 0 --num-gpus 0 --dashboard-host 0.0.0.0 --object-store-memory 500000000

# /.venv/bin/memray run -f --output mem.bin /.venv/bin/daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
# modelw-docker run daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
modelw-docker run gunicorn -b 0.0.0.0:8000 back.config.asgi:application -k uvicorn.workers.UvicornWorker
