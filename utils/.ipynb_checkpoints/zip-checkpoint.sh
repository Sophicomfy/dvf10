#!/bin/bash

# Ask for the path to the folder to zip
read -p "Enter the path to the folder you want to zip: " folder_path

# Validate that the folder exists
if [ ! -d "$folder_path" ]; then
    echo "The provided folder path does not exist. Please check the path and try again."
    exit 1
fi

# Ask for the output directory where the zip file should be created
read -p "Enter the folder path where you want to create the zip file: " output_folder

# Validate that the output folder exists
if [ ! -d "$output_folder" ]; then
    echo "The output folder path does not exist. Please check the path and try again."
    exit 1
fi

# Extract the folder name and create a zip file name
folder_name=$(basename "$folder_path")
zip_file="${output_folder}/${folder_name}.zip"

# Change to the parent directory of the target folder
cd "$(dirname "$folder_path")" || exit

# Zip only the contents of the folder
zip -r "$zip_file" "$(basename "$folder_path")" && echo "Folder zipped successfully."

# Provide the link (path) to the zip file
echo "The zip file has been created at: $zip_file"
