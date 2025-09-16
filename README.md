# Wubby VOD Downloader

Automatically downloads and organizes VODs from https://archive.wubby.tv/vods/public/ for Plex/Jellyfin media servers.

## Features

- **Daily monitoring** - Checks for new VODs once per day
- **Smart organization** - Month-year folders with clean filenames
- **Accurate dating** - Uses HTTP metadata for precise file dates
- **Sequential downloads** - Server-friendly with progress tracking
- **Configurable** - Customize folder structure and file naming

## Quick Start

1. **Clone and install:**
   ```bash
   git clone https://github.com/TiddlyQwert/wubby-vod-downloader.git
   cd wubby-vod-downloader
   pip install -r requirements.txt
   ```

2. **Configure:**
   ```bash
   cp .env.example .env
   # Edit .env with your download path
   ```

3. **Run:**
   ```bash
   # Check for VODs now
   python main.py --check-now
   
   # Start daily scheduler
   python main.py
   ```

## Configuration

Edit your `.env` file:

```bash
# Download destination
DOWNLOAD_PATH=D:\Media\TV\Wubby Vods

# Check time (24-hour format)
CHECK_TIME=02:00

# Folder structure
FOLDER_STRUCTURE={month_name} - {year}

# File naming
FILE_NAME_PATTERN={title} - {date}
```

## Example Output

Files are organized like this:
```
D:\Media\TV\Wubby Vods\
├── apr - 2023\
│   ├── HUGE ANNOUNCEMENT - 2023-04-20.mp4
│   └── HIGH LAUGH YOU LOSE - 2023-04-13.mp4
└── may - 2023\
    └── MEDIA SHARE SUNDAY - 2023-05-06.mp4
```

## Requirements

- Python 3.7+
- Internet connection
- Storage space for VODs