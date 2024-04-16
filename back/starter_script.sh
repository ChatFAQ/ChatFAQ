#!/bin/bash

# Start the first process
echo "Starting driver pointing to: ray:6375..."

/.venv/bin/ray start --address=ray:6375 --num-cpus 0 --num-gpus 0

echo "...driver started, address: ${REMOTE_RAY_CLUSTER_ADDRESS_HEAD}"

# Start the second process
modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
