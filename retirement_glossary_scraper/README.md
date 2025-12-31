# IRS Retirement Topics - Autonomous Agent

An autonomous AI agent that scrapes IRS retirement documentation, processes it to markdown, and builds a searchable knowledge base in ChromaDB. The agent makes its own decisions, adapts to results, and works toward its goal autonomously.

## 📁 Project Structure

```
retirement_glossary_scraper/
├── main_agent.py                   # 🤖 Autonomous agent entry point (builds KB)
├── query_agent.py                  # 🤖 Query agent for Q&A and tag extraction
├── query_retirement_glossary.py    # Query tool for searching the knowledge base
├── src/                            # Modular package components
│   ├── __init__.py                 # Package initialization
│   ├── config.py                   # Configuration management
│   ├── scraper.py                  # Web scraping logic
│   ├── processor.py                # HTML to markdown processing
│   ├── indexer.py                  # ChromaDB indexing
│   ├── utils.py                    # Utility functions
│   ├── agent_core.py               # 🤖 Autonomous agent with reasoning
│   ├── agent_tools.py              # 🤖 Agent's 9 capabilities/tools
│   ├── agent_memory.py             # 🤖 Persistent memory system
│   ├── query_agent_core.py         # 🤖 RAG agent for Q&A and tag extraction
│   └── query_agent_tools.py        # 🤖 Tools for querying knowledge base
├── out/
│   └── irs_retirement_topics/
│       ├── raw/                    # Downloaded HTML files + JSON metadata
│       ├── processed/              # AI-processed markdown files
│       └── discovered_urls.txt     # List of all scraped URLs
└── tmp/
    ├── chroma_retirement_glossary/ # ChromaDB vector database
    └── agent_memory.json           # 🤖 Agent's persistent memory
```

## 🧠 How the Agent Works

The agent uses an autonomous decision-making loop with memory and reasoning capabilities:

### Agent Architecture

```
┌─────────────────────────────────────────┐
│     Autonomous Agent (LLM Brain)        │
│  - Reasons about current state          │
│  - Plans next actions                   │
│  - Selects appropriate tools            │
│  - Learns from results                  │
└─────────────────┬───────────────────────┘
                  │
                  ├──> TOOLS (Agent's Capabilities)
                  │    ├── analyze_website()
                  │    ├── scrape_urls()
                  │    ├── check_content_quality()
                  │    ├── process_content()
                  │    ├── index_to_database()
                  │    ├── verify_indexing()
                  │    ├── search_knowledge_base()
                  │    ├── assess_progress()
                  │    └── get_memory_summary()
                  │
                  └──> MEMORY (Agent's Brain)
                       ├── Past sessions
                       ├── Scraped URLs
                       ├── Indexed documents
                       ├── Failed attempts
                       ├── Quality metrics
                       └── Goal progress
```

### Decision-Making Loop

```
1. CHECK MEMORY
   ↓
   "What have I already done?"
   "What failed before?"
   ↓
2. ASSESS PROGRESS
   ↓
   "How close am I to the goal?"
   "What's the current quality?"
   ↓
3. PLAN
   ↓
   "What should I do next?"
   "Which tool should I use?"
   ↓
4. EXECUTE
   ↓
   Use selected tool
   ↓
5. VALIDATE
   ↓
   "Did it work?"
   "What did I learn?"
   ↓
6. ADAPT
   ↓
   Adjust plan based on results
   ↓
7. REPEAT until goal achieved
```

> 📊 **Visual Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed Mermaid diagrams showing the system architecture, including modules layer, agent layer, and complete orchestration flow.

## 🛠️ Agent Tools

The agent has 9 tools to accomplish its goal:

### 1. analyze_website(url: str)
**Purpose**: Discover available content  
**Agent uses when**: Starting a new scraping session  
**Returns**: Page count, topics found, quality score, recommendation

### 2. scrape_urls(max_pages: int)
**Purpose**: Download HTML content  
**Agent uses when**: New content needs to be downloaded  
**Returns**: Download statistics (downloaded, skipped, errors)

### 3. check_content_quality(sample_size: int)
**Purpose**: Assess if content is worth processing  
**Agent uses when**: After downloading, before processing  
**Returns**: Quality score, relevance check, processing recommendation

