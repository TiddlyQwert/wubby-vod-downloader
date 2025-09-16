"""
VOD Scanner module - Scans the archive for new VODs
"""

import requests
import logging
import re
import json
import os
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin, urlparse

class VODScanner:
    """Scans the VOD archive for new files"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.downloaded_files_db = Path('downloaded_files.json')
        self.downloaded_files = self._load_downloaded_files()
    
    def _load_downloaded_files(self):
        """Load the database of already downloaded files"""
        if self.downloaded_files_db.exists():
            try:
                with open(self.downloaded_files_db, 'r') as f:
                    return set(json.load(f))
            except Exception as e:
                self.logger.warning(f"Error loading downloaded files database: {e}")
        return set()
    
    def _save_downloaded_files(self):
        """Save the database of downloaded files"""
        try:
            with open(self.downloaded_files_db, 'w') as f:
                json.dump(list(self.downloaded_files), f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving downloaded files database: {e}")
    
    def _get_page_content(self, url):
        """Fetch and parse a web page"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _get_file_metadata_date(self, url):
        """Get file creation date from HTTP headers"""
        try:
            response = requests.head(url, timeout=30)
            response.raise_for_status()
            
            # Try to get Last-Modified date
            last_modified = response.headers.get('Last-Modified')
            if last_modified:
                # Parse HTTP date format: "Wed, 21 Oct 2015 07:28:00 GMT"
                from email.utils import parsedate_to_datetime
                return parsedate_to_datetime(last_modified)
                
        except Exception as e:
            self.logger.debug(f"Could not get metadata date for {url}: {e}")
        
        return None
    
    def _extract_vod_info(self, file_url, file_name):
        """Extract VOD information from filename and URL"""
        
        # Define date patterns used throughout the method
        date_patterns = [
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
            r'(\d{4})(\d{2})(\d{2})',    # YYYYMMDD
            r'(\d{2})-(\d{2})-(\d{4})',  # MM-DD-YYYY
            r'(\d{2})(\d{2})(\d{4})',    # MMDDYYYY
        ]
        
        date_obj = None
        
        # ONLY use HTTP metadata for date extraction
        print(f"� Getting actual file date from HTTP metadata...")
        metadata_date = self._get_file_metadata_date(file_url)
        if metadata_date:
            date_obj = metadata_date
            print(f"✅ Found metadata date: {date_obj.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"⚠️  No metadata date available, using current date as fallback")
            date_obj = datetime.now()
        
        # Extract title (remove common extensions and date patterns)
        title = file_name
        for ext in ['.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v']:
            if title.lower().endswith(ext):
                title = title[:-len(ext)]
                break
        
        # Remove date patterns from title
        for pattern in date_patterns:
            title = re.sub(pattern, '', title).strip(' -_')
        
        # Remove timestamp patterns that might be at the start (like "2025-09-16 10_25_12.365370")
        title = re.sub(r'^\d{4}-\d{2}-\d{2}[_\s]\d{1,2}[_:]\d{2}[_:]\d{2}(\.\d+)?[_\s]*', '', title)
        # Remove just date at start (like "2025-09-16_")
        title = re.sub(r'^\d{4}-\d{2}-\d{2}[_\s]*', '', title)
        
        # Clean up URL encoding and common artifacts
        import urllib.parse
        title = urllib.parse.unquote(title)  # Decode URL encoding like %20 -> space
        
        # Remove common filename artifacts
        title = re.sub(r'_\d+$', '', title)  # Remove trailing _40, _19, etc.
        title = re.sub(r'gg$', '', title)    # Remove trailing 'gg'
        title = re.sub(r'_+', ' ', title)    # Replace underscores with spaces
        title = re.sub(r'-+', ' - ', title)  # Clean up dashes
        title = re.sub(r'\s+', ' ', title)   # Normalize spaces
        title = title.strip(' -_')
        
        # Extract time from original filename if present
        time_match = re.search(r'(\d{1,2})[_:](\d{2})[_:](\d{2})', file_name)
        time_str = ""
        if time_match:
            hour, minute, second = time_match.groups()
            time_str = f"{hour.zfill(2)}:{minute}:{second}"
        
        return {
            'url': file_url,
            'original_name': file_name,
            'title': title or 'Untitled VOD',
            'time': time_str,
            'date': date_obj,
            'year': str(date_obj.year),
            'month': f"{date_obj.month:02d}",  # Numeric month (01-12)
            'month_name': date_obj.strftime('%b').lower(),  # Short month name (jan, feb, etc.)
            'day': f"{date_obj.day:02d}",
            'date_str': date_obj.strftime('%Y-%m-%d')
        }
    
    def _scan_directory(self, url):
        """Scan a directory for VOD files"""
        vods = []
        soup = self._get_page_content(url)
        
        if not soup:
            return vods
        
        # Look for links to video files or subdirectories
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.flv', '.wmv'}
        
        for link in soup.find_all('a', href=True):
            # BeautifulSoup returns Tag objects, safely get href attribute  
            if isinstance(link, Tag):
                href_attr = link.get('href')
                if not href_attr:
                    continue
                href = str(href_attr)
            else:
                continue
            
            # Skip parent directory links
            if href in ['../', '../', '..']:
                continue
            
            full_url = urljoin(url, href)
            file_name = href.rstrip('/')
            
            # If it's a directory, recursively scan it
            if href.endswith('/'):
                print(f"📁 Scanning subdirectory: {href}")
                self.logger.debug(f"Scanning subdirectory: {full_url}")
                vods.extend(self._scan_directory(full_url))
            else:
                # Check if it's a video file
                file_ext = Path(file_name).suffix.lower()
                if file_ext in video_extensions:
                    if full_url not in self.downloaded_files:
                        vod_info = self._extract_vod_info(full_url, file_name)
                        vods.append(vod_info)
                        print(f"🆕 Found new VOD: {vod_info['title']}")
                        self.logger.debug(f"Found new VOD: {file_name}")
                    else:
                        self.logger.debug(f"Skipping already downloaded: {file_name}")
        
        return vods
    
    def scan_for_new_vods(self):
        """Scan the archive for new VOD files"""
        print(f"\n🔍 SCANNING FOR NEW VODs")
        print(f"📡 Checking: {self.config.vod_base_url}")
        print(f"💾 Already downloaded: {len(self.downloaded_files)} files")
        print(f"{'='*60}")
        
        new_vods = self._scan_directory(self.config.vod_base_url)
        
        if new_vods:
            print(f"\n🎉 SCAN COMPLETE!")
            print(f"📊 Found {len(new_vods)} new VODs to download")
            print(f"📋 New VODs found:")
            for i, vod in enumerate(new_vods[:5], 1):  # Show first 5
                print(f"   {i}. {vod['title']} ({vod.get('time', 'Unknown time')})")
            if len(new_vods) > 5:
                print(f"   ... and {len(new_vods) - 5} more")
        else:
            print(f"\n✅ SCAN COMPLETE!")
            print(f"📊 No new VODs found - all up to date!")
        
        print(f"{'='*60}")
        return new_vods
    
    def mark_as_downloaded(self, vod_url):
        """Mark a VOD as downloaded"""
        self.downloaded_files.add(vod_url)
        self._save_downloaded_files()
