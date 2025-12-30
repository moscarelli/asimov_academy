"""
Query the IRS Retirement Topics ChromaDB - Semantic Search Only
"""
from pathlib import Path
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.chroma import ChromaDb

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.resolve()

# Configuration
CHROMA_PATH = str(PROJECT_ROOT / "tmp" / "chroma_retirement_glossary")
COLLECTION_NAME = "irs_retirement_glossary"

print("="*80)
print("IRS Retirement Topics - Semantic Search")
print("="*80)

# Initialize ChromaDB connection
print("\nInitializing ChromaDB connection...")
embeddings = OllamaEmbedder(
    id="llama3.2:latest", 
    host="http://localhost:11434",
    dimensions=3072, 
    timeout=60
)

vector_db = ChromaDb(
    collection=COLLECTION_NAME,
    embedder=embeddings,
    persistent_client=True,
    path=CHROMA_PATH,
)
print("✓ Connected to ChromaDB\n")

# Semantic Search Queries
queries = [
    "401k contribution limits",
    "Required minimum distributions",
    "Early withdrawal penalties"
]

for query in queries:
    print("="*80)
    print(f"QUERY: '{query}'")
    print("="*80)
    
    results = vector_db.search(query, limit=5)
    
    print(f"\nFound {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        meta = getattr(result, "metadata", {})
        content = getattr(result, "content", "")
        
        print(f"\n{'-'*80}")
        print(f"RESULT #{i}")
        print(f"{'-'*80}")
        
        # Show all metadata
        print("METADATA:")
        for key, value in meta.items():
            print(f"  {key:20s}: {value}")
        
        # Show full or substantial content
        print(f"\nMATCHED CONTENT ({len(content)} characters):")
        print("-" * 80)
        print(content)
        print("-" * 80)
    
    print("\n")

# Interactive mode
print("="*80)
print("INTERACTIVE SEARCH")
print("="*80)
print("Enter your search query (or 'quit' to exit)\n")

while True:
    try:
        user_query = input("Query: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye!")
            break
        
        if not user_query:
            continue
        
        print(f"\n{'='*80}")
        print(f"SEARCHING: '{user_query}'")
        print(f"{'='*80}\n")
        
        results = vector_db.search(user_query, limit=5)
        
        print(f"Found {len(results)} results:\n")
        
        for i, result in enumerate(results, 1):
            meta = getattr(result, "metadata", {})
            content = getattr(result, "content", "")
            
            print(f"\n{'-'*80}")
            print(f"RESULT #{i}")
            print(f"{'-'*80}")
            
            # Show all metadata
            print("METADATA:")
            for key, value in meta.items():
                print(f"  {key:20s}: {value}")
            
            # Show full content
            print(f"\nMATCHED CONTENT ({len(content)} characters):")
            print("-" * 80)
            print(content)
            print("-" * 80)
        
        print("\n")
            
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}\n")
