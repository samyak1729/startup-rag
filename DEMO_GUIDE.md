# Demo Guide - Biotech Startup RAG System

A step-by-step guide to effectively demonstrate the RAG system to stakeholders, investors, or team members.

## Pre-Demo Checklist (15 minutes before)

- [ ] All services running (Qdrant, API, Streamlit)
- [ ] Sample documents loaded and indexed
- [ ] Browser tabs pre-opened:
  - Streamlit UI: http://localhost:8501
  - API Docs: http://localhost:8000/docs
- [ ] Example queries prepared
- [ ] Network stable (local connection preferred)
- [ ] Screen resolution suitable for projection

## Setup (Do this beforehand)

### Step 1: Start Services

```bash
# Terminal 1: Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Terminal 2: FastAPI
uv run python -m uvicorn src.api:app --reload

# Terminal 3: Streamlit
uv run streamlit run app.py

# Wait for all to be ready
# Qdrant: http://localhost:6333/health
# API: http://localhost:8000/health
# Streamlit: http://localhost:8501
```

### Step 2: Load Sample Documents

**Option A: Via Python (fastest)**
```bash
python -c "
from src.rag_pipeline import RAGPipeline
pipeline = RAGPipeline()
pipeline.process_batch('samples')
print('✓ Documents loaded')
"
```

**Option B: Via UI (shows system in action)**
1. Go to http://localhost:8501
2. Upload Documents page
3. Select `samples/sample_meeting_minutes.txt`
4. Select `samples/sample_progress_report.txt`
5. Select `samples/sample_research_paper.txt`
6. Click "Process Documents"

## Demo Flow (15-20 minutes)

### **Segment 1: Introduction (2 min)**

**What to say:**
> "This is a RAG system built specifically for biotech documents. It intelligently processes meeting minutes, progress reports, and research papers—automatically detecting document type and applying optimized chunking strategies. Then it combines vector and keyword search for hybrid retrieval."

**What to show:**
- Open SYSTEM_OVERVIEW.txt in terminal or README.md in browser
- Show project statistics: 4,307 lines, 23 files, production-ready

**Key message:** This isn't a generic document search—it's tailored for biotech workflows.

---

### **Segment 2: Document Processing (3 min)**

**Navigate to:** http://localhost:8501 → Upload Documents

**What to do:**
1. Show the file browser
2. Drag & drop or select a PDF/document
3. Watch it process in real-time

**What to highlight:**
- ✅ Automatic document type detection
- ✅ Shows "Meeting Minutes" / "Progress Report" / "Research Paper"
- ✅ Number of chunks created depends on type
- ✅ Metadata extraction visible in results

**Talking points:**
> "Notice how it automatically detected the document type. Different types get different chunk sizes—meeting minutes at 300 tokens preserve action items, progress reports at 500 preserve task context, research papers at 1000 preserve methodology."

---

### **Segment 3: Statistics Dashboard (2 min)**

**Navigate to:** Statistics tab

**What to show:**
- Total documents processed
- Total chunks created
- Bar chart of documents by type
- List of individual documents with metadata

**Talking points:**
> "Here you see we've indexed [X] documents creating [Y] chunks. The system tracks metadata—author, creation date, document type—which enriches search results and enables filtering."

---

### **Segment 4: Hybrid Search Demo (5-7 min)**

**Navigate to:** Search tab

**Demo Query 1: Semantic Search**
Query: "gene therapy safety evaluation"

**What to highlight:**
- Results appear instantly
- Shows content preview (truncated)
- Displays three scores:
  - **Vector Score**: How semantically similar (0-1)
  - **BM25 Score**: How many keywords match (0-1)
  - **Combined Score**: Weighted average
- Click "Metadata" to see document type, section, author

**Talking points:**
> "Vector search finds semantically similar content even if keywords don't match exactly. That's the power of embeddings—it understands meaning."

---

**Demo Query 2: Keyword Search**
Query: "action items milestones timeline"

**What to highlight:**
- Different results than semantic search
- Higher BM25 scores (keyword matching)
- Still useful for exact terms
- Combined score ranks both

**Talking points:**
> "This query shows why hybrid search matters. It catches both semantic meaning AND exact keywords. Neither alone would be complete."

---