### 4. process_content()
**Purpose**: Convert HTML to markdown  
**Agent uses when**: Quality check passes  
**Returns**: Processing statistics (processed, errors)

### 5. index_to_database()
**Purpose**: Make content searchable  
**Agent uses when**: Markdown files ready for indexing  
**Returns**: Indexing statistics (indexed, errors)

### 6. verify_indexing(query: str)
**Purpose**: Test search quality  
**Agent uses when**: After indexing, to validate  
**Returns**: Search results count, quality score

### 7. search_knowledge_base(query: str, limit: int)
**Purpose**: Explore indexed content  
**Agent uses when**: Investigating coverage or gaps  
**Returns**: Search results with previews

### 8. assess_progress()
**Purpose**: Check goal progress  
**Agent uses when**: Frequently, to decide next action  
**Returns**: Progress %, status, recommendation

### 9. get_memory_summary()
**Purpose**: Review past actions  
**Agent uses when**: Starting session, avoiding duplicates  
**Returns**: Session history, scraped URLs, indexed docs

## 💾 Memory System

The agent maintains persistent memory across sessions at `tmp/agent_memory.json`:

```json
{
  "sessions": [
    {
      "timestamp": "2025-12-30T10:15:00",
      "event_type": "scrape",
      "data": {"downloaded": 30, "errors": 2}
    }
  ],
  "scraped_urls": ["url1", "url2", ...],
  "indexed_documents": [
    {
      "filename": "001_retirement-plans.md",
      "title": "Retirement Plans Overview",
      "url": "https://..."
    }
  ],
  "failed_attempts": [],
  "knowledge_gaps": ["SIMPLE IRA", "SEP IRA"],
  "quality_metrics": {
    "content_quality": 0.85,
    "search_quality": 0.82
  },
  "goal_progress": {
    "documents_indexed": 78,
    "progress_percentage": 78.0,
    "status": "in_progress",
    "recommendation": "Continue scraping"
  }
}
```

## 🚀 Usage

### Run the Agent

**Important**: Always run from inside the `retirement_glossary_scraper/` directory.

```powershell
cd retirement_glossary_scraper
uv run main_agent.py
```

The agent will:
1. ✅ Check its memory for past work
2. ✅ Assess current progress
3. ✅ Plan its approach
4. ✅ Execute autonomously
5. ✅ Adapt based on results
6. ✅ Stop when goal achieved

### Resuming a Session

The agent automatically resumes from where it left off:

```powershell
# First run - scrapes 50 docs
uv run main_agent.py

# Interrupt (Ctrl+C)

# Second run - remembers 50 docs, continues from there
uv run main_agent.py
```

### Query Agent - Q&A and Tag Extraction

The query agent provides two modes:

#### 1. Q&A Mode (Interactive)

Ask questions about retirement topics:

```powershell
cd retirement_glossary_scraper
uv run query_agent.py
```

Then ask questions interactively:
```
Question: What are 401k contribution limits?
Question: When do I need to take required minimum distributions?
Question: quit
```

#### 2. Q&A Mode (Single Question)

Get a single answer:

```powershell
uv run query_agent.py --question "What are Roth IRA contribution limits?"
```

#### 3. Tag Extraction Mode

Extract retirement terms from text (for API integration):

```powershell
uv run query_agent.py --mode tags --text "I want to maximize my retirement savings with a 401k and Roth IRA"
```

Returns structured tags:
```
Extracted Tags:
1. Term: 401(k) Plans
   - Relevance: high
   - Filename: 401k-plans.md
   - URL: https://www.irs.gov/...
   
2. Term: Roth IRA
   - Relevance: high
   - Filename: roth-ira.md
   - URL: https://www.irs.gov/...
```

**Tag Extraction Options:**
- `--max-tags N`: Maximum tags to extract (default: 10)
- Output includes document references for linking

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

The query tool provides:
- Pre-defined queries (401k limits, RMDs, early withdrawals)
- Interactive mode for custom queries
- Full metadata and matched content display
- Semantic search using ChromaDB embeddings

## 📦 Modular Architecture

The agent uses a clean, modular architecture with clear separation of concerns:

