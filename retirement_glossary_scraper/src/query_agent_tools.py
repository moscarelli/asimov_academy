"""
Query Agent Tools - Q&A and Tag Extraction from Knowledge Base
"""
from pathlib import Path
from typing import List, Dict, Any
from agno.tools import tool
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.chroma import ChromaDb

# Singleton instances
_embedder = None
_vector_db = None

# Known retirement plan acronyms for query expansion
RETIREMENT_ACRONYMS = {
    'EACA': 'Eligible Automatic Contribution Arrangement',
    'QACA': 'Qualified Automatic Contribution Arrangement',
    'RMD': 'Required Minimum Distribution',
    'IRA': 'Individual Retirement Arrangement',
    'ROTH': 'Roth IRA',
    'SEP': 'Simplified Employee Pension',
    'SIMPLE': 'Savings Incentive Match Plan for Employees',
    'QJSA': 'Qualified Joint and Survivor Annuity',
    'QPSA': 'Qualified Pre-Retirement Survivor Annuity',
    'QDRO': 'Qualified Domestic Relations Order',
    'ESOP': 'Employee Stock Ownership Plan',
    'SARSEP': 'Salary Reduction Simplified Employee Pension',
    'TSP': 'Thrift Savings Plan',
    'EPCU': 'Employee Plans Compliance Unit',
    'ERPA': 'Enrolled Retirement Plan Agent',
}

def expand_query(query: str) -> str:
    """
    Expand known acronyms in query for better semantic matching.
    
    Args:
        query: Original search query
        
    Returns:
        Query with acronyms expanded to include full terms
    """
    words = query.upper().split()
    expanded_terms = []
    
    for word in words:
        # Clean punctuation
        clean_word = word.strip('?.,!').upper()
        if clean_word in RETIREMENT_ACRONYMS:
            # Add both acronym and full term for better matching
            expanded_terms.append(f"{clean_word} {RETIREMENT_ACRONYMS[clean_word]}")
        else:
            expanded_terms.append(word)
    
    return ' '.join(expanded_terms)

def _get_vector_db():
    """Get or create ChromaDB connection singleton."""
    global _embedder, _vector_db
    
    if _vector_db is None:
        from .config import ScraperConfig
        config = ScraperConfig()
        
        _embedder = OllamaEmbedder(
            id=config.ollama_embedding_model,
            host=config.ollama_host,
            dimensions=config.ollama_embedding_dimensions,
            timeout=config.ollama_timeout
        )
        
        _vector_db = ChromaDb(
            collection=config.chroma_collection,
            embedder=_embedder,
            persistent_client=True,
            path=config.chroma_path,
        )
        print("✓ Connected to ChromaDB knowledge base")
    
    return _vector_db


@tool
def search_glossary(query: str, limit: int | None = None) -> str:
    """
    Search the IRS retirement glossary for relevant information.
    
    Use this tool to answer user questions about retirement topics.
    Returns the most relevant document excerpts that match the query.
    
    Args:
        query: The search query (e.g., "401k contribution limits")
        limit: Maximum number of results to return (default: 5, optional)
    
    Returns:
        Formatted search results with content and metadata
    """
    vector_db = _get_vector_db()
    # Use default of 5 if limit is None
    search_limit = limit if limit is not None else 5
    
    # Expand acronyms in query for better semantic matching
    expanded_query = expand_query(query)
    
    results = vector_db.search(expanded_query, limit=search_limit)
    
    if not results:
        return f"No results found for query: '{query}'"
    
    output = [f"Found {len(results)} relevant documents for: '{query}'\n"]
    
    for i, result in enumerate(results, 1):
        meta = getattr(result, "meta_data", {})
        content = getattr(result, "content", "")
        
        output.append(f"\n{'='*70}")
        output.append(f"RESULT #{i}")
        output.append(f"{'='*70}")
        
        # Key metadata using actual ChromaDB field names
        doc_number = meta.get('number', 'N/A')
        doc_title = meta.get('documentTitle', 'N/A')
        source_url = meta.get('source_url', 'N/A')
        filename = meta.get('mdfilename', 'N/A')
        
        output.append(f"Document #{doc_number}: {doc_title}")
        output.append(f"File: {filename}")
        output.append(f"URL: {source_url}")
        
        output.append(f"\nContent ({len(content)} chars):")
        output.append(f"{'-'*70}")
        # Show full content (or first 2000 chars for very long documents)
        preview = content[:2000] + "..." if len(content) > 2000 else content
        output.append(preview)
        output.append(f"{'-'*70}")
    
    return "\n".join(output)


