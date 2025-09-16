#!/usr/bin/env python3
"""
VOD Downloader - Automatically download and organize VODs from archive.wubby.tv
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

from src.vod_scanner import VODScanner
from src.vod_downloader import VODDownloader
from src.config import Config

def setup_logging(debug=False):
    """Setup logging configuration"""
    level = logging.DEBUG if debug else logging.INFO
    format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=[
            logging.FileHandler('vod_downloader.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Initialize configuration
    config = Config()
    
    # Setup logging
    setup_logging(config.debug)
    logger = logging.getLogger(__name__)
    
    print(f"\n🎬 WUBBY VOD DOWNLOADER")
    print(f"📁 Download path: {config.download_path}")
    print(f"⏰ Scheduled check time: {config.check_time}")
    print(f"🌐 VOD source: {config.vod_base_url}")
    print(f"{'='*60}")
    
    logger.info("VOD Downloader starting up...")
    logger.info(f"Download path: {config.download_path}")
    logger.info(f"Scheduled check time: {config.check_time}")
    
    # Initialize components
    scanner = VODScanner(config)
    downloader = VODDownloader(config)
    
    def check_and_download():
        """Check for new VODs and download them"""
        try:
            print(f"\n🚀 STARTING VOD CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("Starting VOD check...")
            new_vods = scanner.scan_for_new_vods()
            
            if new_vods:
                downloader.download_vods(new_vods)
            else:
                print(f"😴 No new VODs to download. Check again later!")
                
        except Exception as e:
            print(f"❌ ERROR during VOD check: {e}")
            logger.error(f"Error during VOD check: {e}")
    
    # Schedule the check
    schedule.every().day.at(config.check_time).do(check_and_download)
    
    print(f"⏰ Scheduled to check daily at {config.check_time}")
    print(f"🔄 Press Ctrl+C to stop")
    
    # Run initial check
    if len(sys.argv) > 1 and sys.argv[1] == "--check-now":
        print(f"🎯 Running immediate check...")
        logger.info("Running initial check...")
        check_and_download()
    
    # Keep the script running
    try:
        print(f"\n⏳ Waiting for scheduled check time...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print(f"\n👋 VOD Downloader stopped by user")
        logger.info("VOD Downloader stopped")

if __name__ == "__main__":
    main()
