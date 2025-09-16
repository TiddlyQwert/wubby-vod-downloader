# VOD Downloader Project Instructions

This project is a Python-based VOD downloader that monitors https://archive.wubby.tv/vods/public/ for new files and organizes them for Plex/Jellyfin media servers.

## Key Features:
- Daily monitoring of streamer VOD database
- Automatic download of new VODs
- Simple month-year based folder organization
- Clean filename generation with date information
- Sequential downloads with enhanced console output
- Intelligent title extraction and cleanup
- Configurable download destination and schedule
- Environment-based configuration

## File Organization:
- **Folders**: Organized by month-year (e.g., `/apr - 2023/`)
- **Files**: Clean titles with date appended (e.g., `PUBLIC MENACE - HANDICAPABLE - 2023-04-13.mp4`)
- **Process**: Download → Rename → Move to next (sequential, not concurrent)
- **Date Source**: Uses HTTP metadata (Last-Modified headers) for accurate dates

## Development Guidelines:
- Use Python for web scraping and file management
- Implement configuration via environment variables
- Use sequential downloading for clean file management
- Follow simplified media server naming conventions
- Include comprehensive console output for monitoring
- Handle missing data gracefully (no "Unknown Time" fallbacks)
- Include proper error handling and logging

## Project Status: Complete
All setup tasks have been completed successfully:
✅ Project structure created
✅ Dependencies installed
✅ Configuration system implemented
✅ Sequential download system implemented
✅ Enhanced console output added
✅ Intelligent file naming and organization
✅ VS Code tasks configured
✅ Documentation complete
✅ Project tested and working
