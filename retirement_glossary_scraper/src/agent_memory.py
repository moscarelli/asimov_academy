"""
Agent memory system for tracking scraping progress and learned information.
"""
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Set, Any


# Get the project root directory (retirement_glossary_scraper/)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class AgentMemory:
    """Persistent memory for the autonomous scraper agent."""
    
    def __init__(self, memory_file: str = None):
        """
        Initialize agent memory.
        
        Args:
            memory_file: Path to JSON file for persistent storage (default: PROJECT_ROOT/tmp/agent_memory.json)
        """
        if memory_file is None:
            memory_file = PROJECT_ROOT / "tmp" / "agent_memory.json"
        self.memory_file = Path(memory_file)
        self.memory = self._load()
    
    def _load(self) -> dict:
        """Load memory from disk or initialize new memory."""
        if self.memory_file.exists():
            try:
                data = json.loads(self.memory_file.read_text(encoding='utf-8'))
                # Convert scraped_urls back to set
                if 'scraped_urls' in data and isinstance(data['scraped_urls'], list):
                    data['scraped_urls'] = set(data['scraped_urls'])
                return data
            except Exception as e:
                print(f"Warning: Could not load memory, starting fresh: {e}")
        
        return {
            "sessions": [],
            "scraped_urls": set(),
            "indexed_documents": [],
            "failed_attempts": [],
            "knowledge_gaps": [],
            "quality_metrics": {},
            "goal_progress": {}
        }
    
    def _save(self):
        """Save memory to disk."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        # Convert set to list for JSON serialization
        save_data = self.memory.copy()
        if 'scraped_urls' in save_data:
            save_data['scraped_urls'] = list(save_data['scraped_urls'])
        
        self.memory_file.write_text(
            json.dumps(save_data, indent=2, default=str),
            encoding='utf-8'
        )
    
    def remember_event(self, event_type: str, data: Dict[str, Any]):
        """
        Store an event in memory.
        
        Args:
            event_type: Type of event (e.g., 'scrape', 'index', 'error')
            data: Event data dictionary
        """
        self.memory["sessions"].append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        })
        self._save()
    
    def mark_url_scraped(self, url: str):
        """
        Mark a URL as scraped.
        
        Args:
            url: URL that was scraped
        """
        if 'scraped_urls' not in self.memory:
            self.memory['scraped_urls'] = set()
        self.memory['scraped_urls'].add(url)
        self._save()
    
    def has_scraped(self, url: str) -> bool:
        """
        Check if URL was already scraped.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL was already scraped
        """
        return url in self.memory.get("scraped_urls", set())
    
    def add_indexed_document(self, doc_info: Dict[str, Any]):
        """
        Record an indexed document.
        
        Args:
            doc_info: Document metadata
        """
        self.memory["indexed_documents"].append({
            "timestamp": datetime.now().isoformat(),
            **doc_info
        })
        self._save()
    
    def get_indexed_count(self) -> int:
        """Get number of indexed documents."""
        return len(self.memory.get("indexed_documents", []))
    
    def record_failure(self, failure_info: Dict[str, Any]):
        """
        Record a failed attempt.
        
        Args:
            failure_info: Information about the failure
        """
        self.memory["failed_attempts"].append({
            "timestamp": datetime.now().isoformat(),
            **failure_info
        })
        self._save()
    
    def add_knowledge_gap(self, topic: str):
        """
        Record a topic that needs more coverage.
        
        Args:
            topic: Topic name
        """
        if topic not in self.memory.get("knowledge_gaps", []):
            self.memory["knowledge_gaps"].append(topic)
            self._save()
    
    def get_knowledge_gaps(self) -> List[str]:
        """Get list of topics needing more coverage."""
        return self.memory.get("knowledge_gaps", [])
    
    def update_quality_metrics(self, metrics: Dict[str, float]):
        """
        Update quality metrics.
        
        Args:
            metrics: Quality metrics dictionary
        """
        self.memory["quality_metrics"].update({
            "timestamp": datetime.now().isoformat(),
            **metrics
        })
        self._save()
    
    def get_quality_metrics(self) -> Dict[str, Any]:
        """Get current quality metrics."""
        return self.memory.get("quality_metrics", {})
    
    def update_goal_progress(self, progress: Dict[str, Any]):
        """
        Update progress toward goal.
        
        Args:
            progress: Progress information
        """
        self.memory["goal_progress"] = {
            "timestamp": datetime.now().isoformat(),
            **progress
        }
        self._save()
    
    def get_goal_progress(self) -> Dict[str, Any]:
        """Get current goal progress."""
        return self.memory.get("goal_progress", {})
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """
        Get most recent events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        sessions = self.memory.get("sessions", [])
        return sessions[-limit:] if sessions else []
    
    def clear_memory(self):
        """Clear all memory (use with caution!)."""
        self.memory = {
            "sessions": [],
            "scraped_urls": set(),
            "indexed_documents": [],
            "failed_attempts": [],
            "knowledge_gaps": [],
            "quality_metrics": {},
            "goal_progress": {}
        }
        self._save()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of agent's memory.
        
        Returns:
            Summary dictionary
        """
        return {
            "total_sessions": len(self.memory.get("sessions", [])),
            "scraped_urls_count": len(self.memory.get("scraped_urls", set())),
            "indexed_documents": self.get_indexed_count(),
            "failed_attempts": len(self.memory.get("failed_attempts", [])),
            "knowledge_gaps": len(self.get_knowledge_gaps()),
            "has_quality_metrics": bool(self.memory.get("quality_metrics")),
            "current_progress": self.get_goal_progress()
        }
