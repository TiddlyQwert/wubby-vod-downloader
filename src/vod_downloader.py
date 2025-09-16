"""
VOD Downloader module - Downloads and organizes VOD files
"""

import requests
import logging
import os
import shutil
import time
from pathlib import Path
from urllib.parse import urlparse
from tqdm import tqdm

class VODDownloader:
    """Downloads and organizes VOD files"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def _get_file_size(self, url):
        """Get the size of a file from URL"""
        try:
            response = requests.head(url, timeout=30)
            response.raise_for_status()
            return int(response.headers.get('content-length', 0))
        except Exception as e:
            self.logger.warning(f"Could not get file size for {url}: {e}")
            return 0
    
    def _generate_temp_file_path(self, vod_info):
        """Generate a temporary file path using original filename"""
        # Format the folder structure
        folder_path = self.config.folder_structure.format(**vod_info)
        
        # Sanitize folder path
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            folder_path = folder_path.replace(char, '_')
        
        # Create full path with original filename
        full_folder_path = self.config.download_path / folder_path
        temp_file_path = full_folder_path / vod_info['original_name']
        
        return temp_file_path
    
    def _generate_final_file_path(self, vod_info):
        """Generate the final clean file path"""
        # Format the folder structure
        folder_path = self.config.folder_structure.format(**vod_info)
        
        # Use the configured file name pattern, but handle missing time gracefully
        clean_vod_info = vod_info.copy()
        
        # If no time is available and the pattern includes {time}, modify the pattern
        if not clean_vod_info.get('time') and '{time}' in self.config.file_name_pattern:
            # Remove the time part from the pattern
            modified_pattern = self.config.file_name_pattern
            # Remove common time patterns like "{time} - " or " - {time}" or just "{time}"
            modified_pattern = modified_pattern.replace('{time} - ', '')
            modified_pattern = modified_pattern.replace(' - {time}', '')
            modified_pattern = modified_pattern.replace('{time}', '')
            # Clean up any double spaces or leading/trailing separators
            modified_pattern = modified_pattern.strip(' -')
            modified_pattern = ' '.join(modified_pattern.split())  # Normalize spaces
            file_name = modified_pattern.format(**clean_vod_info)
        else:
            # Use the original pattern (time is available or not in pattern)
            file_name = self.config.file_name_pattern.format(**clean_vod_info)
        
        # Get original extension
        original_ext = Path(vod_info['original_name']).suffix
        if not original_ext:
            original_ext = '.mp4'  # Default extension
        
        # Sanitize filename (remove invalid characters)
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            folder_path = folder_path.replace(char, '_')
            file_name = file_name.replace(char, '_')
        
        # Create full path
        full_folder_path = self.config.download_path / folder_path
        final_file_path = full_folder_path / (file_name + original_ext)
        
        return final_file_path
    
    def _generate_file_path(self, vod_info):
        """Generate the full file path for a VOD"""
        # For backwards compatibility, use the temp path initially
        return self._generate_temp_file_path(vod_info)
    
    def _download_and_rename_file(self, vod_info):
        """Download a single VOD file and rename it to clean format"""
        url = vod_info['url']
        temp_file_path = self._generate_temp_file_path(vod_info)
        final_file_path = self._generate_final_file_path(vod_info)
        
        try:
            # Check if final file already exists
            if final_file_path.exists():
                self.logger.info(f"Final file already exists, skipping: {final_file_path.name}")
                return True
            
            # Check file size if limit is set
            if self.config.max_file_size_bytes:
                self.logger.info(f"Checking file size for: {vod_info['title']}")
                file_size = self._get_file_size(url)
                if file_size > 0:
                    self.logger.info(f"File size: {file_size / 1024 / 1024:.1f} MB")
                if file_size > self.config.max_file_size_bytes:
                    self.logger.info(f"Skipping {vod_info['original_name']} - file too large ({file_size / 1024 / 1024:.1f} MB)")
                    return False
            
            # Create directory if it doesn't exist
            temp_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n{'='*60}")
            print(f"DOWNLOADING: {vod_info['title']}")
            print(f"Original filename: {vod_info['original_name']}")
            print(f"URL: {url}")
            print(f"Downloading to: {temp_file_path}")
            print(f"{'='*60}")
            
            # Download with progress bar
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            total_mb = total_size / 1024 / 1024 if total_size > 0 else 0
            
            if total_size > 0:
                print(f"File size: {total_mb:.1f} MB")
            
            with open(temp_file_path, 'wb') as f:
                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    desc=f"{vod_info['title'][:40]}",
                    disable=False,  # Always show progress for individual downloads
                    ncols=80  # Set width for better formatting
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print(f"\n✅ DOWNLOAD COMPLETE!")
            print(f"Downloaded: {temp_file_path.name}")
            
            # Rename to final clean filename
            if temp_file_path.exists():
                final_file_path.parent.mkdir(parents=True, exist_ok=True)
                print(f"📁 RENAMING FILE...")
                print(f"From: {temp_file_path.name}")
                print(f"To:   {final_file_path.name}")
                shutil.move(str(temp_file_path), str(final_file_path))
                print(f"✅ RENAME COMPLETE!")
                print(f"Final location: {final_file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading {vod_info['original_name']}: {e}")
            # Clean up partial downloads
            for path in [temp_file_path, final_file_path]:
                if path.exists():
                    try:
                        path.unlink()
                    except:
                        pass
            return False
    
    def download_vods(self, vods):
        """Download multiple VODs sequentially with rename after each download"""
        if not vods:
            self.logger.info("No VODs to download")
            return
        
        print(f"\n🎬 VOD DOWNLOADER STARTING")
        print(f"📊 Found {len(vods)} VODs to process")
        print(f"📁 Download location: {self.config.download_path}")
        print(f"{'='*80}")
        
        # Import scanner to mark files as downloaded
        from .vod_scanner import VODScanner
        scanner = VODScanner(self.config)
        
        downloaded_count = 0
        failed_count = 0
        skipped_count = 0
        
        # Process downloads one by one instead of concurrently
        for i, vod in enumerate(vods, 1):
            print(f"\n🎯 PROCESSING VOD {i}/{len(vods)}")
            print(f"Title: {vod['title']}")
            if vod.get('time'):
                print(f"Time: {vod['time']}")
            print(f"Date: {vod['date_str']}")
            
            # Check if we already processed this file
            final_file_path = self._generate_final_file_path(vod)
            if final_file_path.exists():
                print(f"⏭️  FILE ALREADY EXISTS - SKIPPING")
                print(f"Location: {final_file_path}")
                scanner.mark_as_downloaded(vod['url'])
                skipped_count += 1
                continue
            
            # Download and rename
            success = self._download_and_rename_file(vod)
            
            if success:
                downloaded_count += 1
                scanner.mark_as_downloaded(vod['url'])
                print(f"🎉 SUCCESS! VOD {i}/{len(vods)} completed")
            else:
                failed_count += 1
                print(f"❌ FAILED! VOD {i}/{len(vods)} failed to download")
                self.logger.error(f"Failed to process: {vod['original_name']}")
            
            # Show progress summary
            print(f"📈 Progress: {downloaded_count + skipped_count + failed_count}/{len(vods)} processed")
            print(f"   ✅ Downloaded: {downloaded_count} | ⏭️  Skipped: {skipped_count} | ❌ Failed: {failed_count}")
            
            # Small delay between downloads to be respectful to the server
            if i < len(vods):  # Don't sleep after the last download
                print(f"⏱️  Waiting 2 seconds before next download...")
                time.sleep(2)
        
        print(f"\n🏁 DOWNLOAD SESSION COMPLETE!")
        print(f"📊 Final Results:")
        print(f"   ✅ Successfully downloaded: {downloaded_count}")
        print(f"   ⏭️  Already existed (skipped): {skipped_count}")  
        print(f"   ❌ Failed: {failed_count}")
        print(f"   📁 Files saved to: {self.config.download_path}")
        print(f"{'='*80}")
        
        self.logger.info(f"Download complete - Downloaded: {downloaded_count}, Skipped: {skipped_count}, Failed: {failed_count}")
