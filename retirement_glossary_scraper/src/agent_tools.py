"""
Tool functions for the autonomous scraper agent.
These are the agent's capabilities - what it can actually DO.
"""
from pathlib import Path
from typing import List, Dict, Any
import json
from bs4 import BeautifulSoup

from agno.tools import tool

from .config import ScraperConfig
from .scraper import WebScraper
from .processor import ContentProcessor
from .indexer import ChromaDBIndexer
from .agent_memory import AgentMemory


# Initialize shared components
_config = ScraperConfig()
_memory = AgentMemory()


@tool
def analyze_website(url: str) -> Dict[str, Any]:
    """
    Analyze a website to identify retirement-related content.
    Agent uses this to decide if a site is worth scraping.
    
    Args:
        url: Website URL to analyze
        
    Returns:
        Dictionary with analysis results including page_count, topics_found, quality_score
    """
    try:
        scraper = WebScraper(_config)
        urls = scraper.discover_urls()
        
        # Extract topics from URLs
        topics = set()
        for u in urls:
            if '401k' in u.lower():
                topics.add('401k')
            if 'ira' in u.lower():
                topics.add('IRA')
            if 'rmd' in u.lower() or 'minimum-distribution' in u.lower():
                topics.add('RMD')
            if 'contribution' in u.lower():
                topics.add('contributions')
            if 'distribution' in u.lower():
                topics.add('distributions')
        
        quality_score = min(1.0, len(urls) / 100.0)  # Quality based on content volume
        
        result = {
            "success": True,
            "page_count": len(urls),
            "topics_found": list(topics),
            "quality_score": quality_score,
            "recommended_action": "scrape" if len(urls) > 0 else "skip"
        }
        
        _memory.remember_event("analysis", result)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recommended_action": "skip"
        }


@tool
def scrape_urls(max_pages: int = None) -> Dict[str, Any]:
    """
    Download HTML from discovered URLs.
    Agent decides how many pages to scrape at once.
    
    Args:
        max_pages: Optional limit on pages to scrape (None = all)
        
    Returns:
        Dictionary with download statistics
    """
    try:
        scraper = WebScraper(_config)
        urls = scraper.discover_urls()
        
        # Filter out already scraped URLs
        new_urls = [u for u in urls if not _memory.has_scraped(u)]
        
        if max_pages:
            new_urls = new_urls[:max_pages]
        
        if not new_urls:
            return {
                "success": True,
                "downloaded": 0,
                "skipped": len(urls),
                "errors": 0,
                "message": "All URLs already scraped"
            }
        
        stats = scraper.download_html_files(new_urls)
        
        # Mark URLs as scraped
        for url in new_urls:
            _memory.mark_url_scraped(url)
        
        result = {
            "success": True,
            "downloaded": stats[0],
            "skipped": stats[1],
            "errors": stats[2],
            "new_urls_processed": len(new_urls)
        }
        
        _memory.remember_event("scrape", result)
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        _memory.record_failure({"operation": "scrape", "error": str(e)})
        return error_result


@tool
def check_content_quality(sample_size: int = 5) -> Dict[str, Any]:
    """
    Assess quality of downloaded HTML content by sampling.
    Agent uses this to decide if content is worth processing.
    
    Args:
        sample_size: Number of files to sample for quality check
        
    Returns:
        Dictionary with quality assessment
    """
    try:
        raw_files = list(_config.raw_dir.glob("*.html"))
        
        if not raw_files:
            return {
                "success": True,
                "quality_score": 0.0,
                "has_content": False,
                "is_relevant": False,
                "should_process": False,
                "message": "No files to check"
            }
        
        # Sample files
        sample_files = raw_files[:sample_size] if len(raw_files) > sample_size else raw_files
        
        total_score = 0
        relevant_count = 0
        has_content_count = 0
        
        for html_file in sample_files:
            html_content = html_file.read_text(encoding='utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text()
            
            # Check content length
            if len(text) > 500:
                has_content_count += 1
            
            # Check relevance
            retirement_keywords = ['retirement', '401k', 'ira', 'pension', 'rmd']
            if any(keyword in text.lower() for keyword in retirement_keywords):
                relevant_count += 1
                total_score += 1
        
        avg_score = total_score / len(sample_files) if sample_files else 0
        
        result = {
            "success": True,
            "quality_score": avg_score,
            "has_content": has_content_count / len(sample_files) > 0.8,
            "is_relevant": relevant_count / len(sample_files) > 0.8,
            "should_process": avg_score > 0.7,
            "files_checked": len(sample_files)
        }
        
        _memory.update_quality_metrics({"content_quality": avg_score})
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "should_process": False
        }