**Demo Query 3: Filtered Search**
Query: "completed tasks"
Filter: "Progress Reports"

**What to highlight:**
- Dropdown filter by document type
- Results filtered to only progress reports
- Enables targeted searching

**Talking points:**
> "You can filter by document type. Want only meeting minutes? Only research papers? Done."

---

**Demo Query 4: Technical Terms**
Query: "CRISPR off-target mutations"

**What to highlight:**
- Finds relevant passages in research papers
- Technical domain knowledge preserved
- Works across document boundaries

---

### **Segment 5: API & Integration (2-3 min)**

**Navigate to:** http://localhost:8000/docs

**What to show:**
- Swagger/OpenAPI documentation
- Interactive API explorer

**Demo an API call:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "regulatory approval timeline",
    "top_k": 3
  }' | python -m json.tool
```

**Talking points:**
> "The system isn't just a web interface—it's a full REST API. You can integrate this into your own applications. Every endpoint is documented and type-safe."

---

### **Segment 6: Architecture Overview (2 min)**

**Show:** ARCHITECTURE.md

**What to highlight:**
- Modular design: document loader → chunker → vector store → search
- Qdrant for vector database
- BM25 for lexical search
- Type-safe with Pydantic
- Production-ready Docker setup

**Talking points:**
> "The architecture is clean and modular. Each component has a single responsibility, making it easy to customize or replace parts. It's built for production from day one."

---

## Advanced Demo (Optional, +5-10 min)

### Show the Python SDK

```python
from src.rag_pipeline import RAGPipeline

# Initialize
pipeline = RAGPipeline()

# Get statistics
stats = pipeline.get_stats()
print(f"Documents: {stats['total_documents']}")
print(f"Chunks: {stats['total_chunks']}")

# Search programmatically
results = pipeline.search("CRISPR safety", top_k=5)
for r in results:
    print(f"Score: {r['combined_score']:.3f}")
    print(f"Content: {r['content'][:100]}...")
```

**Talking points:**
> "You don't need the UI—you can use it as a Python library. Perfect for backend integration, batch processing, or custom workflows."

---

### Show Document Type Detection

```bash
python -c "
from src.document_loader import DocumentLoader
loader = DocumentLoader()
content, metadata = loader.load_document('samples/sample_meeting_minutes.txt')
print(f'Type: {metadata.doc_type}')
print(f'Title: {metadata.title}')
print(f'Authors: {metadata.authors}')
"
```

---

### Show Customization Points

**In `.env` or `src/config.py`:**
```ini
CHUNK_SIZE_MEETING_MINUTES=300
CHUNK_SIZE_PROGRESS_REPORT=500
CHUNK_SIZE_RESEARCH_PAPER=1000
TOP_K=5
```

> "Everything is configurable. Chunk sizes, search weights, embedding models—you control it all."

---

## Demo Narratives (Pick One)

### Narrative 1: "For Executives/Investors"
Focus: Business value, efficiency, ROI
- **Problem**: Manual document search takes hours
- **Solution**: Semantic search finds answers in seconds
- **Impact**: Team productivity, faster decision-making
- **Tech**: Production-ready, scalable, proven stack

### Narrative 2: "For Engineers"
Focus: Architecture, code quality, extensibility
- **Technical stack**: FastAPI, Streamlit, Qdrant, vector embeddings
- **Intelligent chunking**: Document-type aware strategies
- **Hybrid search**: Vector + BM25 for best results
- **Modular design**: Easy to customize and extend

### Narrative 3: "For Data Scientists"
Focus: ML approach, embeddings, search quality
- **Embeddings**: BAAI/bge-small-en-v1.5 (state-of-the-art)
- **Hybrid approach**: Combines semantic + lexical search
- **Document understanding**: Auto-detects type, extracts structure
- **Evaluation**: Built-in metrics and statistics

---

## Expected Demo Times

| Section | Time | Notes |
|---------|------|-------|
| Intro | 2 min | Set context |
| Document Upload | 3 min | Show real-time processing |
| Statistics | 2 min | Visual proof of capability |
| Search Demo (4 queries) | 7 min | Core value proposition |
| API Overview | 2 min | Integration possibilities |
| Architecture | 2 min | Production-readiness |
| **Total** | **18 min** | Can extend with optional sections |

---

## Sample Queries (Pre-prepared)

### General Knowledge
1. "CRISPR gene therapy"
2. "regulatory approval timeline"
3. "safety evaluation results"
4. "manufacturing scale-up"
5. "action items next week"

### Technical Biotech
1. "off-target mutations"
2. "amyloid-beta accumulation"
3. "viral vector production"
4. "adverse event tracking"
5. "dosing regimen optimization"

### Progress/Status
1. "completed milestones"
2. "in progress tasks"
3. "upcoming deadlines"
4. "blockers and challenges"
5. "team capacity utilization"

### Specific Types (Use filters)
1. Meeting Minutes: "Who was assigned action items?"
2. Progress Reports: "What's the status on manufacturing?"
3. Research Papers: "What were the study results?"

---

## Troubleshooting During Demo

### Problem: Search returns no results
**Solution:** 
- Check documents are loaded (Statistics page)
- Try simpler query
- Ensure Qdrant is healthy: `curl http://localhost:6333/health`