### Core Modules (used by agent tools)

#### `src/config.py` - Configuration Management
**Purpose**: Centralized configuration using Python dataclasses  
**Key Component**: `ScraperConfig` with all settings (URLs, paths, flags, LLM settings)  
**Agent uses**: Configuration for all operations (rate limiting, paths, etc.)

#### `src/scraper.py` - Web Scraping
**Purpose**: Handles URL discovery and HTML downloading  
**Key Component**: `WebScraper` class with `discover_urls()` and `download_html_files()`  
**Agent uses**: Called by `scrape_urls()` tool

#### `src/processor.py` - Content Processing
**Purpose**: Converts HTML to clean markdown using AI  
**Key Component**: `ContentProcessor` class with `process_all_files()`  
**Agent uses**: Called by `process_content()` tool

#### `src/indexer.py` - ChromaDB Indexing
**Purpose**: Creates searchable vector database from markdown  
**Key Component**: `ChromaDBIndexer` class with `index_all_files()` and `test_search()`  
**Agent uses**: Called by `index_to_database()` and `search_knowledge_base()` tools

#### `src/utils.py` - Utility Functions
**Purpose**: Common helper functions for display  
**Functions**: `print_header()`, `print_summary()`, `format_bytes()`  
**Agent uses**: For formatted output and reporting

### Agent Modules

#### `src/agent_core.py` - Autonomous Agent Brain
**Purpose**: LLM-powered reasoning and planning  
**Key Component**: `RetirementScraperAgent(Agent)` with instructions and autonomous loop  
**Capabilities**: Makes decisions, selects tools, learns from results, adapts strategy

#### `src/agent_tools.py` - Agent Capabilities
**Purpose**: 9 @tool decorated functions the agent can call  
**Key Feature**: Each tool wraps core modules (scraper, processor, indexer) with agent-friendly interface  
**Design**: Singleton pattern for config and memory access

#### `src/agent_memory.py` - Persistent Memory
**Purpose**: Remembers past work across sessions  
**Key Component**: `AgentMemory` class with JSON storage  
**Tracks**: Sessions, scraped URLs, indexed docs, failed attempts, quality metrics, progress

### Query Agent Modules

#### `src/query_agent_core.py` - RAG Agent Brain
**Purpose**: LLM-powered Q&A and tag extraction  
**Key Component**: `RetirementQueryAgent(Agent)` with two modes (qa/tags)  
**Capabilities**: Answer questions using RAG, extract relevant terms from text

#### `src/query_agent_tools.py` - Query Capabilities
**Purpose**: 5 @tool decorated functions for querying and analysis  
**Tools**:
- `search_glossary()` - Semantic search for Q&A
- `extract_tags_from_text()` - Extract retirement terms from text
- `get_document_references()` - Get full metadata for terms
- `analyze_text_for_concepts()` - Identify retirement concepts in text

**Use Cases**:
- **Q&A**: User asks "What are 401k limits?" → Agent searches and synthesizes answer
- **Tag Extraction**: API sends text → Agent extracts matching terms with document references for linking

## 🔧 Agent Configuration

Configuration in `src/config.py`:

```python
class ScraperConfig:
    # URLs and paths
    base_url = "https://www.irs.gov/retirement-plans/..."
    
    # Control flags (agent respects these)
    skip_existing_raw = True      # Skip downloaded HTML files
    process_content = True         # Enable markdown processing
    index_to_chromadb = True      # Enable indexing
    
    # Rate limiting
    download_delay = 2            # Seconds between downloads
    indexing_delay = 0.5          # Seconds between indexing
    
    # Ollama LLM settings
    ollama_host = "http://localhost:11434"
    ollama_model = "llama3.2:latest"
    ollama_timeout = 60
    embedding_dimensions = 3072
```

## 📋 Dependencies

- **Agno Framework**: Agent, Ollama, ChromaDB, Knowledge, TextReader
- **BeautifulSoup4**: HTML parsing
- **Requests**: HTTP client
- **Ollama**: Local LLM (llama3.2:latest) for reasoning, processing, and embeddings
  - Host: http://localhost:11434
  - Embedding dimensions: 3072
  - Timeout: 60 seconds

