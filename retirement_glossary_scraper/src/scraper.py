"""
Web scraping module for downloading IRS retirement topics.
"""
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urljoin
import time
import re
import json
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup

from .config import ScraperConfig


class WebScraper:
    """Handles web scraping and HTML downloading."""
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize the web scraper.
        
        Args:
            config: Configuration object with scraper settings
        """
        self.config = config
        self.download_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def discover_urls(self) -> List[str]:
        """
        Discover all retirement topic URLs from the main IRS page.
        
        Returns:
            List of discovered URLs
        """
        print(f"\n[STEP 1] Fetching topic links from main page...")
        print(f"LOG: Requesting URL: {self.config.main_url}")
        
        try:
            # Download the page
            print(f"LOG: Sending HTTP GET request...")
            response = requests.get(self.config.main_url, timeout=30)
            response.raise_for_status()
            print(f"LOG: ✓ Downloaded page successfully ({len(response.content)} bytes)")
            
            # Parse HTML
            print(f"LOG: Parsing HTML with BeautifulSoup...")
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"LOG: ✓ HTML parsed successfully")
            
            # Find all links
            all_links = soup.find_all('a', href=True)
            print(f"LOG: ✓ Found {len(all_links)} total links on page")
            
            # Filter for retirement topic links
            urls = self._filter_retirement_links(all_links)
            
            print(f"\nLOG: ✓ Found {len(urls)} unique retirement topic URLs (in page order)")
            
            # Save URLs to file
            self._save_urls(urls)
            
            return urls
            
        except Exception as e:
            print(f"✗ Error fetching links: {e}")
            raise
    
    def _filter_retirement_links(self, links: List) -> List[str]:
        """
        Filter links to keep only relevant IRS retirement topics.
        
        Args:
            links: List of BeautifulSoup link elements
            
        Returns:
            List of filtered URLs
        """
        print(f"LOG: Filtering retirement topic links (preserving page order)...")
        urls = []
        seen = set()
        
        for idx, link in enumerate(links, 1):
            href = link['href']
            
            # Make absolute URL
            if href.startswith('/'):
                href = urljoin(self.config.main_url, href)
            
            # Only keep IRS retirement-related links
            if href.startswith('http') and 'irs.gov' in href and 'retirement' in href.lower():
                # Skip language variants and the main index page
                if (href != self.config.main_url and 
                    '/es/' not in href and '/ko/' not in href and 
                    '/zh-hans/' not in href and '/zh-hant/' not in href and 
                    '/ru/' not in href and '/vi/' not in href and '/ht/' not in href):
                    
                    # Remove URL fragments (anchors)
                    if '#' in href:
                        href = href.split('#')[0]
                    
                    # Add only if not seen before
                    if href not in seen:
                        urls.append(href)
                        seen.add(href)
                        print(f"LOG:   [{len(urls)}] Found: {href}")
        
        return urls
    
    def _save_urls(self, urls: List[str]):
        """
        Save discovered URLs to a file.
        
        Args:
            urls: List of URLs to save
        """
        print(f"\nLOG: Saving discovered URLs...")
        numbered_urls = [f"{idx}. {url}" for idx, url in enumerate(urls, 1)]
        self.config.urls_file.write_text('\n'.join(numbered_urls), encoding='utf-8')
        print(f"LOG: ✓ Saved {len(urls)} numbered URLs to: {self.config.urls_file}")
    
    def download_html_files(self, urls: List[str]) -> Tuple[int, int, int]:
        """
        Download HTML files for all URLs.
        
        Args:
            urls: List of URLs to download
            
        Returns:
            Tuple of (download_count, skipped_count, error_count)
        """
        print(f"\n[STEP 2] Downloading raw HTML content...")
        print(f"LOG: Skip existing raw files: {self.config.skip_existing_raw}")
        print(f"LOG: Total pages to process: {len(urls)}")
        
        self.download_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
        for idx, url in enumerate(urls, 1):
            try:
                self._download_single_file(idx, url, len(urls))
            except Exception as e:
                print(f"LOG: [{idx}/{len(urls)}] ✗ ERROR: {str(e)}")
                self.error_count += 1
        
        print(f"\nLOG: Download phase complete!")
        print(f"LOG:   Downloaded: {self.download_count}")
        print(f"LOG:   Skipped: {self.skipped_count}")
        print(f"LOG:   Errors: {self.error_count}")
        
        return self.download_count, self.skipped_count, self.error_count
    
    def _download_single_file(self, idx: int, url: str, total: int):
        """
        Download a single HTML file.
        
        Args:
            idx: Current index (1-based)
            url: URL to download
            total: Total number of URLs
        """
        print(f"\nLOG: [{idx}/{total}] Processing URL: {url}")
        
        # Generate filename from URL
        path_parts = urlparse(url).path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else 'index'
        filename = re.sub(r'[^\w\-]', '_', filename)
        
        # Use numbered filename to maintain order
        numbered_filename = f"{str(idx).zfill(3)}_{filename}"
        
        html_file = self.config.raw_dir / f"{numbered_filename}.html"
        meta_file = self.config.raw_dir / f"{numbered_filename}.json"
        
        # Skip if exists
        if self.config.skip_existing_raw and html_file.exists():
            print(f"LOG: [{idx}/{total}] ⊘ Skipped (already exists): {html_file.name}")
            self.skipped_count += 1
            return
        
        print(f"LOG: [{idx}/{total}] Downloading HTML from: {url}")
        
        # Download raw HTML
        print(f"LOG:   Sending HTTP GET request...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"LOG:   ✓ Received response ({len(response.content)} bytes)")
        
        # Save raw HTML
        print(f"LOG:   Saving HTML to: {html_file.name}")
        html_file.write_text(response.text, encoding='utf-8')
        
        # Save metadata
        metadata = {
            'number': idx,
            'url': url,
            'downloaded_at': datetime.now().isoformat(),
            'filename': numbered_filename,
            'html_size_bytes': len(response.content),
            'status_code': response.status_code
        }
        meta_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        print(f"LOG:   ✓ Saved metadata to: {meta_file.name}")
        
        print(f"LOG: [{idx}/{total}] ✓ SUCCESS: {html_file.name} ({len(response.content)} bytes)")
        self.download_count += 1
        
        # Rate limiting
        print(f"LOG:   Waiting {self.config.download_delay} seconds (rate limiting)...")
        time.sleep(self.config.download_delay)
    
    def get_stats(self) -> dict:
        """
        Get download statistics.
        
        Returns:
            Dictionary with download statistics
        """
        return {
            'downloaded': self.download_count,
            'skipped': self.skipped_count,
            'errors': self.error_count
        }
