# System Architecture Diagrams

This document contains the visual architecture diagrams for the IRS Retirement Topics Autonomous Agent system.

## 📦 Modules Layer

The core modules that provide the foundational functionality:

```mermaid
graph TB
    subgraph "Core Modules"
        CONFIG[config.py<br/>Configuration Management<br/>- URLs & Paths<br/>- Control Flags<br/>- LLM Settings]
        SCRAPER[scraper.py<br/>Web Scraping<br/>- discover_urls<br/>- download_html_files]
        PROCESSOR[processor.py<br/>Content Processing<br/>- process_all_files<br/>- HTML to Markdown]
        INDEXER[indexer.py<br/>ChromaDB Indexing<br/>- index_all_files<br/>- test_search]
        UTILS[utils.py<br/>Utility Functions<br/>- print_header<br/>- format_bytes]
    end
    
    CONFIG -.-> SCRAPER
    CONFIG -.-> PROCESSOR
    CONFIG -.-> INDEXER
    
    style CONFIG fill:#e1f5ff
    style SCRAPER fill:#fff4e1
    style PROCESSOR fill:#ffe1f5
    style INDEXER fill:#e1ffe1
    style UTILS fill:#f5f5f5
```

## 🤖 Agent Layer

The autonomous agent components that provide reasoning and decision-making:

```mermaid
graph TB
    subgraph "Agent System"
        AGENT_CORE[agent_core.py<br/>RetirementScraperAgent<br/>- LLM Brain<br/>- Decision Making<br/>- Tool Selection]
        AGENT_TOOLS[agent_tools.py<br/>9 Tool Functions<br/>- analyze_website<br/>- scrape_urls<br/>- check_content_quality<br/>- process_content<br/>- index_to_database<br/>- verify_indexing<br/>- search_knowledge_base<br/>- assess_progress<br/>- get_memory_summary]
        AGENT_MEMORY[agent_memory.py<br/>AgentMemory<br/>- Sessions History<br/>- Scraped URLs<br/>- Indexed Docs<br/>- Quality Metrics<br/>- Goal Progress]
    end
    
    AGENT_CORE --> AGENT_TOOLS
    AGENT_CORE --> AGENT_MEMORY
    AGENT_TOOLS --> AGENT_MEMORY
    
    style AGENT_CORE fill:#ff9999
    style AGENT_TOOLS fill:#ffcc99
    style AGENT_MEMORY fill:#99ccff
```

## 🔄 Complete System Orchestration

How the agent layer orchestrates the core modules to accomplish its goal:

```mermaid
graph TB
    subgraph "Entry Point"
        MAIN[main_agent.py<br/>Agent Entry Point]
    end
    
    subgraph "Agent Layer"
        AGENT[agent_core.py<br/>Autonomous Agent<br/>LLM Reasoning]
        TOOLS[agent_tools.py<br/>9 Tools]
        MEMORY[agent_memory.py<br/>Persistent Memory]
    end
    
    subgraph "Core Modules Layer"
        CONFIG[config.py<br/>Configuration]
        SCRAPER[scraper.py<br/>Web Scraping]
        PROCESSOR[processor.py<br/>HTML→Markdown]
        INDEXER[indexer.py<br/>ChromaDB]
        UTILS[utils.py<br/>Utilities]
    end
    
    subgraph "Storage"
        HTML[out/raw/<br/>HTML Files]
        MD[out/processed/<br/>Markdown Files]
        CHROMA[tmp/chroma/<br/>Vector DB]
        MEM_JSON[tmp/agent_memory.json<br/>Memory State]
    end
    
    MAIN --> AGENT
    AGENT --> TOOLS
    AGENT --> MEMORY
    
    TOOLS --> |uses| CONFIG
    TOOLS --> |analyze_website<br/>scrape_urls| SCRAPER
    TOOLS --> |process_content| PROCESSOR
    TOOLS --> |index_to_database<br/>search_knowledge_base| INDEXER
    TOOLS --> |formatting| UTILS
    
    SCRAPER --> HTML
    PROCESSOR --> |reads| HTML
    PROCESSOR --> |writes| MD
    INDEXER --> |reads| MD
    INDEXER --> |writes| CHROMA
    MEMORY --> |reads/writes| MEM_JSON
    
    style MAIN fill:#ff6b6b
    style AGENT fill:#ff9999
    style TOOLS fill:#ffcc99
    style MEMORY fill:#99ccff
    style CONFIG fill:#e1f5ff
    style SCRAPER fill:#fff4e1
    style PROCESSOR fill:#ffe1f5
    style INDEXER fill:#e1ffe1
    style UTILS fill:#f5f5f5
    style HTML fill:#d4edda
    style MD fill:#d4edda
    style CHROMA fill:#d4edda
    style MEM_JSON fill:#d4edda
```

## 📝 Component Descriptions

### Entry Point
- **main_agent.py**: Initializes the agent, loads memory, displays current state, and starts autonomous execution

### Agent Layer
- **agent_core.py**: The LLM-powered brain that reasons, plans, and makes decisions
- **agent_tools.py**: 9 capabilities the agent can choose to use based on its plan
- **agent_memory.py**: Persistent memory system that tracks all past actions and progress

### Core Modules Layer
- **config.py**: Centralized configuration (URLs, paths, flags, LLM settings)
- **scraper.py**: Web scraping functionality (URL discovery and HTML downloading)
- **processor.py**: AI-powered HTML to markdown conversion
- **indexer.py**: ChromaDB vector database operations (indexing and searching)
- **utils.py**: Common utility functions for display and formatting

### Storage Layer
- **out/raw/**: Downloaded HTML files with JSON metadata
- **out/processed/**: Clean markdown files extracted from HTML
- **tmp/chroma/**: ChromaDB vector database for semantic search
- **tmp/agent_memory.json**: Agent's persistent memory state

## 🔁 Data Flow

1. **main_agent.py** starts the agent
2. **Agent** (agent_core.py) loads its **Memory** (agent_memory.py)
3. **Agent** selects appropriate **Tools** (agent_tools.py) based on reasoning
4. **Tools** use **Core Modules** (scraper, processor, indexer) to perform work
5. **Core Modules** read/write to **Storage** (HTML, Markdown, ChromaDB)
6. **Agent** updates **Memory** with results and continues until goal achieved
