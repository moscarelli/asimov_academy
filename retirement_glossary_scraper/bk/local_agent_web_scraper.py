from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urljoin
import time
import re
import json
import requests
from bs4 import BeautifulSoup

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.text_reader import TextReader


# ---------------- Configuration ----------------

MAIN_URL = "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics"
OUT_DIR = Path("./out/irs_retirement_topics")
RAW_DIR = OUT_DIR / "raw"
PROCESSED_DIR = OUT_DIR / "processed"

# Create directories
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Control flags
SKIP_EXISTING_RAW = True   # Set to False to re-download all HTML files
PROCESS_CONTENT = False     # Set to True to process raw HTML into markdown
WAIT_BEFORE_PROCESSING = 20 # Seconds to wait before starting post-processing
INDEX_TO_CHROMADB = True    # Set to True to index markdown files to ChromaDB

model = Ollama(id="llama3.2:latest", host="http://localhost:11434")

print("="*60)
print("IRS Retirement Topics Scraper")
print("="*60)
print(f"Main URL: {MAIN_URL}")
print(f"Raw HTML dir: {RAW_DIR}")
print(f"Processed dir: {PROCESSED_DIR}")
print(f"Skip existing raw: {SKIP_EXISTING_RAW}")
print(f"Process content: {PROCESS_CONTENT}")
print(f"Wait before processing: {WAIT_BEFORE_PROCESSING}s")
print(f"Index to ChromaDB: {INDEX_TO_CHROMADB}")
print("="*60)

# ---------------- Step 1: Get all topic links using BeautifulSoup ----------------

print(f"\n[STEP 1] Fetching topic links from main page using HTML parser...")
print(f"LOG: Requesting URL: {MAIN_URL}")

try:
    # Download the page
    print(f"LOG: Sending HTTP GET request...")
    response = requests.get(MAIN_URL, timeout=30)
    response.raise_for_status()
    print(f"LOG: ✓ Downloaded page successfully ({len(response.content)} bytes)")
    
    # Parse HTML
    print(f"LOG: Parsing HTML with BeautifulSoup...")
    soup = BeautifulSoup(response.content, 'html.parser')
    print(f"LOG: ✓ HTML parsed successfully")
    
    # Find all links
    all_links = soup.find_all('a', href=True)
    print(f"LOG: ✓ Found {len(all_links)} total links on page")
    
    # Filter for retirement topic links (preserve order)
    print(f"LOG: Filtering retirement topic links (preserving page order)...")
    urls = []
    seen = set()  # Track duplicates while preserving order
    
    for idx, link in enumerate(all_links, 1):
        href = link['href']
        
        # Make absolute URL
        if href.startswith('/'):
            href = urljoin(MAIN_URL, href)
        
        # Only keep IRS retirement-related links
        if href.startswith('http') and 'irs.gov' in href and 'retirement' in href.lower():
            # Skip language variants and the main index page
            if (href != MAIN_URL and 
                '/es/' not in href and '/ko/' not in href and 
                '/zh-hans/' not in href and '/zh-hant/' not in href and 
                '/ru/' not in href and '/vi/' not in href and '/ht/' not in href):
                
                # Remove URL fragments (anchors)
                if '#' in href:
                    href = href.split('#')[0]
                
                # Add only if not seen before (preserve first occurrence)
                if href not in seen:
                    urls.append(href)
                    seen.add(href)
                    print(f"LOG:   [{len(urls)}] Found: {href}")
    
    print(f"\nLOG: ✓ Found {len(urls)} unique retirement topic URLs (in page order)")
    
except Exception as e:
    print(f"✗ Error fetching links: {e}")
    exit(1)

# Save URLs to file for reference (with numbering)
print(f"\nLOG: Saving discovered URLs...")
urls_file = OUT_DIR / "discovered_urls.txt"
numbered_urls = [f"{idx}. {url}" for idx, url in enumerate(urls, 1)]
urls_file.write_text('\n'.join(numbered_urls), encoding='utf-8')
print(f"LOG: ✓ Saved {len(urls)} numbered URLs to: {urls_file}")

# ---------------- Step 2: Download raw HTML content ----------------

