# Architecture Overview

## System Design

The Biotech Startup RAG system is built with a modular architecture that separates concerns across document processing, indexing, and retrieval layers.

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                        │
│         (Search UI, Upload, Statistics Dashboard)           │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  (API Endpoints, Request Handling, Response Formatting)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         ↓             ↓             ↓
    ┌────────┐  ┌────────────┐  ┌──────────┐
    │ Loader │  │  Chunker   │  │ Vector   │
    │        │→ │            │→ │ Store    │
    └────────┘  └────────────┘  └──────────┘
         ↓             ↓             ↓
    Documents   Smart Chunking   Qdrant +
    (PDF, DOCX)  (Type-aware)     BM25
         └─────────────┬───────────┘
                       ↓
        ┌──────────────────────────┐
        │   RAG Pipeline            │
        │   (Orchestration)         │
        └──────────────────────────┘
```

## Core Components

### 1. **Document Loader** (`document_loader.py`)
- Supports multiple formats: PDF, DOCX, TXT
- Extracts metadata (title, authors, dates, creation info)
- Auto-detects document type based on content patterns
- Handles encoding and PDF text extraction

**Key Classes:**
- `DocumentMetadata`: Stores extracted metadata
- `DocumentLoader`: Loads and processes documents

### 2. **Intelligent Chunking** (`chunking.py`)
- Document-type aware chunking strategies
- Preserves document structure and semantic meaning

**Strategy Details:**

#### Meeting Minutes Chunker
- **Chunk Size**: 300 tokens
- **Method**: Section-based (agenda, decisions, action items)
- **Goal**: Preserve decision context and action items
- **Parsing**: Groups by section headers and keywords

#### Progress Report Chunker
- **Chunk Size**: 500 tokens  
- **Method**: Task-status based (completed, in-progress, upcoming)
- **Goal**: Maintain task context and status information
- **Parsing**: Classifies content by task categories

#### Research Paper Chunker
- **Chunk Size**: 1000 tokens
- **Method**: Semantic with overlap
- **Goal**: Preserve experimental context and citations
- **Parsing**: Respects paper structure (abstract, methods, results, etc.)

### 3. **Vector Store** (`vector_store.py`)
- **Primary Store**: Qdrant (vector database)
- **Vector Model**: BAAI/bge-small-en-v1.5 (384-dim embeddings)
- **Lexical Index**: BM25 for exact term matching
- **Search Mode**: Hybrid (weighted combination)

**Hybrid Search Algorithm:**
1. Vector search using cosine similarity
2. BM25 lexical search on tokens
3. Combine results with weights: `0.5 * vector_score + 0.5 * bm25_score`
4. Rank and return top-k results

### 4. **RAG Pipeline** (`rag_pipeline.py`)
- Orchestrates the complete workflow
- Manages document processing pipeline
- Coordinates between components
- Tracks processing statistics

### 5. **FastAPI Backend** (`api.py`)
- RESTful API for all operations
- File upload handling with validation
- Batch processing support
- CORS enabled for frontend access

**Endpoints:**
- `POST /upload` - Upload single document
- `POST /upload-batch` - Process directory
- `POST /search` - Hybrid search with optional type filter
- `GET /stats` - System statistics
- `DELETE /clear` - Clear all documents
- `GET /health` - Health check

### 6. **Streamlit Frontend** (`app.py`)
- Interactive web interface
- Pages: Search, Upload, Statistics, Settings
- Real-time API integration
- Document visualization and metadata display

## Data Flow

### Document Processing Pipeline

```
Input Document
    ↓
[Document Loader]
    - Extract text content
    - Extract metadata (title, authors, dates)
    - Detect document type (heuristic-based)
    ↓
[Type Detection]
    - Pattern matching (keywords, sections)
    - Determine optimal chunking strategy
    ↓
[Intelligent Chunker]
    - Apply document-type specific chunking
    - Preserve structural information
    - Add metadata to chunks
    ↓
[Embedding Generation]
    - Generate vector embeddings
    - BAAI/bge-small-en-v1.5 model
    - 384-dimensional vectors
    ↓
[Vector Store]
    - Index in Qdrant
    - Update BM25 index
    - Store with metadata payload
    ↓
Output: Indexed & Searchable
```

### Search Pipeline

```
Search Query
    ↓
[Query Processing]
    ↓
[Parallel Search]
    ├→ Vector Search (Qdrant)
    │   - Embed query
    │   - Cosine similarity search
    │
    └→ BM25 Search
        - Tokenize query
        - Term-based ranking
    ↓
[Result Merging]
    - Combine results
    - Apply weights
    - Re-rank by combined score
    ↓
