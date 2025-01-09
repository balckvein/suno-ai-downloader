#!/usr/bin/env python3

import csv
import os
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests
from pathlib import Path
import sys

MAX_RETRIES = 3
MAX_WORKERS = 4


def download_file(url, filename, total_size=None):
    """Download a file with progress bar and retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total = total_size or int(response.headers.get("content-length", 0))

            with open(filename, "wb") as f, tqdm(
                desc=Path(filename).name,
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)
            return True

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"\nRetrying {filename} (Attempt {attempt + 2}/{MAX_RETRIES})")
                time.sleep(2)
            else:
                print(f"\nFailed to download {filename}: {str(e)}")
                return False


def process_song(row):
    """Process a single song (for parallel processing)."""
    filename, url, description = row

    # Create full paths
    mp3_path = os.path.join("songs", filename)
    txt_path = os.path.join("songs", filename.replace(".mp3", ".txt"))

    # Skip if files already exist
    if os.path.exists(mp3_path) and os.path.exists(txt_path):
        print(f"Skipping existing file: {filename}")
        return

    # Save description to text file
    with open(txt_path, "w") as txt_file:
        txt_file.write(description)

    # Download MP3
    return download_file(url, mp3_path)


def main():
    """Main execution function."""
    # Create songs directory if it doesn't exist
    os.makedirs("songs", exist_ok=True)

    # Read the CSV file
    try:
        with open("songs.csv", "r") as file:
            next(file)  # Skip header
            reader = csv.reader(file)
            songs = list(reader)
    except FileNotFoundError:
        print("Error: songs.csv not found")
        sys.exit(1)

    print(f"Found {len(songs)} songs to process")

    # Process songs in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_song, songs))

    # Summary
    successful = sum(1 for r in results if r is not False)
    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {successful}/{len(songs)} songs")
    if successful != len(songs):
        print(f"Failed downloads: {len(songs) - successful}")


if __name__ == "__main__":
    main()
