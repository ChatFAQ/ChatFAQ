#!/bin/bash

/.venv/bin/ray start --head --port 6375 --dashboard-host 0.0.0.0

modelw-docker run python -m daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
