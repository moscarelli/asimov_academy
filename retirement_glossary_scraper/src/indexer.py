"""
ChromaDB indexing module for creating searchable knowledge base.
"""
from pathlib import Path
import json
import time
import re
from typing import Tuple

from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader

from .config import ScraperConfig


def extract_acronyms(text: str) -> dict:
    """
    Extract acronyms and their expansions from text.
    Matches patterns like: 'Full Term Name (ACRONYM)'
    
    Args:
        text: Document content to search for acronyms
        
    Returns:
        Dictionary mapping acronyms to their full terms
    """
    # Pattern: capitalized words followed by (CAPS)
    pattern = r'([A-Z][A-Za-z\s&-]+?)\s*\(([A-Z]{2,})\)'
    acronyms = {}
    
    for match in re.finditer(pattern, text):
        full_term = match.group(1).strip()
        acronym = match.group(2)
        # Store acronym -> full term mapping
        acronyms[acronym] = full_term
    
    return acronyms


def augment_content_with_acronyms(content: str) -> str:
    """
    Add searchable acronym section to content for better semantic search.
    
    Args:
        content: Original document content
        
    Returns:
        Content with appended acronym mappings
    """
    acronyms = extract_acronyms(content)
    
    if not acronyms:
        return content
    
    # Append acronym index at the end for semantic search
    augmented = content + "\n\n## Document Acronyms:\n"
    for acronym, expansion in acronyms.items():
        # Add bidirectional mappings for better search
        augmented += f"{acronym} stands for {expansion}. "
        augmented += f"{expansion} is abbreviated as {acronym}. "
    
    return augmented


