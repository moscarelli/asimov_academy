"""
Content processing module for converting HTML to markdown.
"""
from pathlib import Path
from datetime import datetime
import json
import time
from typing import Tuple
from bs4 import BeautifulSoup

from agno.agent import Agent
from agno.models.ollama import Ollama

from .config import ScraperConfig


class ContentProcessor:
    """Handles HTML to markdown conversion using AI."""
    
    def __init__(self, config: ScraperConfig):
        """
        Initialize the content processor.
        
        Args:
            config: Configuration object with processor settings
        """
        self.config = config
        self.model = Ollama(id=config.ollama_model, host=config.ollama_host)
        self.agent = None
        self.processed_count = 0
        self.error_count = 0
    
    def _initialize_agent(self):
        """Initialize the content processing agent."""
        if self.agent is None:
            print(f"LOG: Initializing content processing agent...")
            self.agent = Agent(
                model=self.model,
                tools=[],
                instructions="""
You are a content normalizer.

Rules:
- Extract only the main article content from the HTML
- Ignore headers, footers, banners, navigation and language selectors
- Keep English content only
- Output clean, well-structured Markdown
- Do not add explanations or comments
"""
            )
            print(f"LOG: ✓ Agent initialized")
    
    def wait_before_processing(self):
        """Display countdown before starting processing."""
        if self.config.wait_before_processing > 0:
            print(f"\n[STEP 3] Waiting {self.config.wait_before_processing} seconds before starting post-processing...")
            for i in range(self.config.wait_before_processing, 0, -1):
                print(f"LOG: Waiting... {i} seconds remaining", end='\r')
                time.sleep(1)
            print(f"\nLOG: ✓ Wait complete, starting post-processing...")
    
    def process_all_files(self) -> Tuple[int, int]:
        """
        Process all HTML files to markdown.
        
        Returns:
            Tuple of (processed_count, error_count)
        """
        print(f"\n[STEP 4] Processing raw HTML to markdown...")
        print(f"LOG: Processing all HTML files in: {self.config.raw_dir}")
        
        self._initialize_agent()
        
        self.processed_count = 0
        self.error_count = 0
        
        # Get all HTML files sorted by name
        html_files = sorted(self.config.raw_dir.glob("*.html"))
        print(f"LOG: Found {len(html_files)} HTML files to process")
        
        for html_file in html_files:
            try:
                self._process_single_file(html_file)
            except Exception as e:
                print(f"LOG: ✗ ERROR processing {html_file.name}: {str(e)}")
                self.error_count += 1
        
        print(f"\nLOG: Post-processing complete!")
        print(f"LOG:   Processed successfully: {self.processed_count}")
        print(f"LOG:   Errors: {self.error_count}")
        
        return self.processed_count, self.error_count
    
    def _process_single_file(self, html_file: Path):
        """
        Process a single HTML file to markdown.
        
        Args:
            html_file: Path to the HTML file
        """
        print(f"\nLOG: Processing: {html_file.name}")
                # Check if already processed
        md_file = self.config.processed_dir / f"{html_file.stem}.md"
        if md_file.exists():
            print(f"LOG: ⊘ Skipped (already processed): {md_file.name}")
            self.processed_count += 1  # Count as processed
            return
                # Load raw HTML
        print(f"LOG:   Loading HTML content...")
        html_content = html_file.read_text(encoding='utf-8')
        print(f"LOG:   ✓ Loaded {len(html_content)} characters")
        
        # Load metadata
        meta_file = self.config.raw_dir / f"{html_file.stem}.json"
        metadata = {}
        if meta_file.exists():
            print(f"LOG:   Loading metadata...")
            metadata = json.loads(meta_file.read_text(encoding='utf-8'))
            print(f"LOG:   ✓ Loaded metadata")
        
        # Parse HTML with BeautifulSoup
        print(f"LOG:   Parsing HTML with BeautifulSoup...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract main content
        main_content = soup.get_text(separator='\n', strip=True)
        print(f"LOG:   ✓ Extracted text content ({len(main_content)} characters)")
        
        # Process with agent
        print(f"LOG:   Processing with AI agent...")
        content_to_process = main_content[:8000]  # Limit to avoid token issues
        response = self.agent.run(
            f"Convert this webpage text to clean markdown:\n\n{content_to_process}"
        )
        print(f"LOG:   ✓ AI processing complete")
        
        # Create markdown with frontmatter
        final_content = self._create_markdown_with_frontmatter(response.content, metadata)
        
        # Save processed content
        md_file = self.config.processed_dir / f"{html_file.stem}.md"
        print(f"LOG:   Saving markdown to: {md_file.name}")
        md_file.write_text(final_content, encoding='utf-8')
        
        # Extract and update title
        document_title = self._extract_title(final_content)
        print(f"LOG:   ✓ Extracted title: '{document_title}'")
        
        # Update JSON metadata
        self._update_metadata(meta_file, metadata, md_file.name, document_title)
        
        print(f"LOG: ✓ SUCCESS: {md_file.name}")
        self.processed_count += 1
    
    def _create_markdown_with_frontmatter(self, content: str, metadata: dict) -> str:
        """
        Create markdown content with YAML frontmatter.
        
        Args:
            content: Processed markdown content
            metadata: Document metadata
            
        Returns:
            Complete markdown with frontmatter
        """
        frontmatter = "---\n"
        frontmatter += f"number: {metadata.get('number', 'unknown')}\n"
        frontmatter += f"source_url: {metadata.get('url', 'unknown')}\n"
        frontmatter += f"downloaded_at: {metadata.get('downloaded_at', 'unknown')}\n"
        frontmatter += f"processed_at: {datetime.now().isoformat()}\n"
        frontmatter += "---\n\n"
        
        return frontmatter + content
    
    def _extract_title(self, content: str) -> str:
        """
        Extract document title from markdown content.
        
        Args:
            content: Markdown content with frontmatter
            
        Returns:
            Extracted title or "Untitled"
        """
        document_title = "Untitled"
        lines = content.split('\n')
        in_frontmatter = False
        frontmatter_closed = False
        
        for line in lines:
            if line.strip() == '---':
                if not in_frontmatter:
                    in_frontmatter = True
                elif in_frontmatter and not frontmatter_closed:
                    frontmatter_closed = True
                continue
            
            if frontmatter_closed and line.strip().startswith('# '):
                document_title = line.strip()[2:].strip()
                break
        
        return document_title
    
    def _update_metadata(self, meta_file: Path, metadata: dict, md_filename: str, title: str):
        """
        Update JSON metadata with markdown information.
        
        Args:
            meta_file: Path to JSON metadata file
            metadata: Original metadata dictionary
            md_filename: Markdown filename
            title: Document title
        """
        print(f"LOG:   Updating JSON metadata...")
        metadata['mdfilename'] = md_filename
        metadata['documentTitle'] = title
        meta_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        print(f"LOG:   ✓ Updated JSON metadata")
    
    def get_stats(self) -> dict:
        """
        Get processing statistics.
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            'processed': self.processed_count,
            'errors': self.error_count
        }
