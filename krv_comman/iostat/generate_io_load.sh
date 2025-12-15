#!/bin/bash
# Script to generate fake I/O load on a disk device at ~40 Gbps (5 GB/s)
# Basic usage - writes at ~40 Gbps for 60 seconds (default)
# ./generate_io_load.sh sda
# # Custom duration (e.g., 120 seconds)
# ./generate_io_load.sh sda 500 10 120

# # Parameters: device size_mb num_files duration_seconds
# # Example: 10 files of 500MB each = 5GB per cycle
# ./generate_io_load.sh sda 500 10 60
# This creates, writes, and deletes files to generate disk activity

set -e

# Default values
DEVICE="${1:-sda}"
TMP_DIR="/tmp/iostat_test"
# Target: 40 Gbps = 5 GB/s = 5000 MB/s
# Use 10 parallel files of 500MB each = 5GB per cycle to achieve ~5 GB/s
SIZE_MB="${2:-500}"  # Default 500MB per file (adjusted for 40 Gbps)
NUM_FILES="${3:-10}"  # Default 10 files in parallel
DURATION="${4:-60}"  # Default 60 seconds
BLOCK_SIZE="10M"  # Large block size for efficiency

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating I/O load on device: ${DEVICE} at ~40 Gbps (5 GB/s)${NC}"
echo -e "${YELLOW}File size: ${SIZE_MB}MB per file${NC}"
echo -e "${YELLOW}Number of parallel files: ${NUM_FILES}${NC}"
echo -e "${YELLOW}Total per cycle: $((SIZE_MB * NUM_FILES))MB (~$((SIZE_MB * NUM_FILES / 1024))GB)${NC}"
echo -e "${YELLOW}Duration: ${DURATION} seconds${NC}"
echo -e "${YELLOW}Temp directory: ${TMP_DIR}${NC}"
echo ""

# Find mount point for the device
MOUNT_POINT=$(findmnt -n -o TARGET /dev/${DEVICE} 2>/dev/null || echo "")
if [ -z "$MOUNT_POINT" ]; then
    # Try to find any mount point that might be on this device
    MOUNT_POINT=$(df -h | grep "/dev/${DEVICE}" | awk '{print $6}' | head -1)
fi

if [ -z "$MOUNT_POINT" ]; then
    echo -e "${RED}Error: Could not find mount point for /dev/${DEVICE}${NC}"
    echo "Using /tmp instead (will still generate I/O but may not be on ${DEVICE})"
    WORK_DIR="${TMP_DIR}"
else
    echo -e "${GREEN}Found mount point: ${MOUNT_POINT}${NC}"
    WORK_DIR="${MOUNT_POINT}/iostat_test"
fi

# Create working directory
mkdir -p "${WORK_DIR}"
echo -e "${GREEN}Working directory: ${WORK_DIR}${NC}"
echo ""

# Function to cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up...${NC}"
    # Kill any background dd processes
    pkill -f "dd if=/dev/urandom of=${WORK_DIR}" 2>/dev/null || true
    sleep 1
    rm -rf "${WORK_DIR}" 2>/dev/null || true
    echo -e "${GREEN}Cleanup complete!${NC}"
}

# Trap Ctrl+C and cleanup
trap cleanup EXIT INT TERM

# Function to write files in parallel
write_parallel() {
    local cycle=$1
    local file_count=$2
    local size_mb=$3
    local pids=()
    
    # Start parallel writes
    for i in $(seq 1 ${file_count}); do
        FILE="${WORK_DIR}/test_file_${cycle}_${i}.dat"
        dd if=/dev/urandom of="${FILE}" bs=${BLOCK_SIZE} count=$((size_mb / 10)) status=none 2>/dev/null &
        pids+=($!)
    done
    
    # Wait for all writes to complete
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    sync
}

