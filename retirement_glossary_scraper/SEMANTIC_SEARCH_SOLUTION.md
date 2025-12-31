# Semantic Search Problem & Solutions

## Problem Summary

**Issue**: Acronym queries like "EACA" fail to find Document #17 which contains "Eligible Automatic Contribution Arrangement (EACA)" even though the document exists and is properly indexed.

**Root Cause**: Pure semantic embeddings (vector similarity) struggle to match acronyms to their full term expansions. The semantic distance between "EACA" and "Eligible Automatic Contribution Arrangement" is too large in the embedding space, causing relevant documents to not appear in top results.

**Evidence**:
- Search for "automatic enrollment" → Document #17 appears (✓)
- Search for "automatic contribution" → Document #17 appears (✓)  
- Search for "EACA" → Document #17 does NOT appear (✗)
- Search for "Eligible Automatic Contribution Arrangement" → Document #17 does NOT appear (✗)

This occurs with both embedding models tested:
- llama3.2:latest (3072 dimensions)
- nomic-embed-text:latest (768 dimensions)

---

## Implemented Solutions

### ✓ Solution 1: Query Expansion (Runtime)
**Location**: `src/query_agent_tools.py`

**Implementation**:
```python
RETIREMENT_ACRONYMS = {
    'EACA': 'Eligible Automatic Contribution Arrangement',
    'QACA': 'Qualified Automatic Contribution Arrangement',
    'RMD': 'Required Minimum Distribution',
    'IRA': 'Individual Retirement Arrangement',
    # ... more acronyms
}

def expand_query(query: str) -> str:
    """Expand known acronyms in query for better semantic matching"""
    words = query.upper().split()
    expanded_terms = []
    
    for word in words:
        clean_word = word.strip('?.,!').upper()
        if clean_word in RETIREMENT_ACRONYMS:
            expanded_terms.append(f"{clean_word} {RETIREMENT_ACRONYMS[clean_word]}")
        else:
            expanded_terms.append(word)
    
    return ' '.join(expanded_terms)
```

**How it works**: Transforms "What is EACA?" → "WHAT IS EACA Eligible Automatic Contribution Arrangement" before searching

**Pros**:
- Zero latency (dictionary lookup)
- No external dependencies
- Works immediately without re-indexing
- Easy to maintain and update acronym list

**Cons**:
- Requires manual acronym dictionary maintenance
- Only works for known acronyms
- Still relies on semantic matching with expanded query

**Status**: ✓ Implemented and working, but insufficient alone

---

### ✓ Solution 2: Content Augmentation (Indexing)
**Location**: `src/indexer.py`

**Implementation**:
```python
def extract_acronyms(text: str) -> dict:
    """Extract acronyms from patterns like 'Full Term Name (ACRONYM)'"""
    pattern = r'([A-Z][A-Za-z\s&-]+?)\s*\(([A-Z]{2,})\)'
    acronyms = {}
    for match in re.finditer(pattern, text):
        full_term = match.group(1).strip()
        acronym = match.group(2)
        acronyms[acronym] = full_term
    return acronyms

def augment_content_with_acronyms(content: str) -> str:
    """Add searchable acronym section to content"""
    acronyms = extract_acronyms(content)
    
    if not acronyms:
        return content
    
    augmented = content + "\n\n## Document Acronyms:\n"
    for acronym, expansion in acronyms.items():
        augmented += f"{acronym} stands for {expansion}. "
        augmented += f"{expansion} is abbreviated as {acronym}. "
    
    return augmented
```

**How it works**: During indexing, automatically detects acronyms in documents and appends explicit mappings like "EACA stands for Eligible Automatic Contribution Arrangement" to make them semantically searchable

**Pros**:
- Automatic extraction (no manual work per document)
- Makes acronym-term relationships explicit for embeddings
- Uses only Python stdlib (regex)
- Scales to any number of documents

**Cons**:
- Requires re-indexing when implemented
- Pattern matching may miss some acronym formats
- Still depends on semantic similarity after augmentation

**Status**: ✓ Implemented and working, but insufficient alone

---

## Why Implemented Solutions Are Insufficient

**Combined Impact**: Query expansion + content augmentation improve the situation but **do not fully solve the problem** because:

1. **Semantic Embeddings Fundamental Limitation**: Even with "EACA Eligible Automatic Contribution Arrangement" as the query and explicit acronym mappings in documents, the embedding vectors for these terms are not semantically close enough in vector space

2. **No Exact Match Component**: Pure vector similarity search has no concept of exact keyword matching - it only ranks by semantic similarity

3. **Vector Space Geometry**: Acronyms and their expansions occupy different regions of embedding space, requiring additional bridging mechanisms beyond just including both terms

---

## Additional Solutions Required

### Solution 3: Hybrid Search (Keyword + Semantic)
**Status**: ❌ Not implemented (requires external library or custom implementation)

**Approach**: Combine BM25 keyword search with semantic search and merge results using Reciprocal Rank Fusion (RRF)