@tool
def process_content() -> Dict[str, Any]:
    """
    Convert ALL HTML files to markdown. Takes NO parameters - call it as process_content().
    Processes all HTML files in the raw directory and converts them to clean markdown.
    Automatically skips already processed files.
    
    Returns:
        Dictionary with processing statistics (processed count, errors)
    """
    try:
        processor = ContentProcessor(_config)
        stats = processor.process_all_files()
        
        result = {
            "success": True,
            "processed": stats[0],
            "errors": stats[1]
        }
        
        _memory.remember_event("process", result)
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        _memory.record_failure({"operation": "process", "error": str(e)})
        return error_result


@tool
def index_to_database() -> Dict[str, Any]:
    """
    Index ALL markdown files to ChromaDB. Takes NO parameters - call it as index_to_database().
    Indexes all markdown files in the processed directory to make them searchable.
    Automatically skips already indexed files.
    
    Returns:
        Dictionary with indexing statistics (indexed count, errors)
    """
    try:
        indexer = ChromaDBIndexer(_config)
        indexer.initialize()
        stats = indexer.index_all_files()
        
        # Record indexed documents
        md_files = list(_config.processed_dir.glob("*.md"))
        for md_file in md_files:
            json_file = _config.raw_dir / f"{md_file.stem}.json"
            if json_file.exists():
                metadata = json.loads(json_file.read_text(encoding='utf-8'))
                _memory.add_indexed_document({
                    "filename": md_file.name,
                    "title": metadata.get("documentTitle", "Unknown"),
                    "url": metadata.get("url", "")
                })
        
        result = {
            "success": True,
            "indexed": stats[0],
            "errors": stats[1],
            "collection": _config.chroma_collection
        }
        
        _memory.remember_event("index", result)
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        _memory.record_failure({"operation": "index", "error": str(e)})
        return error_result


@tool
def verify_indexing(query: str = "What are 401k contribution limits?") -> Dict[str, Any]:
    """
    Test knowledge base with a query to verify quality.
    Agent uses this to ensure indexing worked correctly.
    
    Args:
        query: Test query to run
        
    Returns:
        Dictionary with verification results
    """
    try:
        indexer = ChromaDBIndexer(_config)
        indexer.initialize()
        results = indexer.vector_db.search(query, limit=5)
        
        quality_score = min(1.0, len(results) / 3.0)  # Good if we get 3+ results
        
        result = {
            "success": True,
            "found_results": len(results),
            "quality_score": quality_score,
            "needs_improvement": len(results) < 3,
            "query_used": query
        }
        
        _memory.update_quality_metrics({"search_quality": quality_score})
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "needs_improvement": True
        }