class ChromaDBIndexer:
    """Handles ChromaDB indexing and search operations."""
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize the ChromaDB indexer.
        
        Args:
            config: Configuration object with ChromaDB settings
        """
        self.config = config
        self.embeddings = None
        self.vector_db = None
        self.knowledge = None
        self.indexed_count = 0
        self.error_count = 0
    
    def initialize(self):
        """Initialize ChromaDB components."""
        print(f"\n[STEP 5] Indexing markdown files to ChromaDB...")
        print(f"LOG: Initializing ChromaDB...")
        
        try:
            # Initialize embedder
            print(f"LOG: Creating OllamaEmbedder ({self.config.ollama_embedding_model}, {self.config.ollama_embedding_dimensions} dimensions)...")
            self.embeddings = OllamaEmbedder(
                id=self.config.ollama_embedding_model,
                host=self.config.ollama_host,
                dimensions=self.config.ollama_embedding_dimensions,
                timeout=self.config.ollama_timeout
            )
            print(f"LOG: ✓ Embedder initialized")
            
            # Initialize ChromaDB
            print(f"LOG: Creating ChromaDB collection at: {self.config.chroma_path}")
            self.vector_db = ChromaDb(
                collection=self.config.chroma_collection,
                embedder=self.embeddings,
                persistent_client=True,
                path=self.config.chroma_path,
            )
            print(f"LOG: ✓ ChromaDB initialized")
            
            # Create Knowledge base
            print(f"LOG: Creating Knowledge base...")
            self.knowledge = Knowledge(vector_db=self.vector_db)
            print(f"LOG: ✓ Knowledge base initialized")
            
        except Exception as e:
            print(f"LOG: ✗ ERROR initializing ChromaDB: {str(e)}")
            raise
    
    def index_all_files(self) -> Tuple[int, int]:
        """
        Index all markdown files to ChromaDB.
        
        Returns:
            Tuple of (indexed_count, error_count)
        """
        if self.knowledge is None:
            raise RuntimeError("ChromaDB not initialized. Call initialize() first.")
        
        # Get all markdown files
        md_files = sorted(self.config.processed_dir.glob("*.md"))
        print(f"LOG: Found {len(md_files)} markdown files to index")
        
        self.indexed_count = 0
        self.error_count = 0
        
        for md_file in md_files:
            try:
                self._index_single_file(md_file)
            except Exception as e:
                print(f"LOG: ✗ ERROR indexing {md_file.name}: {str(e)}")
                self.error_count += 1
        
        print(f"\nLOG: ChromaDB indexing complete!")
        print(f"LOG:   Indexed: {self.indexed_count}")
        print(f"LOG:   Errors: {self.error_count}")
        print(f"LOG:   Collection: {self.config.chroma_collection}")
        print(f"LOG:   Location: {Path(self.config.chroma_path).absolute()}")
        
        return self.indexed_count, self.error_count
    
    def _index_single_file(self, md_file: Path):
        """
        Index a single markdown file.
        
        Args:
            md_file: Path to the markdown file
        """
        print(f"\nLOG: Indexing: {md_file.name}")
        
        # Load markdown content
        print(f"LOG:   Loading markdown content...")
        md_content = md_file.read_text(encoding='utf-8')
        
        # Load corresponding JSON metadata
        json_file = self.config.raw_dir / f"{md_file.stem}.json"
        metadata = {}
        if json_file.exists():
            print(f"LOG:   Loading JSON metadata...")
            metadata = json.loads(json_file.read_text(encoding='utf-8'))
            print(f"LOG:   ✓ Loaded metadata")
        else:
            print(f"LOG:   ⚠ Warning: JSON metadata not found, using minimal metadata")
        
        # Parse frontmatter and extract content
        clean_content = self._extract_content_without_frontmatter(md_content)
        print(f"LOG:   ✓ Extracted content ({len(clean_content)} characters)")
        
        # Augment content with acronym mappings for better search
        searchable_content = augment_content_with_acronyms(clean_content)
        if len(searchable_content) > len(clean_content):
            acronym_count = len(extract_acronyms(clean_content))
            print(f"LOG:   ✓ Added {acronym_count} acronym mappings for searchability")
        
        # Prepare metadata for ChromaDB
        doc_metadata = {
            "number": metadata.get('number', 0),
            "source_url": metadata.get('url', ''),
            "filename": metadata.get('filename', md_file.stem),
            "mdfilename": metadata.get('mdfilename', md_file.name),
            "documentTitle": metadata.get('documentTitle', 'Untitled'),
            "downloaded_at": metadata.get('downloaded_at', ''),
            "processed_at": metadata.get('processed_at', ''),
        }
        
        print(f"LOG:   Indexing document: '{doc_metadata['documentTitle']}'")
        
        # Create temporary file with augmented content for indexing
        # (Agno loads from file path, so we need to write augmented content)
        temp_md_file = md_file.parent / f"temp_{md_file.name}"
        temp_md_file.write_text(searchable_content, encoding='utf-8')
        
        try:
            # Use knowledge.add_content() with augmented content file
            self.knowledge.add_content(
                path=str(temp_md_file),
                reader=TextReader(),
                metadata=doc_metadata,
                skip_if_exists=True
            )
        finally:
            # Clean up temporary file
            if temp_md_file.exists():
                temp_md_file.unlink()
        
        print(f"LOG: ✓ SUCCESS: Indexed {md_file.name}")
        self.indexed_count += 1
        
        # Small delay to avoid overwhelming the embedding service
        time.sleep(self.config.index_delay)
    
    def _extract_content_without_frontmatter(self, content: str) -> str:
        """
        Extract content without YAML frontmatter.
        
        Args:
            content: Full markdown content
            
        Returns:
            Content without frontmatter
        """
        lines = content.split('\n')
        in_frontmatter = False
        frontmatter_ended = False
        content_lines = []
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                    continue
                elif in_frontmatter and not frontmatter_ended:
                    frontmatter_ended = True
                    continue
            
            if frontmatter_ended:
                content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def test_search(self, query: str = "What are 401k contribution limits?", limit: int = 5):
        """
        Test the indexing with a sample query.
        
        Args:
            query: Search query
            limit: Maximum number of results
        """
        print(f"\n[TEST QUERY] Testing ChromaDB search functionality...")
        print(f"LOG: Running test query: '{query}'")
        
        try:
            results = self.vector_db.search(query, limit=limit)
            print(f"LOG: ✓ Query successful! Found {len(results)} results\n")
            
            for i, result in enumerate(results, 1):
                meta = getattr(result, "metadata", {})
                content = getattr(result, "content", "") or ""
                
                print(f"--- RESULT {i} ---")
                print(f"Document: {meta.get('documentTitle', 'N/A')}")
                print(f"Source: {meta.get('source_url', 'N/A')}")
                print(f"Content preview: {content[:300]}...")
                print()
                
        except Exception as e:
            print(f"LOG: ✗ ERROR during test query: {str(e)}")
    
    def get_stats(self) -> dict:
        """
        Get indexing statistics.
        
        Returns:
            Dictionary with indexing statistics
        """
        return {
            'indexed': self.indexed_count,
            'errors': self.error_count,
            'collection': self.config.chroma_collection
        }
