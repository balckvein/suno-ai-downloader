#!/usr/bin/env python3

import csv
import os
import time
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
    try:
        # Skip empty or malformed rows
        if not row or len(row) != 3:
            print(f"Skipping invalid row: {row}")
            return False

        filename, url, description = row

        # Skip if any required field is empty
        if not all([filename.strip(), url.strip(), description.strip()]):
            print(f"Skipping row with empty fields: {filename}")
            return False

        # Create full paths
        mp3_path = os.path.join("songs", filename)
        txt_path = os.path.join("songs", filename.replace(".mp3", ".txt"))

        # Skip if files already exist
        if os.path.exists(mp3_path) and os.path.exists(txt_path):
            print(f"Skipping existing file: {filename}")
            return True

        # Save description to text file
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(description.strip())

        # Download MP3
        return download_file(url, mp3_path)
    except Exception as e:
        print(
            f"Error processing song {filename if 'filename' in locals() else 'unknown'}: {str(e)}"
        )
        return False


def main():
    """Main execution function."""
    # Create songs directory if it doesn't exist
    os.makedirs("songs", exist_ok=True)

    # Read the CSV file
    try:
        with open("songs.csv", "r", encoding="utf-8") as file:
            # Use csv.reader with proper quoting and filtering
            reader = csv.reader(file, quoting=csv.QUOTE_ALL, skipinitialspace=True)
            next(reader)  # Skip header
            # Filter out empty rows and validate row length
            songs = [row for row in reader if row and len(row) == 3]
    except FileNotFoundError:
        print("Error: songs.csv not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        sys.exit(1)

    if not songs:
        print("No valid songs found in CSV")
        sys.exit(1)

    print(f"Found {len(songs)} valid songs to process")

    # Process songs in parallel
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_song, songs))

    # Summary
    successful = sum(1 for r in results if r is True)
    print(f"\nDownload complete!")
    print(f"Successfully downloaded: {successful}/{len(songs)} songs")
    if successful != len(songs):
        print(f"Failed downloads: {len(songs) - successful}")


if __name__ == "__main__":
    main()
