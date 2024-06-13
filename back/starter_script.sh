#!/bin/bash

# /.venv/bin/memray run -f --output mem.bin /.venv/bin/daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
modelw-docker run daphne -b 0.0.0.0 -p 8000 back.config.asgi:application
