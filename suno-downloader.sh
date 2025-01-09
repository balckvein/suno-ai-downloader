#!/bin/bash

# Check if songs.csv exists
if [ ! -f "songs.csv" ]; then
    echo "Error: songs.csv not found"
    exit 1
fi

# Create songs directory if it doesn't exist
mkdir -p songs

# Skip header line and process each row
tail -n +2 songs.csv | while IFS=, read -r name url prompt; do
    # Remove quotes if present
    name=$(echo "$name" | tr -d '"')
    url=$(echo "$url" | tr -d '"')

    echo "Downloading: $name"
    # Create prompt file alongside the mp3 in the songs directory
    echo "$prompt" > "songs/${name%.*}.txt"
    # Download the mp3 to the songs directory
    curl -L -o "songs/$name" "$url"

    # Wait a bit between downloads
    sleep 1
done
