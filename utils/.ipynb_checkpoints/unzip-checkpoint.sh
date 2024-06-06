#!/bin/bash

# Ask the user for the filename to unzip
echo "Please enter the filename to unzip:"
read FILENAME

# Validate if the filename was provided
if [ -z "$FILENAME" ]; then
    echo "Error: No filename given"
    exit 1
fi

# Function to download and use a standalone unzip binary
download_and_unzip() {
    TMP_DIR=$(mktemp -d)
    cd "$TMP_DIR" || exit 1
    wget https://github.com/ncbi/tk-tools/releases/download/1.0/unzip -O unzip
    chmod +x unzip
    ./unzip "$FILENAME" -d extracted_files
    mv extracted_files/* .
    rm -rf "$TMP_DIR"
}

# Check if unzip is available
if command -v unzip &> /dev/null; then
    # Unzip using the installed unzip command
    unzip "$FILENAME"
else
    # If unzip is not installed, download a standalone binary and unzip
    echo "unzip not found, downloading a standalone version..."
    download_and_unzip
fi