[Optional Filtering]
    - Filter by doc_type if specified
    - Limit to top-k results
    ↓
Output: Ranked Results with Scores
```

## Metadata Schema

Each chunk is indexed with metadata for filtering and context:

```python
{
    "content": "chunk text",
    "metadata": {
        "doc_type": "meeting_minutes|progress_report|research_paper|general",
        "chunk_type": "structured_section|task_based|semantic|default",
        "source_file": "path/to/file.pdf",
        "section": "Agenda|Results|Completed Tasks|etc",
        "task_type": "completed|in_progress|upcoming|etc",  # for progress reports
        "title": "document title",
        "created_date": "2024-01-15",
        "authors": ["author1", "author2"],
        "page_number": 5  # for PDFs
    }
}
```

## Technology Choices

### Document Processing
- **PyPDF2**: PDF text extraction with metadata support
- **python-docx**: DOCX document handling
- **Chonkie**: Intelligent text chunking

### Vector Search
- **Qdrant**: High-performance vector database with HTTP API
- **Sentence Transformers**: Generate embeddings locally
- **BAAI/bge-small-en-v1.5**: Efficient (~100MB) with good quality

### Lexical Search
- **rank-bm25**: Pure Python BM25 implementation

### Backend
- **FastAPI**: Modern, type-safe, auto-documented API
- **Pydantic**: Data validation and settings management

### Frontend
- **Streamlit**: Rapid development of data applications
- **httpx**: Async HTTP client for API calls
- **Plotly**: Interactive charts

### Infrastructure
- **Qdrant**: Containerized vector database
- **Docker/Docker Compose**: Container orchestration
- **UV**: Fast Python package manager

## Performance Characteristics

### Indexing
- **Document Processing**: ~100 docs/hour (depends on size)
- **Chunk Creation**: Varies by type (300-1000 token chunks)
- **Embedding Generation**: ~50-100 chunks/second
- **Qdrant Indexing**: Real-time (< 1 second per batch)

### Search
- **Vector Search**: O(log n) approximate, ~50-100ms
- **BM25 Search**: O(n log m) worst case, ~10-50ms
- **Result Merging**: O(k log k), negligible
- **Total Latency**: ~100-200ms typical

## Scaling Considerations

### Horizontal Scaling
1. **Multiple API Instances**: Run multiple FastAPI instances behind load balancer
2. **Qdrant Clustering**: Deploy Qdrant in cluster mode
3. **Caching Layer**: Add Redis for frequently accessed queries

### Vertical Scaling
1. **Larger Embeddings**: Switch to larger dimension models
2. **GPU Acceleration**: Use CUDA for embedding generation
3. **Batch Processing**: Process documents in optimized batches

### Storage
- **Qdrant Snapshots**: Regular backups via API
- **Persistent Storage**: Use Docker volumes or S3

## Security Considerations

### Current State (Development)
- No authentication (CORS open)
- No input validation on file types
- API accessible on all interfaces

### Production Recommendations
1. **Authentication**: Add OAuth2 or API key validation
2. **Input Validation**: Strict file type and size checks
3. **Rate Limiting**: Implement per-user rate limits
4. **Encryption**: TLS for all endpoints, encrypt at rest
5. **Access Control**: Role-based access control (RBAC)
6. **Audit Logging**: Track all API operations
7. **Data Privacy**: HIPAA compliance for biotech data

## Monitoring & Observability

### Current Implementation
- Basic health checks via API
- Statistics endpoint for system state
- Processing logs to stdout

### Recommended Additions
1. **Metrics**: Prometheus metrics for indexing/search latency
2. **Logging**: Structured logging with timestamps
3. **Tracing**: Distributed tracing for request flows
4. **Alerts**: Setup for critical failures
5. **Dashboards**: Grafana dashboards for operations

## Error Handling

### Document Processing
- Invalid file types: HTTP 400
- File read errors: HTTP 500 with error details
- Chunking errors: Logged and processed continues
- Metadata extraction failures: Gracefully handled

### Search
- Empty queries: HTTP 400
- API connectivity: HTTP 500
- No results: Empty result set (not error)

## Future Enhancements

1. **Multi-Language Support**: Handle documents in multiple languages
2. **Advanced Filtering**: Date range, author-based filtering
3. **Semantic Search**: Use different embedding models
4. **Entity Extraction**: Automatic extraction of key entities (proteins, dates)
5. **Citation Tracking**: Track citations across documents
6. **Version Control**: Track changes to documents
7. **Generative QA**: Integrate with LLMs for question answering
8. **Fine-tuned Models**: Train on biotech corpus