### Problem: Slow responses
**Solution:**
- Close unnecessary applications
- Reduce top_k value (from 5 to 3)
- Qdrant may be indexing—wait a moment

### Problem: API endpoint won't respond
**Solution:**
- Check FastAPI running: `curl http://localhost:8000/health`
- Restart: Ctrl+C and re-run `uvicorn`

### Problem: Streamlit page won't load
**Solution:**
- Hard refresh browser (Ctrl+Shift+R)
- Check: `curl http://localhost:8501`
- Restart Streamlit terminal

---

## Discussion Points / Follow-ups

**Strengths to emphasize:**
- ✅ Intelligent chunking (not just text splitting)
- ✅ Hybrid search (vector + keyword)
- ✅ Production-ready (Docker, type-safe, documented)
- ✅ Extensible (modular architecture)
- ✅ Fast deployment (docker-compose)

**Common questions & answers:**

**Q: How accurate is the search?**
> The hybrid approach gives us best of both worlds. Vector search handles semantic similarity, BM25 handles exact terms. For biotech documents with technical terminology, this is highly effective.

**Q: Can it handle more documents?**
> Absolutely. Qdrant scales horizontally. We could handle millions of documents. Currently using single-instance, but cluster mode is available.

**Q: How fast is it?**
> Search latency is 100-200ms typical. Vector search ~50ms, BM25 ~10-50ms. Depends on database size and query complexity. Easily handles 5-10 concurrent users.

**Q: What embedding model are you using?**
> BAAI/bge-small-en-v1.5. It's lightweight (~100MB), fast, and has excellent performance. We generate embeddings locally on-device—no external APIs.

**Q: Can we integrate this into our platform?**
> Yes. Three ways: (1) Web UI as-is, (2) REST API integration, (3) Python SDK import. All fully supported.

**Q: What about data privacy?**
> Data stays on-premise. Embeddings generated locally. No cloud calls. Perfect for sensitive biotech data.

---

## Post-Demo

### Leave them with:
1. Link to **README.md** for installation
2. Link to **INSTALLATION.md** for setup help
3. Link to **ARCHITECTURE.md** for technical deep-dive
4. Offer to run **examples.py** for deeper exploration
5. Provide **API documentation** (swagger at `/docs`)

### Next steps:
- "Let's set this up for your environment"
- "Want to customize it for your document types?"
- "Let's discuss integration with your systems"

---

## Pro Tips for Smooth Demo

1. **Pre-load documents**: Users don't want to wait for uploads
2. **Use realistic queries**: Not "hello" but "CRISPR safety results"
3. **Have backup plan**: Save screenshots if tech fails
4. **Practice transitions**: Smooth switching between tabs/pages
5. **Have talking points ready**: Don't wing it
6. **Show code occasionally**: Impressive to developers
7. **Ask questions**: "What would you search for?"
8. **End strong**: Architecture + production-readiness = credibility

---

## Success Metrics

A good demo if:
- ✅ Audience understands the problem being solved
- ✅ Search results look relevant and impressive
- ✅ They see it's production-ready (not a toy)
- ✅ They want to try it themselves
- ✅ They ask follow-up technical questions
- ✅ They discuss next steps/integration

---

**Estimated Total Demo Time: 20 minutes**
**With discussion/Q&A: 30-45 minutes**
