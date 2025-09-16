# VOD Downloader

Automatically download and organize VODs from https://archive.wubby.tv/vods/public/ for Plex or Jellyfin media servers.

## Features

- **Scheduled Monitoring**: Automatically checks for new VODs daily at a configurable time
- **Smart Organization**: Organizes downloaded files using customizable folder structures and naming patterns
- **Plex/Jellyfin Ready**: Formats files and folders for optimal media server compatibility
- **Sequential Downloads**: Downloads files one at a time with clean renaming after each download
- **Enhanced Console Output**: Real-time progress display with detailed status information
- **Intelligent File Naming**: Extracts clean titles and timestamps from VOD filenames
- **Accurate Date Detection**: Uses HTTP metadata for precise file creation dates
- **Archive-Style Organization**: Month-year folder structure matching the source site
- **Simplified Organization**: Month-year folder structure with date information in filename
- **Size Filtering**: Optional file size limits to manage storage
- **Progress Tracking**: Maintains a database of downloaded files to avoid duplicates
- **Robust Error Handling**: Comprehensive logging and error recovery

## Quick Start

1. **Clone or download the project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure settings**:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your preferences:
     ```
     DOWNLOAD_PATH="D:\Media\TV\Wubby Vods"
     CHECK_TIME=02:00
     FOLDER_STRUCTURE={month_name} - {year}
     FILE_NAME_PATTERN={title} - {date}
     ```

4. **Run the downloader**:
   ```bash
   # Run once immediately then start scheduled monitoring
   python main.py --check-now
   
   # Or start scheduled monitoring only
   python main.py
   ```

## What You'll See

The VOD downloader provides detailed console output so you can monitor exactly what's happening:

### **Scanning Phase:**
```
🔍 SCANNING FOR NEW VODs
📡 Checking: https://archive.wubby.tv/vods/public/
📁 Scanning subdirectory: apr_2023/
🕐 Getting actual file date from HTTP metadata...
✅ Found metadata date: 2023-04-13 19:04:19
🆕 Found new VOD: HUGE ANNOUNCEMENT - HIGH LAUGH YOU LOSE
```

### **Download Phase:**
```
🎯 PROCESSING VOD 1/3
Title: HUGE ANNOUNCEMENT - HIGH LAUGH YOU LOSE
Time: 19:04:19
Date: 2023-04-13

============================================================
DOWNLOADING: HUGE ANNOUNCEMENT - HIGH LAUGH YOU LOSE
Original filename: 2025-09-16_19_04_19.413015_HUGE%20ANNOUNCEMENT.mp4
File size: 2.1 GB
[████████████████████████████████] 100% 2.1GB/2.1GB

✅ DOWNLOAD COMPLETE!
📁 RENAMING FILE...
From: 2025-09-16_19_04_19.413015_HUGE%20ANNOUNCEMENT.mp4
To:   HUGE ANNOUNCEMENT - HIGH LAUGH YOU LOSE - 2023-04-13.mp4
✅ RENAME COMPLETE!
Final location: D:\Media\TV\Wubby Vods\apr - 2023\HUGE ANNOUNCEMENT - HIGH LAUGH YOU LOSE - 2023-04-13.mp4
```

## Configuration

All settings are configured through environment variables in the `.env` file:

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `DOWNLOAD_PATH` | Where to save downloaded VODs | `./downloads` or `C:\Media\VODs` |
| `CHECK_TIME` | Daily check time (24-hour format) | `02:00` (2:00 AM) |

### Optional Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `VOD_BASE_URL` | `https://archive.wubby.tv/vods/public/` | Base URL to scan |
| `DEBUG` | `false` | Enable debug logging |
| `MAX_CONCURRENT_DOWNLOADS` | `3` | ⚠️ **Not used** - Downloads are sequential |
| `MAX_FILE_SIZE_MB` | `0` | File size limit (0 = no limit) |
| `FOLDER_STRUCTURE` | `{month_name} - {year}` | Directory organization pattern |
| `FILE_NAME_PATTERN` | `{title} - {date}` | File naming pattern |

### Organization Patterns

Available variables for `FOLDER_STRUCTURE` and `FILE_NAME_PATTERN`:

- `{year}` - 4-digit year (e.g., 2025)
- `{month}` - 2-digit month (e.g., 09)
- `{month_name}` - 3-letter month name (e.g., apr, sep)
- `{day}` - 2-digit day (e.g., 16)
- `{date}` - Full date (YYYY-MM-DD format)
- `{time}` - Extracted timestamp (e.g., 19:04:19)
- `{title}` - Clean extracted video title
- `{original_name}` - Original filename (file pattern only)

### Example Configurations

**For month-year organization matching archive structure (default)**:
```
FOLDER_STRUCTURE={month_name} - {year}
FILE_NAME_PATTERN={title} - {date}
# Result: apr - 2023/PUBLIC MENACE - HANDICAPABLE - 2023-04-13.mp4
```

**For simple year-based organization**:
```
FOLDER_STRUCTURE={year}
FILE_NAME_PATTERN={title} - {date}
# Result: 2025/PUBLIC MENACE - HANDICAPABLE - 2025-09-16.mp4
```

