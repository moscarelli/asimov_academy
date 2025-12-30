#!/usr/bin/env python3
"""
IRS Retirement Glossary Scraper - Main Entry Point

A modular web scraper that:
1. Discovers IRS retirement topic URLs
2. Downloads raw HTML content
3. Processes HTML to clean markdown (optional)
4. Indexes content to ChromaDB for semantic search (optional)
"""

from src.config import ScraperConfig
from src.scraper import WebScraper
from src.processor import ContentProcessor
from src.indexer import ChromaDBIndexer
from src.utils import print_header, print_summary


def main():
    """Main execution function."""
    
    # Initialize configuration
    config = ScraperConfig()
    
    # Print header
    print_header("IRS Retirement Topics Scraper")
    print(f"Main URL: {config.main_url}")
    print(f"Raw HTML dir: {config.raw_dir}")
    print(f"Processed dir: {config.processed_dir}")
    print(f"Skip existing raw: {config.skip_existing_raw}")
    print(f"Process content: {config.process_content}")
    print(f"Wait before processing: {config.wait_before_processing}s")
    print(f"Index to ChromaDB: {config.index_to_chromadb}")
    print("=" * 60)
    
    # Step 1: Discover URLs
    scraper = WebScraper(config)
    urls = scraper.discover_urls()
    
    # Step 2: Download HTML files
    download_stats = scraper.download_html_files(urls)
    
    # Step 3 & 4: Process content (optional)
    process_stats = None
    if config.process_content:
        processor = ContentProcessor(config)
        processor.wait_before_processing()
        process_stats = processor.process_all_files()
    
    # Step 5: Index to ChromaDB (optional)
    index_stats = None
    if config.index_to_chromadb:
        indexer = ChromaDBIndexer(config)
        indexer.initialize()
        index_stats = indexer.index_all_files()
        
        # Test the indexing
        indexer.test_search()
    
    # Print summary
    print_header("SCRAPING COMPLETE!")
    print(f"Total URLs found: {len(urls)}")
    
    print_summary("Download Phase", {
        "Downloaded": download_stats[0],
        "Skipped (existing)": download_stats[1],
        "Errors": download_stats[2]
    })
    
    if process_stats:
        print_summary("Processing Phase", {
            "Processed to markdown": process_stats[0],
            "Processing errors": process_stats[1]
        })
    
    if index_stats:
        print_summary("ChromaDB Indexing", {
            "Indexed": index_stats[0],
            "Errors": index_stats[1],
            "Collection": config.chroma_collection
        })
    
    print("\nOutput directories:")
    print(f"  Raw HTML: {config.raw_dir.absolute()}")
    print(f"  Processed: {config.processed_dir.absolute()}")
    if config.index_to_chromadb:
        print(f"  ChromaDB: {config.chroma_path}")
    
    print("\nConfiguration used:")
    print(f"  SKIP_EXISTING_RAW: {config.skip_existing_raw}")
    print(f"  PROCESS_CONTENT: {config.process_content}")
    if config.process_content:
        print(f"  WAIT_BEFORE_PROCESSING: {config.wait_before_processing}s")
    print(f"  INDEX_TO_CHROMADB: {config.index_to_chromadb}")
    print("=" * 60)


if __name__ == "__main__":
    main()