**Implementation Plan**:
```python
# Install: pip install rank-bm25
from rank_bm25 import BM25Okapi

class HybridSearchIndexer:
    def __init__(self):
        self.vector_db = ChromaDb(...)  # Existing
        self.bm25_index = None  # New
        self.documents = []  # New
        
    def index_documents(self):
        # Index to ChromaDB (existing)
        self.vector_db.add_documents(documents)
        
        # Build BM25 index (new)
        tokenized_docs = [doc.split() for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)
        self.documents = documents
        
    def hybrid_search(self, query: str, limit: int = 5):
        # Semantic search
        semantic_results = self.vector_db.search(query, limit=20)
        
        # Keyword search
        tokenized_query = query.split()
        bm25_scores = self.bm25_index.get_scores(tokenized_query)
        keyword_results = get_top_k(bm25_scores, k=20)
        
        # Merge using RRF
        merged = reciprocal_rank_fusion(
            semantic_results, 
            keyword_results, 
            k=60
        )
        
        return merged[:limit]
```

**Pros**:
- Keyword matching catches exact acronym matches
- Semantic search handles conceptual queries
- Best of both worlds

**Cons**:
- Requires BM25 library (rank-bm25)
- More complex indexing pipeline
- Slightly slower search (2 searches + merge)

**Scalability**: ✓ Excellent - BM25 is fast and memory-efficient

---

### Solution 4: Metadata Filtering
**Status**: ❌ Not implemented

**Approach**: Store extracted acronyms in ChromaDB metadata and use pre-filtering before semantic search

**Implementation Plan**:
```python
# During indexing
acronyms = extract_acronyms(content)
document = Document(
    content=content,
    meta_data={
        'number': doc_number,
        'title': title,
        'acronyms': ','.join(acronyms.keys()),  # Store: "EACA,QACA,RMD"
    }
)

# During search
def search_with_acronym_filter(query: str):
    # Check if query contains known acronym
    query_upper = query.upper()
    matching_acronym = None
    for acronym in RETIREMENT_ACRONYMS:
        if acronym in query_upper:
            matching_acronym = acronym
            break
    
    if matching_acronym:
        # Use metadata filter to pre-select documents
        results = vector_db.search(
            query=expand_query(query),
            filters={"acronyms": {"$contains": matching_acronym}},
            limit=5
        )
    else:
        # Normal semantic search
        results = vector_db.search(query, limit=5)
    
    return results
```

**Pros**:
- Uses existing ChromaDB features
- Fast pre-filtering before semantic search
- No external dependencies

**Cons**:
- Still requires semantic ranking after filtering
- Depends on regex pattern matching during indexing
- Only works for detected acronyms

**Scalability**: ✓ Excellent - metadata filtering is very fast

---

### Solution 5: Custom Chunking Strategy
**Status**: ❌ Not implemented

**Approach**: Ensure acronym definitions stay together in chunks and create overlapping chunks around acronyms

**Implementation Plan**:
```python
def smart_chunk_with_acronyms(content: str, chunk_size: int = 1000):
    """Create chunks ensuring acronym definitions aren't split"""
    
    # Find all acronym positions
    acronym_pattern = r'([A-Z][A-Za-z\s&-]+?)\s*\(([A-Z]{2,})\)'
    acronym_positions = [(m.start(), m.end()) for m in re.finditer(acronym_pattern, content)]
    
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + chunk_size
        
        # Check if we're splitting an acronym definition
        for acro_start, acro_end in acronym_positions:
            if start < acro_start < end < acro_end:
                # Extend chunk to include full acronym definition
                end = acro_end + 200  # Include context after
                break
        
        chunks.append(content[start:end])
        
        # Create overlap for context
        start = end - 100
    
    return chunks
```

**Pros**:
- Ensures complete acronym context in each chunk
- Uses existing infrastructure
- No external dependencies

**Cons**:
- Complex chunking logic
- May create uneven chunk sizes
- Requires re-indexing

**Scalability**: ✓ Good - one-time overhead during indexing

---

### Solution 6: Acronym Synonym Table in ChromaDB
**Status**: ❌ Not implemented

**Approach**: Create a separate ChromaDB collection specifically for acronym lookups

**Implementation Plan**:
```python
# Create acronym collection
acronym_db = ChromaDb(
    collection="acronym_mappings",
    embedder=OllamaEmbedder(...)
)

# Index acronym mappings
for acronym, expansion in RETIREMENT_ACRONYMS.items():
    acronym_db.add(Document(
        content=f"{acronym} means {expansion}. {expansion} abbreviated as {acronym}.",
        meta_data={'acronym': acronym, 'expansion': expansion}
    ))

# Search workflow
def smart_search(query: str):
    # First check if query is acronym-related
    acronym_results = acronym_db.search(query, limit=1)
    
    if acronym_results and has_high_confidence(acronym_results[0]):
        # Expand query with found acronym
        expansion = acronym_results[0].meta_data['expansion']
        enhanced_query = f"{query} {expansion}"
    else:
        enhanced_query = query
    
    # Search main collection
    return main_db.search(enhanced_query, limit=5)
```

**Pros**:
- Dedicated acronym resolution system
- Can be updated independently
- Improves over time with usage

