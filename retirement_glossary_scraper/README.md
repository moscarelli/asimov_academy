# IRS Retirement Topics Glossary - Web Scraper & Knowledge Base

This project scrapes IRS retirement topics, processes them into markdown, and indexes them into a ChromaDB vector database for semantic search.

**New**: The project has been refactored into a modular architecture! See [MODULES.md](MODULES.md) for detailed documentation.

## 📁 Project Structure

```
retirement_glossary_scraper/
├── main.py                         # New modular main entry point
├── local_agent_web_scraper.py      # Original monolithic script (legacy)
├── query_retirement_glossary.py    # Query tool for searching the knowledge base
├── src/                            # Modular package components
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration management
│   ├── scraper.py                  # Web scraping logic
│   ├── processor.py                # HTML to markdown processing
│   ├── indexer.py                  # ChromaDB indexing
│   └── utils.py                    # Utility functions
├── out/
│   └── irs_retirement_topics/
│       ├── raw/                    # Downloaded HTML files + JSON metadata
│       ├── processed/              # AI-processed markdown files
│       └── discovered_urls.txt     # List of all scraped URLs
└── tmp/
    └── chroma_retirement_glossary/ # ChromaDB vector database
```

## 🚀 Features

### Modular Architecture

The scraper is now organized into clean, reusable components:

- **config.py**: Centralized configuration with dataclass
- **scraper.py**: Web scraping and HTML downloading
- **processor.py**: AI-powered HTML to markdown conversion
- **indexer.py**: ChromaDB vector database indexing
- **utils.py**: Common utility functions

### Web Scraper (`main.py` or `local_agent_web_scraper.py`)

- **Step 1**: Discovers all retirement topic URLs from IRS website
- **Step 2**: Downloads raw HTML content with metadata
- **Step 3**: Optional 20-second countdown before processing
- **Step 4**: Processes HTML to clean markdown using AI agent
- **Step 5**: Indexes markdown files to ChromaDB for semantic search

**Configuration (in `src/config.py`):**
```python
SKIP_EXISTING_RAW = True      # Skip already downloaded files
PROCESS_CONTENT = False        # Enable HTML→Markdown processing
WAIT_BEFORE_PROCESSING = 20   # Countdown timer (seconds)
INDEX_TO_CHROMADB = True      # Enable ChromaDB indexing
```

### Query Tool (`query_retirement_glossary.py`)

Semantic search interface for the knowledge base:
- Pre-defined queries (401k limits, RMDs, early withdrawals)
- Interactive mode for custom queries
- Displays full metadata and matched content

## 📊 Current Status
 (Modular Version - Recommended)
```powershell
cd retirement_glossary_scraper
uv run main.py
```

### Run the Scraper (Legacy Monolithic Version)
- **Total URLs**: 107 discovered
- **Downloaded**: 106 HTML files (1 returned 404)
- **Processed**: 106 markdown files
- **Indexed**: 106 documents in ChromaDB

## 🛠️ Usage

**Important**: Always run scripts from inside the `retirement_glossary_scraper/` directory.

### Run the Scraper
```powershell
cd retirement_glossary_scraper
uv run local_agent_web_scraper.py
```

### Query the Knowledge Base
```powershell
cd retirement_glossary_scraper
uv run query_retirement_glossary.py
```

Interactive mode allows you to search for any retirement-related topic:
```
Query: What are Roth IRA contribution limits?
Query: Required minimum distribution age
Query: quit  # Exit
```

## 📋 Dependencies

- **Agno Framework**: Agent, Ollama, ChromaDB, Knowledge, TextReader
- **BeautifulSoup4**: HTML parsing
- **Requests**: HTTP client
- **Ollama**: Local LLM (llama3.2:latest) for processing and embeddings
  - Host: http://localhost:11434
  - Embedding dimensions: 3072

## 📝 Data Files

### Raw HTML Files (`out/irs_retirement_topics/raw/`)
- Numbered format: `001_retirement-plans.html`
- JSON metadata: download time, source URL, file size, status code

### Processed Markdown (`out/irs_retirement_topics/processed/`)
- YAML frontmatter with metadata
- Clean, structured content
- Document titles extracted

### ChromaDB (`tmp/chroma_retirement_glossary/`)
- Collection: `irs_retirement_glossary`
- SQLite-based persistent storage
- Full-text and semantic search enabled

## � Documentation

- **[MODULES.md](MODULES.md)**: Detailed documentation of the modular architecture
  - Individual module descriptions
  - Usage examples for each component
  - Migration guide from monolithic to modular
  - Best practices and future enhancements

## �🔍 Example Queries

- "401k contribution limits"
- "Required minimum distributions"
- Architecture**: Modular Python package with clear separation of concerns
- **Configuration**: Dataclass-based settings in `config.py`
- **Scraping**: Request-based HTML downloader with rate limiting
- **Processing**: AI agent for content extraction and normalization
- **Indexing**: ChromaDB with Ollama embeddings for semantic search
- **Utilities**: Helper functions for formatting and display

**LLM Model**: Ollama llama3.2:latest
- Content processing: Converts HTML to clean markdown
- Embeddings: 3072-dimensional vectors for semantic search
- Timeout: 60 seconds

**Storage**:
- Raw HTML preserved for reprocessing
- Markdown for readability and ChromaDB indexing
- JSON metadata for tracking and lineage

**Rate Limiting**: 
- 2-second delay between downloads to respect IRS servers
- 0.5-second delay between indexing operation
**Storage**:
- Raw HTML preserved for reprocessing
- Markdown for readability and ChromaDB indexing
- JSON metadata for tracking and lineage

**Rate Limiting**: 2-second delay between downloads to respect IRS servers

## 📌 Notes

- Link order preserved from original IRS page (alphabetical)
- Skips non-English language variants
- Handles 404 errors gracefully
- All operations logged with LOG: prefix
- Unicode characters replaced with ASCII for PowerShell compatibility
