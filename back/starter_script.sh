#!/bin/bash

# Start the first process
echo "Starting driver pointing to: ray:6379..."

/.venv/bin/ray start --address=ray:6379 --num-cpus 0 --num-gpus 0

echo "...driver started, address: ${REMOTE_RAY_CLUSTER_ADDRESS_HEAD}"

# Start the second process

if [ -z "$IS_CELERY" ]; then
    echo "Starting daphne..."
    modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application &
else
    echo "Starting celery worker..."
    modelw-docker run python -m celery -A back.config worker -l INFO -E --pool threads --concurrency 2 &
fi

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