# Function to generate I/O load at high speed
generate_io() {
    local cycle=$1
    local file_count=$2
    local size_mb=$3
    
    CYCLE_START=$(date +%s.%N)
    
    # Phase 1: Write files in parallel
    write_parallel ${cycle} ${file_count} ${size_mb}
    
    WRITE_END=$(date +%s.%N)
    WRITE_TIME=$(echo "$WRITE_END - $CYCLE_START" | bc)
    
    # Phase 2: Delete files (parallel)
    DELETE_START=$(date +%s.%N)
    for i in $(seq 1 ${file_count}); do
        rm -f "${WORK_DIR}/test_file_${cycle}_${i}.dat" &
    done
    wait  # Wait for all deletes to complete
    sync
    
    DELETE_END=$(date +%s.%N)
    TOTAL_TIME=$(echo "$DELETE_END - $CYCLE_START" | bc)
    
    # Calculate throughput
    DATA_WRITTEN_GB=$(echo "scale=3; ${size_mb} * ${file_count} / 1024" | bc)
    THROUGHPUT_GBPS=$(echo "scale=2; ${DATA_WRITTEN_GB} / ${WRITE_TIME}" | bc)
    THROUGHPUT_GBITS=$(echo "scale=2; ${THROUGHPUT_GBPS} * 8" | bc)
    
    echo -e "${GREEN}[$(date +%H:%M:%S)] Cycle ${cycle} | Write: ${WRITE_TIME}s | Speed: ~${THROUGHPUT_GBITS} Gbps (~${THROUGHPUT_GBPS} GB/s) | Total time: ${TOTAL_TIME}s${NC}" >&2
    
    # Return throughput for statistics (to stdout)
    echo "${THROUGHPUT_GBPS}"
}

# Check if bc is available for calculations
if ! command -v bc &> /dev/null; then
    echo -e "${RED}Error: 'bc' command not found. Please install it: sudo apt-get install bc${NC}"
    exit 1
fi

# Continuous mode (if duration > 0)
if [ "${DURATION}" -gt 0 ]; then
    START_TIME=$(date +%s)
    END_TIME=$((START_TIME + DURATION))
    CYCLE=0
    TOTAL_DATA_MB=0
    THROUGHPUTS=()
    
    echo -e "${GREEN}Running for ${DURATION} seconds (press Ctrl+C to stop early)${NC}"
    echo -e "${GREEN}Target: ~40 Gbps (5 GB/s)${NC}"
    echo ""
    
    while [ $(date +%s) -lt ${END_TIME} ]; do
        CYCLE=$((CYCLE + 1))
        TIME_REMAINING=$((END_TIME - $(date +%s)))
        
        if [ $((CYCLE % 5)) -eq 1 ] || [ $CYCLE -eq 1 ]; then
            echo ""
            echo -e "${GREEN}════════════════════════════════════════${NC}"
            echo -e "${GREEN}Cycle ${CYCLE} - Time remaining: ${TIME_REMAINING}s${NC}"
            echo -e "${GREEN}════════════════════════════════════════${NC}"
        fi
        
        # Generate I/O and capture throughput
        THROUGHPUT=$(generate_io ${CYCLE} ${NUM_FILES} ${SIZE_MB})
        THROUGHPUTS+=("${THROUGHPUT}")
        TOTAL_DATA_MB=$((TOTAL_DATA_MB + SIZE_MB * NUM_FILES))
        
        # Small delay to prevent overwhelming the system
        sleep 0.1
    done
    
    # Calculate statistics
    ELAPSED_TIME=$(echo "$(date +%s) - $START_TIME" | bc)
    TOTAL_DATA_GB=$(echo "scale=3; ${TOTAL_DATA_MB} / 1024" | bc)
    AVG_THROUGHPUT_GBPS=$(echo "scale=2; ${TOTAL_DATA_GB} / ${ELAPSED_TIME}" | bc)
    AVG_THROUGHPUT_GBITS=$(echo "scale=2; ${AVG_THROUGHPUT_GBPS} * 8" | bc)
    
    # Calculate max throughput
    MAX_THROUGHPUT=0
    for t in "${THROUGHPUTS[@]}"; do
        if (( $(echo "$t > $MAX_THROUGHPUT" | bc -l) )); then
            MAX_THROUGHPUT=$t
        fi
    done
    MAX_GBITS=$(echo "scale=2; ${MAX_THROUGHPUT} * 8" | bc)
    
    echo ""
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${GREEN}Duration completed!${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Total cycles: ${CYCLE}${NC}"
    echo -e "${YELLOW}Total data written: ~${TOTAL_DATA_GB} GB${NC}"
    echo -e "${YELLOW}Average throughput: ~${AVG_THROUGHPUT_GBITS} Gbps (~${AVG_THROUGHPUT_GBPS} GB/s)${NC}"
    echo -e "${YELLOW}Peak throughput: ~${MAX_GBITS} Gbps (~${MAX_THROUGHPUT} GB/s)${NC}"
    echo -e "${GREEN}════════════════════════════════════════${NC}"
else
    # Single cycle mode
    echo ""
    echo -e "${GREEN}Running single cycle at ~40 Gbps...${NC}"
    generate_io 1 ${NUM_FILES} ${SIZE_MB}
fi

echo ""
echo -e "${GREEN}I/O load generation complete!${NC}"

