# Biotech Startup RAG System - Complete Index

## 📊 Project Overview

A production-ready Retrieval-Augmented Generation (RAG) system for biotech startup documents with intelligent chunking, hybrid search (vector + BM25), and a modern full-stack architecture.

**Lines of Code**: 4,307  
**Files**: 23  
**Languages**: Python, YAML, Markdown  
**Status**: Production Ready  

## 📁 File Structure

### Documentation (1,674 lines)

| File | Lines | Purpose |
|------|-------|---------|
| **README.md** | 281 | Project overview, features, installation, usage guide |
| **INSTALLATION.md** | 507 | Detailed installation steps, troubleshooting, development setup |
| **ARCHITECTURE.md** | 304 | Technical design, data flow, components, scaling strategy |
| **DEPLOYMENT.md** | 500 | Production deployment on AWS/GCP/Azure, Kubernetes, CI/CD |
| **CAPABILITIES.md** | 360 | Complete feature list, performance specs, capabilities matrix |
| **PROJECT_SUMMARY.md** | 322 | Executive summary, key highlights, next steps |
| **INDEX.md** | This file | Navigation and file guide |

### Source Code (1,252 lines)

#### Core RAG Pipeline
| File | Lines | Purpose |
|------|-------|---------|
| **src/rag_pipeline.py** | 183 | Main orchestration, document processing workflow |
| **src/document_loader.py** | 167 | Document loading, format handling, metadata extraction |
| **src/chunking.py** | 239 | Intelligent chunking strategies by document type |
| **src/vector_store.py** | 258 | Qdrant integration, BM25 indexing, hybrid search |
| **src/config.py** | 30 | Configuration management with pydantic-settings |
| **src/__init__.py** | 9 | Package initialization |

#### API & Frontend
| File | Lines | Purpose |
|------|-------|---------|
| **src/api.py** | 218 | FastAPI backend, REST endpoints, data models |
| **app.py** | 305 | Streamlit frontend, multi-page UI, real-time search |

#### Examples & Utilities
| File | Lines | Purpose |
|------|-------|---------|
| **examples.py** | 187 | 7 comprehensive usage examples |
| **scripts/quick_start.sh** | Shell script | Automated setup and environment validation |

### Configuration (88 lines)

| File | Lines | Purpose |
|------|-------|---------|
| **pyproject.toml** | 40 | Project metadata, dependencies, build config |
| **docker-compose.yml** | 48 | Multi-container orchestration for all services |

### Dockerfiles (34 lines)

| File | Lines | Purpose |
|------|-------|---------|
| **Dockerfile.api** | 19 | Container image for FastAPI backend |
| **Dockerfile.streamlit** | 15 | Container image for Streamlit frontend |

### Sample Data (315 lines)

| File | Lines | Document Type |
|------|-------|---|
| **samples/sample_meeting_minutes.txt** | 49 | Meeting Minutes (January 2024) |
| **samples/sample_progress_report.txt** | 155 | Progress Report (Weekly Status) |
| **samples/sample_research_paper.txt** | 111 | Research Paper (CRISPR Gene Therapy) |

### Configuration Files

| File | Purpose |
|------|---------|
| **.env.example** | Environment variables template |
| **.gitignore** | Git ignore rules |

## 🎯 Quick Navigation

### I Want To...

#### Get Started
1. Start here: **README.md** (5 min read)
2. Install: **INSTALLATION.md** (10 min setup)
3. Try examples: **examples.py** (5 min run)
4. Explore UI: http://localhost:8501 (2 min)

#### Understand the System
1. Architecture: **ARCHITECTURE.md** (15 min read)
2. Component details: See source code modules
3. Data flow: ARCHITECTURE.md diagrams

#### Deploy to Production
1. Overview: **DEPLOYMENT.md** (20 min read)
2. Choose platform: AWS/GCP/Azure/Kubernetes section
3. Configure: Use templates provided
4. Monitor: Health checks and logging setup

#### Search & Process Documents
1. API Reference: **src/api.py** docstrings
2. Python SDK: **examples.py**
3. UI Guide: **app.py** for features
4. Performance: **CAPABILITIES.md**

