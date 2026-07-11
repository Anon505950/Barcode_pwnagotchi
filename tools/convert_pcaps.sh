#!/bin/bash

# Define source and destination directories
SRC_DIR="/root/handshakes"
DEST_DIR="/home/pi/hash"

# Counters
seen=0
processed=0

# Check if hcxpcapngtool is installed
if ! command -v hcxpcapngtool &> /dev/null; then
    echo "Error: hcxpcapngtool is not installed. Please install hcxtools."
    exit 1
fi

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

echo "Starting batch conversion from $SRC_DIR to $DEST_DIR..."

# Loop through all pcap and pcapng files in the source directory
for file in "$SRC_DIR"/*.pcap "$SRC_DIR"/*.pcapng; do
    [ -e "$file" ] || continue

    seen=$((seen+1))

    filename=$(basename "$file")
    echo "Processing: $filename"

    # Convert and save to the destination folder with .hc22000 extension
    output="$DEST_DIR/${filename%.*}.hc22000"
    hcxpcapngtool -o "$output" "$file"

    # Count only if the output file is non‑empty
    if [[ -s "$output" ]]; then
        processed=$((processed+1))
    fi
done

echo "Batch conversion complete. Files saved in $DEST_DIR."
echo ""
echo "========== SUMMARY =========="
echo "Total files seen:        $seen"
echo "Total hashes generated:  $processed"
echo "Total failed/incomplete: $((seen - processed))"
echo "============================="

