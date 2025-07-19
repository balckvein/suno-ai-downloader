# Suno Music Downloader

A set of tools to download your music from Suno.ai with organized filenames and prompts.

## Setup

1. Clone this repository
2. Install Python requirements:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### 1. Get Song Data

1. Login to https://suno.com/me
2. Open browser developer tools (F12)
3. Copy and paste the contents of `getData.js` into the console
4. Copy the output and save it to `songs.csv`

You can skip this step if you run `suno-downloader.py --all`.

The script will generate a CSV with:
- Formatted filenames (with random ID)
- Download URLs
- Original prompts and UUIDs

### 2. Download Songs

Run the Python downloader:
```bash
python3 suno-downloader.py
```

Options:
```bash
# Fetch every track using the API
python3 suno-downloader.py --all

# Use a custom CSV file
python3 suno-downloader.py --csv my_songs.csv
```

### Features

- **Fast Parallel Downloads**: Downloads 4 files simultaneously
- **Smart File Handling**:
  - Skips existing files automatically
  - Creates organized filenames with IDs
  - Preserves original UUIDs in text files
- **Progress Tracking**:
  - Real-time progress bars for each download
  - Download speed and size information
  - Completion summary with success/failure counts
- **Error Handling**:
  - Automatic retry on failed downloads (up to 3 attempts)
  - Detailed error reporting
  - Graceful handling of network issues

## Output Structure

```
songs/
  ├── song-name-id-xxxxx.mp3  # Organized filename with random ID
  └── song-name-id-xxxxx.txt  # Matching text file with prompt
```

Text files contain:
```
Original filename: uuid.mp3

Prompt:
Your original generation prompt
```

## Files

- `getData.js` - Browser script to extract song data
- `suno-downloader.py` - Python script with parallel download capability
- `requirements.txt` - Python package dependencies
- `songs.csv` - Generated list of songs to download

## Technical Details

- Uses Python's ThreadPoolExecutor for parallel downloads
- Configurable number of simultaneous downloads (default: 4)
- Progress bars powered by tqdm
- Robust error handling with automatic retries
