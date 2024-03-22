#!/bin/bash

# Path to the script.py
SCRIPT="cssDownload.py"

# Read each URL from websites.txt and run script.py for each URL
while IFS= read -r url || [[ -n "$url" ]]; do
    echo "Running instance for URL: $url"
    python3 "$SCRIPT" "$url"
done < "websites.txt"