**For time-based naming**:
```
FOLDER_STRUCTURE={month_name} - {year}
FILE_NAME_PATTERN={time} - {title} - {date}
# Result: sep - 2025/19:04:19 - HUGE ANNOUNCEMENT - 2025-09-16.mp4
```

**For Plex TV Shows format**:
```
FOLDER_STRUCTURE=Wubby VODs/Season {year}
FILE_NAME_PATTERN=Wubby VODs - S{year}E{month}{day} - {title}
```

**For date-based organization**:
```
FOLDER_STRUCTURE={year}/{month}
FILE_NAME_PATTERN={title} - {date}
# Result: 2025/09/PUBLIC MENACE - 2025-09-16.mp4
```

## Usage

### Download Process

The VOD downloader uses a **sequential download and rename process** for optimal file organization:

1. **Scan**: Searches the archive for new VOD files
2. **Download**: Downloads each file with its original filename  
3. **Rename**: Immediately renames to clean format (e.g., "PUBLIC MENACE - HANDICAPABLE - 2025-09-16.mp4")
4. **Repeat**: Moves to next file with 2-second delay between downloads

This approach ensures:
- ✅ Clean, readable filenames with date information
- ✅ Simple folder structure organized by year only
- ✅ No partial/corrupt files in your media library
- ✅ Real-time progress visibility
- ✅ Respectful server usage with delays

### Automatic Mode
```bash
python main.py
```
Runs continuously, checking for new VODs at the configured time daily.

### Manual Check
```bash
python main.py --check-now
```
Performs an immediate check for new VODs, then continues with scheduled monitoring.

### Console Output

The enhanced console interface provides real-time feedback:

- **🔍 Scanning**: Shows which directories are being checked and new VODs found
- **📊 Progress**: Displays current VOD being processed (X/Y format) 
- **⬬ Downloads**: Real-time progress bars with file size and speed
- **📁 Organization**: Shows file rename operations and final locations
- **📈 Summary**: Running totals and final session statistics

All major operations include visual indicators (emojis) and clear formatting for easy monitoring.

## File Organization

The VOD downloader uses a **simplified organization structure** designed for easy browsing and media server compatibility:

### **Folder Structure:**
```
Download Folder/
├── apr - 2023/
│   ├── STREAM TITLE 1 - 2023-04-15.mp4
│   ├── STREAM TITLE 2 - 2023-04-20.mkv
│   └── ...
├── sep - 2025/
│   ├── PUBLIC MENACE - HANDICAPABLE - 2025-09-16.mp4
│   ├── HUGE ANNOUNCEMENT - HIGH LAUGH - 2025-09-17.mp4
│   └── ...
└── ...
```

### **Benefits of This Structure:**
- ✅ **Matches Archive**: Folder names mirror the source site structure (apr_2023 → apr - 2023)
- ✅ **Chronological Browsing**: Easy to find content by time period
- ✅ **Complete Information**: Date is preserved in the filename
- ✅ **Clean Titles**: Automatically removes timestamps, URL encoding, and artifacts
- ✅ **Media Server Friendly**: Easy to browse in Plex/Jellyfin

### Logs
- Console output shows current activity with enhanced visual feedback
- Detailed logs saved to `vod_downloader.log`
- Downloaded files tracked in `downloaded_files.json`

## File Structure

```
VOD Downloader/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Configuration template
├── .env               # Your configuration (create this)
├── src/
│   ├── __init__.py
│   ├── config.py      # Configuration management
│   ├── vod_scanner.py # Archive scanning logic
│   └── vod_downloader.py # Download and organization
├── vod_downloader.log # Application logs
└── downloaded_files.json # Download tracking database
```

## Troubleshooting

### Common Issues

**Files have messy names**:
- The downloader automatically cleans up VOD titles by:
  - Removing URL encoding (`%20` → spaces)
  - Extracting timestamps from filenames  
  - Removing timestamp prefixes (e.g., "2025-09-16 10_25_12.365370_")
  - Removing file artifacts (`_40`, `gg`, etc.)
  - Converting underscores to spaces
- Final files will have clean names like "PUBLIC MENACE - HANDICAPABLE - 2025-09-16.mp4"
- If no time is extracted, it's omitted entirely (no "Unknown Time" text)

**Downloads not starting**:
- Check network connectivity to archive.wubby.tv
- Verify `DOWNLOAD_PATH` exists and is writable
- Check logs for specific error messages

**Files not found**:
- The archive structure may have changed
- Check if the base URL is still valid
- Enable debug logging for detailed scanning information

**Downloads seem slow**:
- Downloads are intentionally **sequential** (one at a time) to:
  - Ensure clean file renaming after each download
  - Be respectful to the server with 2-second delays
  - Provide clear progress visibility for each file
- This is by design and cannot be changed to concurrent downloads

**Permission errors**:
- Ensure the download path is writable
- On Windows, avoid special folders like `System32`
- Consider running with elevated permissions if needed

### Debug Mode

Enable detailed logging:
```
DEBUG=true
```
This will show:
- Individual file discoveries
- Download progress bars
- Detailed error messages
- HTTP request information

## Development

### Running Tests
```bash
# Install development dependencies
pip install pytest

# Run tests
pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

This project is for personal use. Respect the content creator's rights and terms of service.