#### Extend & Customize
1. Understand chunking: **src/chunking.py**
2. Modify document detection: **src/document_loader.py**
3. Add new endpoints: **src/api.py**
4. Customize UI: **app.py**

### Document Processing Flow

```
Your Documents
    ↓
[1] Document Loader (src/document_loader.py)
    - Reads PDF/DOCX/TXT
    - Extracts metadata
    - Detects document type
    ↓
[2] Intelligent Chunker (src/chunking.py)
    - Applies optimal chunking strategy
    - Preserves document structure
    - Extracts section info
    ↓
[3] Vector Store (src/vector_store.py)
    - Generates embeddings
    - Indexes in Qdrant
    - Updates BM25 index
    ↓
[4] RAG Pipeline (src/rag_pipeline.py)
    - Orchestrates above steps
    - Tracks statistics
    - Manages workflow
    ↓
Searchable & Indexed
```

### API Endpoints

| Method | Endpoint | Handler | Purpose |
|--------|----------|---------|---------|
| POST | /upload | `upload_document()` | Upload single document |
| POST | /upload-batch | `upload_batch()` | Process directory |
| POST | /search | `search_documents()` | Search with hybrid search |
| GET | /stats | `get_stats()` | Get system statistics |
| DELETE | /clear | `clear_documents()` | Clear all documents |
| GET | /health | `health_check()` | Health status |

### Frontend Pages

| Page | File | Features |
|------|------|----------|
| 🔍 Search | app.py:75-120 | Query, filter by type, view results |
| 📤 Upload | app.py:121-175 | Upload documents, progress tracking |
| 📊 Statistics | app.py:176-230 | Metrics, charts, document list |
| ⚙️ Settings | app.py:231-280 | Configuration info, clear data |

## 🔧 Technology Stack

```
Frontend:        Streamlit (UI framework)
Backend:         FastAPI (REST API)
Vector DB:       Qdrant (vector search)
Embeddings:      Sentence Transformers (BAAI/bge-small-en-v1.5)
Lexical Search:  rank-bm25
Chunking:        Chonkie
Document Parse:  PyPDF2, python-docx
Containers:      Docker, Docker Compose
Package Mgr:     UV
Python:          3.10+
```

## 📊 Statistics

### Code Distribution
- **Documentation**: 40% (1,674 lines)
- **Source Code**: 30% (1,252 lines)
- **Sample Data**: 7% (315 lines)
- **Configuration**: 2% (88 lines)
- **Containers**: 1% (34 lines)

### Module Breakdown
- **Chunking Logic**: 239 lines
- **Vector Operations**: 258 lines
- **Document Processing**: 167 lines
- **API Handlers**: 218 lines
- **UI/Frontend**: 305 lines
- **Pipeline Orchestration**: 183 lines

### Features
- **Document Types Supported**: 4 (meeting minutes, progress reports, research papers, general)
- **API Endpoints**: 6 major endpoints
- **Frontend Pages**: 4 interactive pages
- **Search Methods**: 3 (vector, BM25, hybrid)
- **Supported Formats**: 3 (PDF, DOCX, TXT)

## 🚀 Getting Started (30 minutes)

### Step 1: Clone & Setup (5 min)
```bash
git clone <repo>
cd biotech-startup-rag
bash scripts/quick_start.sh
```

### Step 2: Start Services (5 min)
```bash
# Terminal 1
docker run -d -p 6333:6333 qdrant/qdrant

# Terminal 2
uv run python -m uvicorn src.api:app

# Terminal 3
uv run streamlit run app.py
```

### Step 3: Test System (5 min)
```bash
# Run examples
uv run python examples.py

# Or open browser
# http://localhost:8501
```

### Step 4: Load Sample Docs (5 min)
1. Go to http://localhost:8501
2. Click "Upload Documents"
3. Select files from `samples/`
4. Click "Process Documents"

### Step 5: Try Search (5 min)
1. Go to "Search" tab
2. Enter query: "CRISPR gene therapy"
3. View results with scores
4. Try document type filters

## 📚 Documentation Map

