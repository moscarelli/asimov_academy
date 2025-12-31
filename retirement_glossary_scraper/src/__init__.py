"""
IRS Retirement Glossary Scraper Package

A modular web scraper and knowledge base builder for IRS retirement topics.
Includes autonomous agents for building and querying the knowledge base.
"""

__version__ = "2.0.0"
__author__ = "Asimov Academy"

# Lazy imports to avoid loading all dependencies at package import time
__all__ = [
    "ScraperConfig",
    "WebScraper",
    "ContentProcessor",
    "ChromaDBIndexer",
    "RetirementScraperAgent",
    "RetirementQueryAgent",
]


def __getattr__(name):
    """Lazy import for package components."""
    if name == "ScraperConfig":
        from .config import ScraperConfig
        return ScraperConfig
    elif name == "WebScraper":
        from .scraper import WebScraper
        return WebScraper
    elif name == "ContentProcessor":
        from .processor import ContentProcessor
        return ContentProcessor
    elif name == "ChromaDBIndexer":
        from .indexer import ChromaDBIndexer
        return ChromaDBIndexer
    elif name == "RetirementScraperAgent":
        from .agent_core import RetirementScraperAgent
        return RetirementScraperAgent
    elif name == "RetirementQueryAgent":
        from .query_agent_core import RetirementQueryAgent
        return RetirementQueryAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
