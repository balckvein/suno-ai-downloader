#!/usr/bin/env python3

import argparse
import csv
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from tqdm import tqdm

MAX_RETRIES = 3
MAX_WORKERS = 4


def fetch_all_songs():
    """Retrieve all songs using the Suno API with basic pagination."""
    songs = []
    cursor = ""
    session = requests.Session()
    while True:
        params = {"cursor": cursor} if cursor else {}
        try:
            resp = session.get(
                "https://studio-api.suno.ai/api/feed/tracks", params=params
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"Error fetching songs: {e}")
            break

        data = resp.json()
        for item in data.get("items", []):
            title = (item.get("title") or item.get("id", "")).strip()
            uuid = item.get("id", "")
            if not uuid:
                continue
            if not title:
                title = uuid
            hash_id = uuid[:5]
            formatted_title = f"{title.lower().replace(' ', '-')}-id-{hash_id}.mp3"
            description = item.get("description", "No description available")
            full_desc = f"Original filename: {uuid}.mp3\n\nPrompt:\n{description}"
            songs.append([formatted_title, item.get("audio_url", ""), full_desc])

        cursor = data.get("nextCursor") or data.get("next_cursor")
        if not cursor:
            break
    return songs


def read_csv(csv_file: str):
    """Read song data from a CSV file."""
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file, quoting=csv.QUOTE_ALL, skipinitialspace=True)
        next(reader, None)
        return [row for row in reader if row and len(row) == 3]


def parse_args():
    parser = argparse.ArgumentParser(description="Download songs from Suno.ai")
    parser.add_argument(
        "--all", action="store_true", help="Retrieve all songs using the API"
    )
    parser.add_argument(
        "--csv",
        default="songs.csv",
        metavar="FILE",
        help="CSV file containing songs (default: songs.csv)",
    )
    return parser.parse_args()


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
    args = parse_args()

    # Create songs directory if it doesn't exist
    os.makedirs("songs", exist_ok=True)

    if args.all:
        songs = fetch_all_songs()
    else:
        try:
            songs = read_csv(args.csv)
        except FileNotFoundError:
            print(f"Error: {args.csv} not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            sys.exit(1)

    if not songs:
        print("No songs found to process")
        sys.exit(1)

    print(f"Found {len(songs)} songs to process")

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