@tool
def search_knowledge_base(query: str, limit: int = 5) -> Dict[str, Any]:
    """
    Search the knowledge base and return results.
    Agent uses this to explore what's in the knowledge base.
    
    Args:
        query: Search query
        limit: Maximum results to return
        
    Returns:
        Dictionary with search results
    """
    try:
        indexer = ChromaDBIndexer(_config)
        indexer.initialize()
        results = indexer.vector_db.search(query, limit=limit)
        
        formatted_results = []
        for r in results:
            meta = getattr(r, "metadata", {})
            content = getattr(r, "content", "")
            formatted_results.append({
                "title": meta.get("documentTitle", "Unknown"),
                "url": meta.get("source_url", ""),
                "content_preview": content[:200] if content else ""
            })
        
        return {
            "success": True,
            "query": query,
            "results_found": len(formatted_results),
            "results": formatted_results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }


@tool
def assess_progress() -> Dict[str, Any]:
    """
    Check progress toward goal. NO PARAMETERS - call as: assess_progress()
    Verifies ACTUAL ChromaDB state vs memory to detect if re-indexing is needed.
    Returns indexed document count, progress percentage, quality metrics, status, and recommendations.
    
    Returns:
        Dict with 'documents_indexed', 'progress_percentage', 'quality_metrics', 'status', 'recommendation', 'goal_reached', 'actual_db_count', 'memory_count', 'needs_reindex'
    """
    try:
        memory_indexed_count = _memory.get_indexed_count()
        quality_metrics = _memory.get_quality_metrics()
        failed_attempts = len(_memory.memory.get("failed_attempts", []))
        
        # VERIFY ACTUAL CHROMADB STATE
        actual_db_count = 0
        needs_reindex = False
        try:
            from agno.knowledge.embedder.ollama import OllamaEmbedder
            from agno.vectordb.chroma import ChromaDb
            
            embedder = OllamaEmbedder(
                id=_config.ollama_embedding_model,
                host=_config.ollama_host,
                dimensions=_config.ollama_embedding_dimensions,
                timeout=_config.ollama_timeout
            )
            
            vector_db = ChromaDb(
                collection=_config.chroma_collection,
                embedder=embedder,
                persistent_client=True,
                path=_config.chroma_path,
            )
            
            # Try a test search to see if database has content
            test_results = vector_db.search("retirement", limit=1)
            actual_db_count = len(test_results) if test_results else 0
            
            # Check if memory says docs are indexed but DB is empty
            if memory_indexed_count > 0 and actual_db_count == 0:
                needs_reindex = True
                
        except Exception as e:
            # If can't access DB, assume needs indexing
            needs_reindex = True if memory_indexed_count > 0 else False
        
        # Use actual count if available, otherwise use memory
        indexed_count = memory_indexed_count if not needs_reindex else 0
        
        # Calculate progress
        progress_pct = min(100, (indexed_count / 100) * 100)
        
        # Determine recommendation
        if needs_reindex:
            recommendation = "ChromaDB is empty or missing - run index_to_database() immediately"
            status = "needs_reindex"
        elif indexed_count < 50:
            recommendation = "Continue aggressive scraping and indexing"
            status = "in_progress"
        elif indexed_count < 100:
            recommendation = "Focus on quality verification and gap filling"
            status = "in_progress"
        elif quality_metrics.get("search_quality", 0) < 0.8:
            recommendation = "Improve indexing quality"
            status = "in_progress"
        else:
            recommendation = "Goal achieved! Knowledge base is complete."
            status = "complete"
        
        result = {
            "success": True,
            "documents_indexed": indexed_count,
            "actual_db_count": actual_db_count,
            "memory_count": memory_indexed_count,
            "needs_reindex": needs_reindex,
            "progress_percentage": progress_pct,
            "quality_metrics": quality_metrics,
            "failed_attempts": failed_attempts,
            "status": status,
            "recommendation": recommendation,
            "goal_reached": status == "complete"
        }
        
        _memory.update_goal_progress(result)
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "status": "error"
        }


@tool
def get_memory_summary() -> Dict[str, Any]:
    """
    Get summary of agent's memory and past actions.
    Agent uses this to understand what it has already done.
    
    Returns:
        Dictionary with memory summary
    """
    return {
        "success": True,
        **_memory.get_summary()
    }
