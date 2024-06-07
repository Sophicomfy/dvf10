#!/bin/bash

# Check if the directory is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

# Assign the directory argument to a variable
TARGET_DIR=$1

# Check if the provided argument is a valid directory
if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: $TARGET_DIR is not a valid directory."
  exit 1
fi

# Update read/write permissions for all files recursively
find "$TARGET_DIR" -type f -exec chmod u+rw {} \;

# Provide feedback
echo "Updated read/write permissions for all files in $TARGET_DIR"