```
User Journey:
  ↓
  README.md ───→ Start Here
    ↓
    INSTALLATION.md ───→ Get Running
      ↓
      README.md (Usage) ───→ Learn Usage
        ↓
        examples.py ───→ Run Examples
          ↓
          app.py ───→ Explore UI
            ↓
            API Reference ───→ Integrate

Developer Journey:
  ↓
  README.md ───→ Understand Project
    ↓
    ARCHITECTURE.md ───→ Learn Design
      ↓
      src/*.py ───→ Study Code
        ↓
        CAPABILITIES.md ───→ See Features
          ↓
          examples.py ───→ Build Examples
            ↓
            DEPLOYMENT.md ───→ Deploy

Operations Journey:
  ↓
  README.md ───→ Get Overview
    ↓
    INSTALLATION.md ───→ Install
      ↓
      docker-compose.yml ───→ Deploy Locally
        ↓
        DEPLOYMENT.md ───→ Deploy Production
          ↓
          ARCHITECTURE.md ───→ Understand Scaling
            ↓
            scripts/*.sh ───→ Run Operations
```

## 🔍 Search Tips

### Find by Filename
- `src/api.py` - REST API endpoints
- `src/chunking.py` - Document chunking strategies
- `app.py` - Streamlit frontend code
- `README.md` - Quick start guide

### Find by Feature
- **Document Upload**: `src/api.py` POST /upload, `app.py` Upload Documents page
- **Search**: `src/vector_store.py` hybrid_search(), `app.py` Search page
- **Statistics**: `src/rag_pipeline.py` get_stats(), `app.py` Statistics page
- **Configuration**: `src/config.py`, `.env.example`

### Find by Technology
- **FastAPI**: `src/api.py`
- **Streamlit**: `app.py`
- **Qdrant**: `src/vector_store.py`
- **Chonkie**: `src/chunking.py`
- **Docker**: `docker-compose.yml`, `Dockerfile.*`

## 💡 Key Concepts

### Document Type Detection
Pattern-based automatic detection:
- Meeting minutes: "attendees", "agenda", "action items"
- Progress reports: "completed", "in progress", "milestones"
- Research papers: "abstract", "methodology", "results"

### Intelligent Chunking
Document-type specific chunk sizes:
- Meeting minutes: 300 tokens (preserve decisions)
- Progress reports: 500 tokens (preserve tasks)
- Research papers: 1000 tokens (preserve methodology)

### Hybrid Search
Combines two ranking methods:
- **Vector (50%)**: Semantic similarity
- **BM25 (50%)**: Exact keyword matching

### Metadata Preservation
Tracks through chunking:
- Document type
- Source file
- Creation date
- Authors
- Sections
- Custom fields

## 🛠️ Customization Points

1. **Chunk Sizes**: Edit `.env` or `src/config.py`
2. **Search Weights**: Modify in `vector_store.py` hybrid_search()
3. **Document Types**: Add patterns to `document_loader.py`
4. **UI Pages**: Add to `app.py` with Streamlit
5. **API Endpoints**: Add to `src/api.py` with FastAPI

## 📈 Scaling Strategy

### Horizontal
- Multiple API instances behind load balancer
- Qdrant cluster for distributed vectors

### Vertical
- Larger embedding models
- GPU acceleration
- Batch processing

### Cloud
- AWS: ECS, Beanstalk
- GCP: Cloud Run, Kubernetes
- Azure: Container Instances, AKS

## 🔒 Security Checklist

Production deployment should include:
- [ ] HTTPS/TLS encryption
- [ ] API key authentication
- [ ] Rate limiting
- [ ] Input validation
- [ ] Audit logging
- [ ] Data encryption at rest
- [ ] Regular backups
- [ ] Security scanning

## 📞 Support

### Issues
- Check INSTALLATION.md troubleshooting section
- Review ARCHITECTURE.md for design questions
- See DEPLOYMENT.md for production issues

### Documentation
- Start with README.md
- Use ARCHITECTURE.md for technical details
- Refer to CAPABILITIES.md for features
- Check examples.py for usage patterns

### Code Navigation
- `src/` - Core logic
- `app.py` - Frontend
- `examples.py` - Usage patterns
- Sample docs - Test data

---

**Created**: January 2024  
**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: January 2024
