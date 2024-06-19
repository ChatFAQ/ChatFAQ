#!/bin/bash

LOGFILE="memory_usage.log"

# Header for the log file
echo "Timestamp|PID|Process Name|RSS" > "$LOGFILE"

log_memory() {
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    # Use ps to get RSS of processes containing 'ray' or 'python'.
    # Write the results in pipe-delimited format to the log file.
    ps aux | grep -E '[r]ay|[p]ython' | awk -v ts="$timestamp" 'BEGIN{OFS="|"} {cmd=""; for (i=11; i<NF; i++) cmd=cmd $i " "; cmd=cmd $NF; print ts, $2, cmd, $6}' >> "$LOGFILE"
}

# Interval in seconds between measurements
INTERVAL=5

while true; do
    log_memory
    sleep $INTERVAL
done