## 📝 Data Files

### Raw HTML Files (`out/irs_retirement_topics/raw/`)
- Numbered format: `001_retirement-plans.html`
- JSON metadata: download time, source URL, file size, status code
- Agent tracks these to avoid re-downloading

### Processed Markdown (`out/irs_retirement_topics/processed/`)
- YAML frontmatter with metadata
- Clean, structured content extracted by AI
- Document titles extracted
- Agent checks these before processing

### ChromaDB (`tmp/chroma_retirement_glossary/`)
- Collection: `irs_retirement_glossary`
- SQLite-based persistent storage
- Full-text and semantic search enabled
- 3072-dimensional embeddings from Ollama

### Agent Memory (`tmp/agent_memory.json`)
- JSON format for human readability
- Tracks all agent sessions and actions
- Persistent across restarts
- Can be manually inspected or cleared

## 🎯 Example Agent Session

Here's how the agent works autonomously:

```
🤖 Agent: "Starting new session. Let me check my memory first."
→ Calls: get_memory_summary()
→ Result: "50 documents already indexed, 40 URLs scraped"

🤖 Agent: "Good! I've made progress. Let me assess current state."
→ Calls: assess_progress()
→ Result: "50% complete, quality score 0.75, need 50 more docs"

🤖 Agent: "I need to scrape more content. Let me analyze what's available."
→ Calls: analyze_website("irs.gov/retirement")
→ Result: "107 URLs found, 40 already scraped, 67 new"

🤖 Agent: "Perfect! Let me scrape 30 new URLs to get closer to goal."
→ Calls: scrape_urls(max_pages=30)
→ Result: "Downloaded 28, 2 errors"

🤖 Agent: "Good progress. Let me check quality before processing."
→ Calls: check_content_quality(sample_size=5)
→ Result: "Quality score 0.85, content is relevant, should process"

🤖 Agent: "Quality looks good! Processing all new content to markdown."
→ Calls: process_content()
→ Result: "28 files processed successfully"

🤖 Agent: "Now indexing to make content searchable."
→ Calls: index_to_database()
→ Result: "28 documents indexed, 0 errors"

🤖 Agent: "Let me verify the indexing quality."
→ Calls: verify_indexing(query="401k limits")
→ Result: "Found 5 results, quality score 0.9"

🤖 Agent: "Great! Let me check overall progress."
→ Calls: assess_progress()
→ Result: "78% complete (78/100 docs), quality 0.82, status: in_progress"

🤖 Agent: "Almost there! Scraping remaining URLs..."
→ Continues autonomously...

🤖 Agent: "Goal achieved! 105 documents indexed, quality 0.85. Task complete."
```

## 🌟 Agent Advantages

**Intelligent**: Makes decisions based on context, not fixed sequences  
**Efficient**: Avoids duplicate work via persistent memory  
**Adaptive**: Changes approach if something fails  
**Goal-oriented**: Knows when it's done  
**Self-validating**: Checks quality at each step  
**Resumable**: Can continue from interruption seamlessly  
**Autonomous**: Requires no human intervention during execution

## 🔍 Example Queries

Once the knowledge base is built, you can search for:
- "401k contribution limits"
- "Required minimum distributions"
- "Roth IRA conversion rules"
- "Early withdrawal penalties"
- "SIMPLE IRA employer match"
- "Catch-up contributions for over 50"

## 🏗️ Technical Architecture

**Agent LLM**: Ollama llama3.2:latest for reasoning and tool selection  
**Content Processing**: Same LLM for HTML to markdown conversion  
**Embeddings**: 3072-dimensional vectors for semantic search  
**Vector Database**: ChromaDB with SQLite backend  
**Rate Limiting**: 2s between downloads, 0.5s between indexing  
**Memory Storage**: JSON-based for human inspection  
**Tools Framework**: Agno @tool decorators with type safety

## 📌 Notes

- Link order preserved from original IRS page (alphabetical)
- Skips non-English language variants
- Handles 404 errors gracefully
- All operations logged with LOG: prefix
- Unicode characters replaced with ASCII for PowerShell compatibility
- Agent automatically skips already processed content
- Memory survives interruptions and restarts
