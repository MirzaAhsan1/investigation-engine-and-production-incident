#!/bin/bash

set -e

# ==========================================================
# Disk Usage
# ==========================================================

DISK_USAGE=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')


# ==========================================================
# Disk I/O Wait
# ==========================================================

CPU_LINE=$(grep '^cpu ' /proc/stat)

read -r CPU USER NICE SYSTEM IDLE IOWAIT IRQ SOFTIRQ STEAL GUEST GUEST_NICE <<< "$CPU_LINE"

TOTAL=$((USER + NICE + SYSTEM + IDLE + IOWAIT + IRQ + SOFTIRQ + STEAL))

if [ "$TOTAL" -gt 0 ]; then
    DISK_IO_WAIT=$(awk \
        -v iowait="$IOWAIT" \
        -v total="$TOTAL" \
        'BEGIN { printf "%.2f", (iowait / total) * 100 }'
    )
else
    DISK_IO_WAIT="0.00"
fi


# ==========================================================
# Output
# ==========================================================

echo "disk_usage=$DISK_USAGE disk_io_wait=$DISK_IO_WAIT"