**Cons**:
- Requires maintaining separate collection
- Additional search overhead
- More complex infrastructure

**Scalability**: ✓ Good - small acronym collection is fast to search

---

## Recommended Implementation Priority

### Immediate (Current Sprint)
**Maintain existing implementations**:
- ✓ Query expansion (already working)
- ✓ Content augmentation (already working)

### Short-term (Next Sprint) - RECOMMENDED
**Implement Solution 3: Hybrid Search (Keyword + Semantic)**

**Why**: This provides the most significant improvement with reasonable complexity
- Catches exact acronym matches via BM25
- Maintains semantic search quality for conceptual queries
- Industry-standard approach (used by Elasticsearch, Pinecone, etc.)
- Single external dependency (rank-bm25: ~100KB, pure Python)

**Implementation Steps**:
1. Add `rank-bm25` to dependencies
2. Modify `src/indexer.py` to build BM25 index alongside ChromaDB
3. Implement RRF merge function in `src/query_agent_tools.py`
4. Update `search_glossary()` to use hybrid search
5. Test and tune RRF weights (typically k=60 works well)

### Medium-term (Future Enhancement)
**Implement Solution 4: Metadata Filtering**
- Easy to add alongside hybrid search
- Provides fast path for acronym queries
- Uses existing ChromaDB capabilities

### Long-term (If Needed)
**Implement Solution 5: Custom Chunking**
- Only if hybrid search + metadata filtering are insufficient
- More complex but handles edge cases

---

## Success Metrics

After implementing hybrid search, we should see:

1. **Acronym Query Success Rate**: 
   - Before: EACA → 0% relevant (doc #17 not in top 5)
   - Target: EACA → 100% relevant (doc #17 in top 3)

2. **Semantic Query Quality Maintained**:
   - "What happens with automatic enrollment?" → Still returns relevant results
   - No degradation in non-acronym queries

3. **Search Latency**:
   - Before: ~2.4s (single semantic search)
   - Target: <4s (hybrid search with BM25 + semantic + RRF merge)

4. **Coverage**:
   - All known IRS retirement acronyms (EACA, QACA, RMD, IRA, SEP, SIMPLE, etc.) successfully resolve to correct documents

---

## Code Changes Required for Hybrid Search

### 1. Dependencies (`pyproject.toml`)
```toml
[project]
dependencies = [
    # ... existing dependencies
    "rank-bm25>=0.2.2",
]
```

### 2. Indexer Changes (`src/indexer.py`)
- Add BM25 index building after ChromaDB indexing
- Persist BM25 index to disk (pickle)
- Load BM25 index on startup

### 3. Search Changes (`src/query_agent_tools.py`)
- Implement RRF merge function
- Update `search_glossary()` to perform hybrid search
- Add configuration for BM25 weight vs semantic weight

### 4. Configuration (`src/config.py`)
```python
class ScraperConfig:
    # ... existing config
    
    # Hybrid search settings
    use_hybrid_search: bool = True
    bm25_weight: float = 0.3  # 30% BM25, 70% semantic
    rrf_k: int = 60  # RRF constant
```

---

## Alternative: If No External Dependencies Allowed

If adding `rank-bm25` is not acceptable, implement **Solution 4 (Metadata Filtering)** as the next best option:

**Pros**:
- Zero external dependencies
- Uses only existing Agno/ChromaDB features
- Still provides significant improvement for acronym queries

**Cons**:
- Less robust than full hybrid search
- Requires exact acronym match in query
- No fuzzy matching capability

---

## Testing Plan

### Test Cases for Validation:

1. **Acronym Queries** (High Priority):
   - "What is EACA?" → Should return doc #17
   - "What is QACA?" → Should return doc #17
   - "What is RMD?" → Should return RMD documents
   - "Explain SIMPLE IRA" → Should return SIMPLE IRA documents

2. **Natural Language Queries** (Must Not Regress):
   - "automatic enrollment 401k" → Should return enrollment documents
   - "required minimum distribution rules" → Should return RMD documents
   - "contribution limits for retirement" → Should return contribution documents

3. **Mixed Queries**:
   - "EACA vs QACA differences" → Should return doc #17
   - "RMD calculation worksheet" → Should return RMD worksheet documents

4. **Edge Cases**:
   - "eaca" (lowercase) → Should still work with query normalization
   - "E.A.C.A." (periods) → Should handle punctuation
   - "What does EACA stand for" → Should expand and find

---

## Conclusion

**Current Status**: 
- Query expansion and content augmentation are implemented and working
- They improve the situation but are insufficient due to semantic embedding limitations

**Recommended Next Step**: 
- Implement **Hybrid Search (BM25 + Semantic)** as it provides the best balance of:
  - Effectiveness (solves acronym problem)
  - Scalability (fast, efficient)
  - Maintainability (industry standard approach)
  - Dependencies (single small library)

**Fallback Option**: 
- If no external dependencies allowed → Metadata Filtering (Solution 4)

**Timeline Estimate**: 
- Hybrid Search implementation: 2-3 hours
- Testing and tuning: 1-2 hours
- Total: ~4-5 hours development time
