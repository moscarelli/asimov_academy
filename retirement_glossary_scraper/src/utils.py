"""
Utility functions for the IRS Retirement Glossary Scraper.
"""
from typing import Dict, Any


def print_header(title: str, width: int = 60):
    """
    Print a formatted header.
    
    Args:
        title: Header title
        width: Width of the header line
    """
    print("=" * width)
    print(title)
    print("=" * width)


def print_summary(title: str, stats: Dict[str, Any], width: int = 60):
    """
    Print a formatted summary section.
    
    Args:
        title: Section title
        stats: Dictionary of statistics to display
        width: Width of the header line
    """
    print(f"\n{title}:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable format.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"