@tool
def extract_tags_from_text(text: str, threshold: float = 0.5, max_tags: int = 10) -> str:
    """
    Extract retirement-related terms/tags from a large text by matching against the knowledge base.
    
    Use this tool when another API sends text and you need to identify relevant retirement concepts.
    Returns a list of matching terms with their document references for linking.
    
    Args:
        text: The large text to analyze (from external API)
        threshold: Similarity threshold (0.0-1.0) for matching (default: 0.5)
        max_tags: Maximum number of tags to extract (default: 10)
    
    Returns:
        JSON-formatted list of extracted tags with document references
    """
    vector_db = _get_vector_db()
    
    # Search using the full text to find relevant concepts
    results = vector_db.search(text, limit=max_tags * 2)
    
    if not results:
        return "No matching retirement terms found in text"
    
    # Extract unique tags with metadata
    tags = []
    seen_titles = set()
    
    for result in results:
        meta = getattr(result, "meta_data", {})
        title = meta.get("documentTitle", "Unknown")
        
        # Avoid duplicate tags
        if title in seen_titles:
            continue
        
        seen_titles.add(title)
        
        tag_info = {
            "term": title,
            "filename": meta.get("mdfilename", ""),
            "url": meta.get("source_url", ""),
            "relevance": "high" if len(tags) < 5 else "medium"
        }
        
        tags.append(tag_info)
        
        if len(tags) >= max_tags:
            break
    
    # Format output
    output = [f"Extracted {len(tags)} retirement-related tags from text:\n"]
    
    for i, tag in enumerate(tags, 1):
        output.append(f"\n{i}. {tag['term']}")
        output.append(f"   - Relevance: {tag['relevance']}")
        output.append(f"   - Filename: {tag['filename']}")
        if tag['url']:
            output.append(f"   - URL: {tag['url']}")
    
    return "\n".join(output)


@tool
def get_document_references(term: str) -> str:
    """
    Get detailed document references for a specific retirement term.
    
    Use this tool to get full metadata and linking information for a term.
    
    Args:
        term: The retirement term/concept (e.g., "401k", "Roth IRA")
    
    Returns:
        Document metadata including filename, URL, and content preview
    """
    vector_db = _get_vector_db()
    results = vector_db.search(term, limit=3)
    
    if not results:
        return f"No document references found for term: '{term}'"
    
    output = [f"Document references for '{term}':\n"]
    
    for i, result in enumerate(results, 1):
        meta = getattr(result, "meta_data", {})
        content = getattr(result, "content", "")
        
        output.append(f"\n{'='*70}")
        output.append(f"REFERENCE #{i}")
        output.append(f"{'='*70}")
        output.append(f"Document #{meta.get('number', 'N/A')}: {meta.get('documentTitle', 'N/A')}")
        output.append(f"Filename: {meta.get('mdfilename', 'N/A')}")
        output.append(f"URL: {meta.get('source_url', 'N/A')}")
        output.append(f"\nContent preview:")
        output.append(f"{'-'*70}")
        preview = content[:300] + "..." if len(content) > 300 else content
        output.append(preview)
        output.append(f"{'-'*70}")
    
    return "\n".join(output)


@tool
def analyze_text_for_concepts(text: str) -> str:
    """
    Analyze text to identify which retirement concepts are discussed.
    
    Use this to understand what retirement topics are covered in a piece of text.
    
    Args:
        text: Text to analyze
    
    Returns:
        List of identified retirement concepts with confidence levels
    """
    vector_db = _get_vector_db()
    
    # Split text into chunks if it's very long
    max_chunk_size = 1000
    if len(text) > max_chunk_size:
        # Take first chunk for analysis
        text = text[:max_chunk_size]
    
    results = vector_db.search(text, limit=5)
    
    if not results:
        return "No retirement concepts identified in text"
    
    output = ["Retirement concepts identified in text:\n"]
    
    for i, result in enumerate(results, 1):
        meta = getattr(result, "metadata", {})
        title = meta.get("title", "Unknown concept")
        
        output.append(f"\n{i}. {title}")
        output.append(f"   - Document: {meta.get('filename', 'N/A')}")
        output.append(f"   - Confidence: {'High' if i <= 2 else 'Medium' if i <= 4 else 'Low'}")
    
    return "\n".join(output)
