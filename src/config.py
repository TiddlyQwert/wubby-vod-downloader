"""
Configuration module for VOD Downloader
"""

import os
from pathlib import Path

class Config:
    """Configuration class that loads settings from environment variables"""
    
    def __init__(self):
        # Download settings
        self.download_path = Path(os.getenv('DOWNLOAD_PATH', './downloads')).resolve()
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '0'))
        
        # Scheduling
        self.check_time = os.getenv('CHECK_TIME', '02:00')
        
        # URLs
        self.vod_base_url = os.getenv('VOD_BASE_URL', 'https://archive.wubby.tv/vods/public/')
        
        # Organization
        self.folder_structure = os.getenv('FOLDER_STRUCTURE', '{year}/{month} - {date}')
        self.file_name_pattern = os.getenv('FILE_NAME_PATTERN', '{date} - {title}')
        
        # Logging
        self.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Ensure download path exists
        self.download_path.mkdir(parents=True, exist_ok=True)
    
    @property
    def max_file_size_bytes(self):
        """Convert max file size from MB to bytes"""
        if self.max_file_size_mb <= 0:
            return None
        return self.max_file_size_mb * 1024 * 1024
