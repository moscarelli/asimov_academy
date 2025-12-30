"""
Configuration module for the IRS Retirement Glossary Scraper.
"""
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperConfig:
    """Configuration settings for the scraper."""
    
    # URLs and paths
    main_url: str = "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics"
    out_dir: Path = Path("./out/irs_retirement_topics")
    
    # Control flags
    skip_existing_raw: bool = True
    process_content: bool = True
    wait_before_processing: int = 20
    index_to_chromadb: bool = True
    
    # Ollama settings
    ollama_model: str = "llama3.2:latest"
    ollama_host: str = "http://localhost:11434"
    ollama_embedding_dimensions: int = 3072
    ollama_timeout: int = 60
    
    # ChromaDB settings
    chroma_path: str = "tmp/chroma_retirement_glossary"
    chroma_collection: str = "irs_retirement_glossary"
    
    # Rate limiting
    download_delay: int = 2
    index_delay: float = 0.5
    
    def __post_init__(self):
        """Initialize derived paths."""
        self.raw_dir = self.out_dir / "raw"
        self.processed_dir = self.out_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def urls_file(self) -> Path:
        """Path to the discovered URLs file."""
        return self.out_dir / "discovered_urls.txt"