print(f"\n[STEP 2] Downloading raw HTML content...")
print(f"LOG: Skip existing raw files: {SKIP_EXISTING_RAW}")
print(f"LOG: Total pages to process: {len(urls)}")

download_count = 0
skipped_count = 0
error_count = 0

for idx, url in enumerate(urls, 1):
    try:
        print(f"\nLOG: [{idx}/{len(urls)}] Processing URL: {url}")
        
        # Generate filename from URL
        path_parts = urlparse(url).path.strip('/').split('/')
        filename = path_parts[-1] if path_parts else 'index'
        filename = re.sub(r'[^\w\-]', '_', filename)
        
        # Use numbered filename to maintain order
        numbered_filename = f"{str(idx).zfill(3)}_{filename}"
        
        html_file = RAW_DIR / f"{numbered_filename}.html"
        meta_file = RAW_DIR / f"{numbered_filename}.json"
        
        # Skip if exists
        if SKIP_EXISTING_RAW and html_file.exists():
            print(f"LOG: [{idx}/{len(urls)}] ⊘ Skipped (already exists): {html_file.name}")
            skipped_count += 1
            continue
        
        print(f"LOG: [{idx}/{len(urls)}] Downloading HTML from: {url}")
        
        # Download raw HTML using requests
        print(f"LOG:   Sending HTTP GET request...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"LOG:   ✓ Received response ({len(response.content)} bytes)")
        
        # Save raw HTML
        print(f"LOG:   Saving HTML to: {html_file.name}")
        html_file.write_text(response.text, encoding='utf-8')
        
        # Save metadata
        metadata = {
            'number': idx,
            'url': url,
            'downloaded_at': datetime.now().isoformat(),
            'filename': numbered_filename,
            'html_size_bytes': len(response.content),
            'status_code': response.status_code
        }
        meta_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
        print(f"LOG:   ✓ Saved metadata to: {meta_file.name}")
        
        print(f"LOG: [{idx}/{len(urls)}] ✓ SUCCESS: {html_file.name} ({len(response.content)} bytes)")
        download_count += 1
        
        # Rate limiting
        print(f"LOG:   Waiting 2 seconds (rate limiting)...")
        time.sleep(2)
        
    except Exception as e:
        print(f"LOG: [{idx}/{len(urls)}] ✗ ERROR: {str(e)}")
        error_count += 1

print(f"\nLOG: Download phase complete!")
print(f"LOG:   Downloaded: {download_count}")
print(f"LOG:   Skipped: {skipped_count}")
print(f"LOG:   Errors: {error_count}")

# ---------------- Step 3: Wait before processing ----------------

if PROCESS_CONTENT:
    print(f"\n[STEP 3] Waiting {WAIT_BEFORE_PROCESSING} seconds before starting post-processing...")
    for i in range(WAIT_BEFORE_PROCESSING, 0, -1):
        print(f"LOG: Waiting... {i} seconds remaining", end='\r')
        time.sleep(1)
    print(f"\nLOG: ✓ Wait complete, starting post-processing...")

# ---------------- Step 4: Process content (optional) ----------------

processed_count = 0
process_errors = 0

if PROCESS_CONTENT:
    print(f"\n[STEP 4] Processing raw HTML to markdown...")
    print(f"LOG: Processing all HTML files in: {RAW_DIR}")
    
    # Agent for content processing
    print(f"LOG: Initializing content processing agent...")
    content_agent = Agent(
        model=model,
        tools=[],  # No tools needed for processing
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
    
    processed_count = 0
    process_errors = 0
    
    # Get all HTML files sorted by name (maintains numbering order)
    html_files = sorted(RAW_DIR.glob("*.html"))
    print(f"LOG: Found {len(html_files)} HTML files to process")
    
    for html_file in html_files:
        try:
            print(f"\nLOG: Processing: {html_file.name}")
            
            # Load raw HTML
            print(f"LOG:   Loading HTML content...")
            html_content = html_file.read_text(encoding='utf-8')
            print(f"LOG:   ✓ Loaded {len(html_content)} characters")
            
            # Load metadata
            meta_file = RAW_DIR / f"{html_file.stem}.json"
            metadata = {}
            if meta_file.exists():
                print(f"LOG:   Loading metadata...")
                metadata = json.loads(meta_file.read_text(encoding='utf-8'))
                print(f"LOG:   ✓ Loaded metadata")
            
            # Parse HTML with BeautifulSoup to extract text
            print(f"LOG:   Parsing HTML with BeautifulSoup...")
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract main content (adjust selector as needed)
            main_content = soup.get_text(separator='\n', strip=True)
            print(f"LOG:   ✓ Extracted text content ({len(main_content)} characters)")
            
            # Process with agent (limit size to avoid token issues)
            print(f"LOG:   Processing with AI agent...")
            content_to_process = main_content[:8000]  # Limit to avoid token issues
            response = content_agent.run(
                f"Convert this webpage text to clean markdown:\n\n{content_to_process}"
            )
            print(f"LOG:   ✓ AI processing complete")
            
            # Add frontmatter with source information
            frontmatter = "---\n"
            frontmatter += f"number: {metadata.get('number', 'unknown')}\n"
            frontmatter += f"source_url: {metadata.get('url', 'unknown')}\n"
            frontmatter += f"downloaded_at: {metadata.get('downloaded_at', 'unknown')}\n"
            frontmatter += f"processed_at: {datetime.now().isoformat()}\n"
            frontmatter += "---\n\n"
            
            # Combine frontmatter with processed content
            final_content = frontmatter + response.content
            
            # Save processed content
            md_file = PROCESSED_DIR / f"{html_file.stem}.md"
            print(f"LOG:   Saving markdown to: {md_file.name}")
            md_file.write_text(final_content, encoding='utf-8')
            
            # Extract title from the processed content
            document_title = "Untitled"
            lines = final_content.split('\n')
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
            
            print(f"LOG:   ✓ Extracted title: '{document_title}'")
            
            # Update JSON metadata with markdown info
            print(f"LOG:   Updating JSON metadata...")
            metadata['mdfilename'] = md_file.name
            metadata['documentTitle'] = document_title
            meta_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            print(f"LOG:   ✓ Updated JSON metadata")
            
            print(f"LOG: ✓ SUCCESS: {md_file.name}")
            processed_count += 1
            
        except Exception as e:
            print(f"LOG: ✗ ERROR processing {html_file.name}: {str(e)}")
            process_errors += 1
    
    print(f"\nLOG: Post-processing complete!")
    print(f"LOG:   Processed successfully: {processed_count}")
    print(f"LOG:   Errors: {process_errors}")

# ---------------- Step 5: Index to ChromaDB ----------------

indexed_count = 0
error_count = 0

if INDEX_TO_CHROMADB:
    print(f"\n[STEP 5] Indexing markdown files to ChromaDB...")
    print(f"LOG: Initializing ChromaDB...")
    
    try:
        # Initialize embedder
        print(f"LOG: Creating OllamaEmbedder (llama3.2:latest, 3072 dimensions)...")
        embeddings = OllamaEmbedder(
            id="llama3.2:latest", 
            host="http://localhost:11434",
            dimensions=3072, 
            timeout=60
        )
        print(f"LOG: ✓ Embedder initialized")
        
        # Initialize ChromaDB
        chroma_path = "tmp/chroma_retirement_glossary"
        print(f"LOG: Creating ChromaDB collection at: {chroma_path}")
        vector_db = ChromaDb(
            collection="irs_retirement_glossary",
            embedder=embeddings,
            persistent_client=True,
            path=chroma_path,
        )
        print(f"LOG: ✓ ChromaDB initialized")
        
        # Create Knowledge base with the vector database
        print(f"LOG: Creating Knowledge base...")
        knowledge = Knowledge(vector_db=vector_db)
        print(f"LOG: ✓ Knowledge base initialized")
        
        # Get all markdown files and their JSON metadata
        md_files = sorted(PROCESSED_DIR.glob("*.md"))
        print(f"LOG: Found {len(md_files)} markdown files to index")
        
        indexed_count = 0
        error_count = 0
        
        for md_file in md_files:
            try:
                print(f"\nLOG: Indexing: {md_file.name}")
                
                # Load markdown content
                print(f"LOG:   Loading markdown content...")
                md_content = md_file.read_text(encoding='utf-8')
                
                # Load corresponding JSON metadata
                json_file = RAW_DIR / f"{md_file.stem}.json"
                metadata = {}
                if json_file.exists():
                    print(f"LOG:   Loading JSON metadata...")
                    metadata = json.loads(json_file.read_text(encoding='utf-8'))
                    print(f"LOG:   ✓ Loaded metadata")
                else:
                    print(f"LOG:   ⚠ Warning: JSON metadata not found, using minimal metadata")
                
                # Parse frontmatter and extract content
                lines = md_content.split('\n')
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
                
                # Get the clean content (without frontmatter)
                clean_content = '\n'.join(content_lines).strip()
                print(f"LOG:   ✓ Extracted content ({len(clean_content)} characters)")
                
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
                
                # Use knowledge.add_content() with file path (same pattern as working local_agent_local_llm.py)
                knowledge.add_content(
                    path=str(md_file),  # Pass the markdown file path directly
                    reader=TextReader(),  # Use TextReader for markdown/text files
                    metadata=doc_metadata,
                    skip_if_exists=True  # Skip files already indexed
                )
                
                print(f"LOG: ✓ SUCCESS: Indexed {md_file.name}")
                indexed_count += 1
                
                # Small delay to avoid overwhelming the embedding service
                time.sleep(0.5)
                
            except Exception as e:
                print(f"LOG: ✗ ERROR indexing {md_file.name}: {str(e)}")
                error_count += 1
        
        print(f"\nLOG: ChromaDB indexing complete!")
        print(f"LOG:   Indexed: {indexed_count}")
        print(f"LOG:   Errors: {error_count}")
        print(f"LOG:   Collection: irs_retirement_glossary")
        print(f"LOG:   Location: {Path(chroma_path).absolute()}")
        
        # Test the indexing with a sample query
        print(f"\n[TEST QUERY] Testing ChromaDB search functionality...")
        print(f"LOG: Running test query: 'What are 401k contribution limits?'")
        
        try:
            results = vector_db.search("What are 401k contribution limits?", limit=5)
            print(f"LOG: ✓ Query successful! Found {len(results)} results\n")
            
            for i, result in enumerate(results, 1):
                # Extract metadata and content
                meta = getattr(result, "metadata", {})
                content = getattr(result, "content", "") or ""
                
                print(f"--- RESULT {i} ---")
                print(f"Document: {meta.get('documentTitle', 'N/A')}")
                print(f"Source: {meta.get('source_url', 'N/A')}")
                print(f"Content preview: {content[:300]}...")
                print()
                
        except Exception as e:
            print(f"LOG: ✗ ERROR during test query: {str(e)}")
        
    except Exception as e:
        print(f"LOG: ✗ ERROR initializing ChromaDB: {str(e)}")

# ---------------- Summary ----------------

print(f"\n{'='*60}")
print(f"SCRAPING COMPLETE!")
print(f"{'='*60}")
print(f"Total URLs found: {len(urls)}")
print(f"\nDownload Phase:")
print(f"  Downloaded: {download_count}")
print(f"  Skipped (existing): {skipped_count}")
print(f"  Errors: {error_count}")
if PROCESS_CONTENT:
    print(f"\nProcessing Phase:")
    print(f"  Processed to markdown: {processed_count}")
    print(f"  Processing errors: {process_errors}")
if INDEX_TO_CHROMADB:
    print(f"\nChromaDB Indexing:")
    print(f"  Indexed: {indexed_count}")
    print(f"  Errors: {error_count}")
    print(f"  Collection: irs_retirement_glossary")
print(f"\nOutput directories:")
print(f"  Raw HTML: {RAW_DIR.absolute()}")
print(f"  Processed: {PROCESSED_DIR.absolute()}")
if INDEX_TO_CHROMADB:
    print(f"  ChromaDB: {Path('tmp/chroma_retirement_glossary').absolute()}")
print(f"\nConfiguration used:")
print(f"  SKIP_EXISTING_RAW: {SKIP_EXISTING_RAW}")
print(f"  PROCESS_CONTENT: {PROCESS_CONTENT}")
if PROCESS_CONTENT:
    print(f"  WAIT_BEFORE_PROCESSING: {WAIT_BEFORE_PROCESSING}s")
print(f"  INDEX_TO_CHROMADB: {INDEX_TO_CHROMADB}")
print(f"{'='*60}")