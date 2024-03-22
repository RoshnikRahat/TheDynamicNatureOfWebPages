#!/bin/bash

# Path to the script (modify if needed)
SCRIPT_PATH="./cssDownload.py"  # Use relative path for portability

# Function to run script.py with URL in a separate terminal and wait
run_script_with_wait() {
  local url="$1"
  gnome-terminal --wait -- python3 "$SCRIPT_PATH" "$url" &  # Run in background with &
  echo "Running instance for URL: $url (background process)"
}

# Read each URL from websites.txt and run script.py for each URL in background
while IFS= read -r url || [[ -n "$url" ]]; do
  run_script_with_wait "$url"
done < "websites.txt"

echo "All script instances started. Waiting for completion..."

# Wait for all background processes to finish (if necessary)
wait  # Wait for all background processes spawned with `&` to finish

echo "All script instances completed."
