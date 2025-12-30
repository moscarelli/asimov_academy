# Autonomous Agent Documentation

## Overview

This project now includes a **true autonomous agent** that can build the retirement knowledge base by making its own decisions, rather than following a fixed pipeline.

## Agent vs Pipeline Comparison

| Feature | Autonomous Agent | Pipeline (main.py) | Legacy Script |
|---------|-----------------|-------------------|---------------|
| **Decision Making** | ✅ Plans its own steps | ❌ Fixed sequence | ❌ Fixed sequence |
| **Adaptation** | ✅ Adjusts based on results | ❌ No adaptation | ❌ No adaptation |
| **Memory** | ✅ Remembers past work | ❌ No memory | ❌ No memory |
| **Goal Awareness** | ✅ Knows when done | ❌ Runs all steps | ❌ Runs all steps |
| **Quality Checks** | ✅ Validates each step | ❌ No validation | ❌ No validation |
| **Error Recovery** | ✅ Adapts to failures | ❌ Continues blindly | ❌ Continues blindly |
| **Efficiency** | ✅ Avoids duplicate work | ⚠️ Can re-process | ⚠️ Can re-process |

## How the Agent Works

### 1. Agent Architecture

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

### 2. Agent's Decision-Making Loop

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

### 3. Example Agent Session

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

## Agent Tools Reference

### 1. `analyze_website(url: str)`
**Purpose**: Discover available content
**Agent uses when**: Starting a new scraping session
**Returns**: Page count, topics found, quality score, recommendation

### 2. `scrape_urls(max_pages: int)`
**Purpose**: Download HTML content
**Agent uses when**: New content needs to be downloaded
**Returns**: Download statistics (downloaded, skipped, errors)

### 3. `check_content_quality(sample_size: int)`
**Purpose**: Assess if content is worth processing
**Agent uses when**: After downloading, before processing
**Returns**: Quality score, relevance check, processing recommendation

### 4. `process_content()`
**Purpose**: Convert HTML to markdown
**Agent uses when**: Quality check passes
**Returns**: Processing statistics (processed, errors)

### 5. `index_to_database()`
**Purpose**: Make content searchable
**Agent uses when**: Markdown files ready for indexing
**Returns**: Indexing statistics (indexed, errors)

### 6. `verify_indexing(query: str)`
**Purpose**: Test search quality
**Agent uses when**: After indexing, to validate
**Returns**: Search results count, quality score

### 7. `search_knowledge_base(query: str, limit: int)`
**Purpose**: Explore indexed content
**Agent uses when**: Investigating coverage or gaps
**Returns**: Search results with previews

### 8. `assess_progress()`
**Purpose**: Check goal progress
**Agent uses when**: Frequently, to decide next action
**Returns**: Progress %, status, recommendation

### 9. `get_memory_summary()`
**Purpose**: Review past actions
**Agent uses when**: Starting session, avoiding duplicates
**Returns**: Session history, scraped URLs, indexed docs

## Agent Memory System

The agent maintains persistent memory across sessions:

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

## Running the Agent

### Basic Usage
```bash
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
```bash
# First run - scrapes 50 docs
uv run main_agent.py

# Interrupt (Ctrl+C)

# Second run - remembers 50 docs, continues from there
uv run main_agent.py
```

### Clearing Memory

To start fresh:
```python
from src.agent_memory import AgentMemory

memory = AgentMemory()
memory.clear_memory()
```

## Agent Configuration

The agent uses the same config as the pipeline:

```python
# src/config.py
class ScraperConfig:
    skip_existing_raw = True      # Agent respects this
    process_content = False        # Agent decides when to process
    index_to_chromadb = True      # Agent decides when to index
    download_delay = 2            # Rate limiting
    # ...
```

## Advantages of Agent vs Pipeline

### Agent Advantages:
1. **Intelligent** - Makes decisions based on context
2. **Efficient** - Avoids duplicate work via memory
3. **Adaptive** - Changes approach if something fails
4. **Goal-oriented** - Knows when it's done
5. **Self-validating** - Checks quality at each step
6. **Resumable** - Can continue from interruption

### Pipeline Advantages:
1. **Predictable** - Always does the same thing
2. **Simple** - Easy to understand
3. **Fast** - No decision overhead
4. **Deterministic** - Same input = same output

## When to Use Each

**Use Autonomous Agent (`main_agent.py`) when:**
- ✅ You want intelligent, adaptive behavior
- ✅ You need to resume interrupted work
- ✅ Content quality varies and needs assessment
- ✅ You want progress tracking and reporting
- ✅ You're building a large knowledge base incrementally

**Use Pipeline (`main.py`) when:**
- ✅ You need predictable, repeatable behavior
- ✅ You're processing a fixed dataset
- ✅ Speed is more important than intelligence
- ✅ You want simple debugging

**Use Legacy (`local_agent_web_scraper.py`) when:**
- ✅ You need exact original behavior
- ✅ Testing compatibility

## Technical Details

**Agent LLM**: Ollama llama3.2:latest
- Reasoning and planning
- Tool selection
- Result interpretation

**Tools**: Agno framework `@tool` decorators
- Type-safe function signatures
- Automatic documentation
- Error handling

**Memory**: JSON-based persistent storage
- Survives restarts
- Human-readable
- Easy to inspect/modify

## Future Enhancements

Potential agent improvements:
- Multi-agent collaboration (scraper + quality checker)
- Learning from user feedback
- Dynamic goal adjustment
- Parallel execution of independent tools
- More sophisticated planning (tree search, MCTS)
- Integration with external knowledge sources
