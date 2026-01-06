# Biotech Startup RAG System

A Retrieval-Augmented Generation (RAG) system for biotech startup documents using hybrid search (vector + lexical).

## Features

- **Intelligent Document Processing**: Automatically detects document type (meeting minutes, progress reports, research papers)
- **Smart Chunking**: Different chunking strategies optimized for each document type
  - Meeting Minutes: 300 token chunks (preserves action items and decisions)
  - Progress Reports: 500 token chunks (maintains task context)
  - Research Papers: 1000 token chunks with semantic awareness
- **Hybrid Search**: Combines vector embeddings (semantic) with BM25 (lexical) search
- **Metadata Extraction**: Automatically extracts and indexes document metadata
- **FastAPI Backend**: RESTful API for document processing and search
- **Streamlit Frontend**: Interactive web interface for search and document management

## Technology Stack

- **Vector Store**: Qdrant
- **Chunking**: Chonkie
- **Lexical Search**: BM25
- **Embeddings**: Sentence Transformers (BAAI/bge-small-en-v1.5)
- **Backend**: FastAPI
- **Frontend**: Streamlit
- **Package Manager**: UV

## Installation

### Prerequisites

- Python 3.10+
- Docker & Docker Compose (optional)
- UV package manager

### Local Setup

1. Clone the repository:
```bash
git clone <repo-url>
cd biotech-startup-rag
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Create `.env` file from example:
```bash
cp .env.example .env
```

4. Start Qdrant (using Docker):
```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

5. Run FastAPI backend:
```bash
uv run python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

6. Run Streamlit frontend (in another terminal):
```bash
uv run streamlit run app.py
```

### Docker Compose

To run everything together:
```bash
docker-compose up
```

Then access:
- Streamlit UI: http://localhost:8501
- FastAPI docs: http://localhost:8000/docs
- Qdrant: http://localhost:6333

## Usage

### API Endpoints

#### Search Documents
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "gene therapy progress",
    "top_k": 5,
    "doc_type": null
  }'
```

#### Upload Document
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@document.pdf"
```

#### Get Statistics
```bash
curl http://localhost:8000/stats
```

#### Batch Process Directory
```bash
curl -X POST "http://localhost:8000/upload-batch?directory=/path/to/docs"
```

#### Clear All Documents
```bash
curl -X DELETE http://localhost:8000/clear
```

### Python SDK

```python
from src.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Process a single document
pipeline.process_document("path/to/document.pdf")

# Search
results = pipeline.search("your query here", top_k=5)
for result in results:
    print(f"Score: {result['combined_score']:.3f}")
    print(f"Content: {result['content'][:200]}...")
    print(f"Metadata: {result['metadata']}")

# Get statistics
stats = pipeline.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Total chunks: {stats['total_chunks']}")
```

## Document Type Detection

The system automatically detects document types based on content patterns:

### Meeting Minutes
Patterns: "minutes of meeting", "attendees", "action items", "decisions"
- Small chunks (300 tokens)
- Section-aware parsing

### Progress Reports
Patterns: "progress report", "completed", "in progress", "milestones"
- Medium chunks (500 tokens)
- Task-aware context preservation

### Research Papers
Patterns: "abstract", "methodology", "results", "conclusion"
- Larger chunks (1000 tokens)
- Semantic awareness with overlap

## Chunking Strategies

Each document type uses an optimized chunking strategy:

1. **Meeting Minutes Chunker**: Groups content by sections (agenda, decisions, action items)
2. **Progress Report Chunker**: Parses by task status (completed, in-progress, upcoming)
3. **Research Paper Chunker**: Preserves paper structure (abstract, methodology, results, etc.)

## Hybrid Search

The system combines two search methods:

1. **Vector Search** (Semantic)
   - Uses BAAI/bge-small-en-v1.5 embeddings
   - Good for semantic similarity

2. **BM25 Lexical Search**
   - Good for exact term matching
   - Useful for specific keywords

Results are ranked using weighted scores:
- Vector weight: 0.5
- BM25 weight: 0.5

## Project Structure

```
biotech-startup-rag/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── document_loader.py     # Document loading & metadata extraction
│   ├── chunking.py            # Intelligent chunking strategies
│   ├── vector_store.py        # Qdrant integration & hybrid search
│   ├── rag_pipeline.py        # Main RAG orchestration
│   └── api.py                 # FastAPI backend
├── app.py                     # Streamlit frontend
├── pyproject.toml             # Project dependencies
├── docker-compose.yml         # Docker Compose setup
├── Dockerfile.api             # API Dockerfile
├── Dockerfile.streamlit       # Streamlit Dockerfile
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Configuration

Edit `.env` to customize:

```ini
# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Chunk sizes
CHUNK_SIZE_MEETING_MINUTES=300
CHUNK_SIZE_PROGRESS_REPORT=500
CHUNK_SIZE_RESEARCH_PAPER=1000

# API
API_HOST=0.0.0.0
API_PORT=8000

# Search
TOP_K=5
```

## Performance Tips

1. **Batch Processing**: Use the batch endpoint for multiple documents
2. **Chunk Size**: Adjust chunk sizes based on your document lengths
3. **Top-K**: Start with top_k=5, increase if needed
4. **Qdrant**: Scale Qdrant separately for production use

## Troubleshooting

### Qdrant Connection Error
Ensure Qdrant is running:
```bash
curl http://localhost:6333/health
```

### API Not Responding
Check if FastAPI is running:
```bash
curl http://localhost:8000/health
```

### Out of Memory
Reduce chunk sizes or process documents in smaller batches.

### Slow Search
- Increase top_k value for better results
- Consider using simpler embedding model
- Index fewer documents at a time

## Development

### Run Tests
```bash
uv run pytest tests/ -v
```

### Code Quality
```bash
uv run black src/
uv run ruff check src/
```

## License

MIT

## Contributing

Contributions welcome! Please:
1. Create a feature branch
2. Add tests
3. Submit a pull request

## Support

For issues or questions, please open an issue on GitHub.
