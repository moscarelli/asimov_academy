# Module Documentation

## Overview

The IRS Retirement Glossary Scraper has been refactored into a modular architecture following Python best practices. The original monolithic script (`local_agent_web_scraper.py`) remains available for backward compatibility, while the new modular version provides better maintainability and reusability.

## Module Structure

### `src/config.py` - Configuration Management

**Purpose**: Centralized configuration using Python dataclasses.

**Key Components**:
- `ScraperConfig`: Dataclass containing all configuration settings
  - URLs and paths
  - Control flags (skip existing, process content, etc.)
  - Ollama LLM settings
  - ChromaDB settings
  - Rate limiting parameters

**Usage**:
```python
from src.config import ScraperConfig

config = ScraperConfig()
# Modify settings if needed
config.skip_existing_raw = False
config.process_content = True
```

### `src/scraper.py` - Web Scraping

**Purpose**: Handles URL discovery and HTML downloading.

**Key Components**:
- `WebScraper`: Class for web scraping operations
  - `discover_urls()`: Fetches and filters retirement topic URLs
  - `download_html_files()`: Downloads HTML content with metadata
  - `get_stats()`: Returns download statistics

**Usage**:
```python
from src.config import ScraperConfig
from src.scraper import WebScraper

config = ScraperConfig()
scraper = WebScraper(config)
urls = scraper.discover_urls()
scraper.download_html_files(urls)
```

### `src/processor.py` - Content Processing

**Purpose**: Converts HTML to clean markdown using AI.

**Key Components**:
- `ContentProcessor`: Class for HTML to markdown conversion
  - `process_all_files()`: Processes all HTML files to markdown
  - `wait_before_processing()`: Optional countdown timer
  - `get_stats()`: Returns processing statistics

**Usage**:
```python
from src.config import ScraperConfig
from src.processor import ContentProcessor

config = ScraperConfig()
processor = ContentProcessor(config)
processor.wait_before_processing()
processor.process_all_files()
```

### `src/indexer.py` - ChromaDB Indexing

**Purpose**: Creates searchable vector database from markdown files.

**Key Components**:
- `ChromaDBIndexer`: Class for database operations
  - `initialize()`: Sets up ChromaDB connection
  - `index_all_files()`: Indexes markdown files
  - `test_search()`: Tests semantic search
  - `get_stats()`: Returns indexing statistics

**Usage**:
```python
from src.config import ScraperConfig
from src.indexer import ChromaDBIndexer

config = ScraperConfig()
indexer = ChromaDBIndexer(config)
indexer.initialize()
indexer.index_all_files()
indexer.test_search("401k contribution limits")
```

### `src/utils.py` - Utility Functions

**Purpose**: Common helper functions.

**Key Components**:
- `print_header()`: Formatted header display
- `print_summary()`: Formatted statistics display
- `format_bytes()`: Human-readable byte formatting

**Usage**:
```python
from src.utils import print_header, format_bytes

print_header("My Section")
size = format_bytes(1048576)  # Returns "1.00 MB"
```

## Entry Points

### `main.py` - New Modular Entry Point (Recommended)

A clean orchestrator that uses all modular components. This is the recommended way to run the scraper.

**Advantages**:
- Clean, readable code
- Easy to modify and extend
- Better error handling
- Follows Python best practices

**Run**:
```powershell
cd retirement_glossary_scraper
uv run main.py
```

### `local_agent_web_scraper.py` - Legacy Monolithic Script

The original script kept for backward compatibility. Contains all logic in a single file.

**Use When**:
- You need the exact original behavior
- Quick one-off modifications
- Testing legacy functionality

**Run**:
```powershell
cd retirement_glossary_scraper
uv run local_agent_web_scraper.py
```

## Benefits of Modular Architecture

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Reusability**: Components can be imported and used in other projects
3. **Testability**: Individual modules can be tested independently
4. **Maintainability**: Easier to locate and fix bugs
5. **Extensibility**: New features can be added without modifying existing code
6. **Type Safety**: Better IDE support with type hints and dataclasses

## Migration Guide

If you want to customize the scraper:

1. **Change Configuration**: Edit `src/config.py` or create a custom config instance
2. **Extend Functionality**: Inherit from existing classes and override methods
3. **Add Features**: Create new modules in the `src/` directory
4. **Custom Entry Point**: Create your own main script using the components

Example custom script:
```python
from src.config import ScraperConfig
from src.scraper import WebScraper

# Custom configuration
config = ScraperConfig()
config.download_delay = 5  # Slower rate limiting

# Use only the scraper component
scraper = WebScraper(config)
urls = scraper.discover_urls()
scraper.download_html_files(urls)
```

## Best Practices

1. **Always use the config object**: Don't hardcode settings
2. **Import only what you need**: Use specific imports to keep memory usage low
3. **Handle exceptions**: Wrap operations in try-except blocks
4. **Check stats**: Use `get_stats()` methods to monitor progress
5. **Follow the pattern**: When adding features, follow the existing structure

## Future Enhancements

Potential improvements to the modular architecture:

- Add async/await for parallel downloads
- Implement retry logic with exponential backoff
- Add command-line argument parsing
- Create unit tests for each module
- Add logging framework (structlog or loguru)
- Implement progress bars (tqdm)
- Add configuration file support (YAML/TOML)
