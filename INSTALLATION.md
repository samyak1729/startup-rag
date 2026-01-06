# Installation & Setup Guide

## System Requirements

- **Python**: 3.10 or higher
- **OS**: Linux, macOS, or Windows
- **RAM**: 4GB minimum (8GB+ recommended for production)
- **Storage**: 10GB for vectors + documents
- **Docker**: Required for Qdrant (optional if using cloud Qdrant)

## Installation Methods

## Method 1: UV Package Manager (Recommended)

UV is a fast, Rust-based Python package manager.

### Install UV

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install Project Dependencies

```bash
cd biotech-startup-rag
uv sync
```

### Run with UV

```bash
# Start API
uv run python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Start Streamlit
uv run streamlit run app.py

# Run examples
uv run python examples.py
```

## Method 2: Traditional pip + venv

### Create Virtual Environment

```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -e .
```

### Run

```bash
# Start API
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000

# Start Streamlit (in another terminal)
streamlit run app.py
```

## Method 3: Docker Compose (Full Stack)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

### Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

This starts:
- Qdrant on port 6333
- FastAPI on port 8000
- Streamlit on port 8501

## Configuration

### Environment Variables

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` for your configuration:

```ini
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Chunking Configuration
CHUNK_SIZE_MEETING_MINUTES=300
CHUNK_SIZE_PROGRESS_REPORT=500
CHUNK_SIZE_RESEARCH_PAPER=1000

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Search Configuration
TOP_K=5
```

### Configuration Precedence

1. Environment variables (`.env` file)
2. Default values in `src/config.py`

## Verifying Installation

### Check Python Version

```bash
python --version
# Should be Python 3.10 or higher
```

### Verify Dependencies

```bash
# List installed packages
pip list | grep -E "fastapi|streamlit|qdrant|chonkie"

# Or with uv
uv pip list
```

### Test Imports

```bash
python -c "
from src.rag_pipeline import RAGPipeline
from src.config import settings
from src.document_loader import DocumentLoader
from src.chunking import IntelligentChunker
from src.vector_store import VectorStore
print('✓ All imports successful')
"
```

### Test Qdrant Connection

```bash
# Start Qdrant first
docker run -d -p 6333:6333 qdrant/qdrant

# Test connection
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://localhost:6333')
health = client.get_collection
print('✓ Qdrant connection successful')
"
```

## Starting the System

### Terminal Setup

You need 3 terminals:

**Terminal 1: Start Qdrant**
```bash
docker run -p 6333:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

Wait for: "Listening on 0.0.0.0:6333"

**Terminal 2: Start FastAPI Backend**
```bash
uv run python -m uvicorn src.api:app --reload
# Or with pip: python -m uvicorn src.api:app --reload
```

Wait for: "Application startup complete"

**Terminal 3: Start Streamlit Frontend**
```bash
uv run streamlit run app.py
# Or with pip: streamlit run app.py
```

Wait for: "You can now view your Streamlit app..."

### Access the Application

- **Streamlit UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **Qdrant**: http://localhost:6333/dashboard

## Loading Sample Documents

### Option 1: Using Streamlit UI

1. Go to http://localhost:8501
2. Click "Upload Documents" page
3. Drag & drop files from `samples/` folder
4. Click "Process Documents"

### Option 2: Using Python Script

```python
from src.rag_pipeline import RAGPipeline

pipeline = RAGPipeline()

# Process single document
pipeline.process_document("samples/sample_meeting_minutes.txt")

# Or batch process
results = pipeline.process_batch("samples", pattern="*.txt")

# View stats
stats = pipeline.get_stats()
print(f"Documents: {stats['total_documents']}")
print(f"Chunks: {stats['total_chunks']}")
```

### Option 3: Using API

```bash
# Upload document
curl -X POST http://localhost:8000/upload \
  -F "file=@samples/sample_meeting_minutes.txt"

# Batch process directory
curl -X POST "http://localhost:8000/upload-batch?directory=samples"
```

## Running Examples

```bash
# Run all examples
uv run python examples.py
# or
python examples.py
```

This demonstrates:
1. Processing single documents
2. Batch processing
3. Basic search
4. Filtered search
5. System statistics
6. Multiple queries
7. Metadata exploration

## Testing

### Run Unit Tests

```bash
# Install test dependencies
uv sync --extra dev
# or: pip install -e ".[dev]"

# Run tests
uv run pytest tests/ -v
pytest tests/ -v
```

### Manual Testing

**Test document loading:**
```bash
python -c "
from src.document_loader import DocumentLoader
loader = DocumentLoader()
content, metadata = loader.load_document('samples/sample_meeting_minutes.txt')
print(f'Content length: {len(content)}')
print(f'Doc type: {metadata.doc_type}')
"
```

**Test chunking:**
```bash
python -c "
from src.rag_pipeline import RAGPipeline
pipeline = RAGPipeline()
result = pipeline.process_document('samples/sample_meeting_minutes.txt')
print(f'Chunks created: {result[\"chunk_count\"]}')
"
```

**Test search:**
```bash
python -c "
from src.rag_pipeline import RAGPipeline
pipeline = RAGPipeline()
pipeline.process_document('samples/sample_research_paper.txt')
results = pipeline.search('CRISPR gene therapy', top_k=3)
print(f'Found {len(results)} results')
for r in results:
    print(f'  Score: {r[\"combined_score\"]:.3f}')
"
```

## Troubleshooting Installation

### Python Version Issues

```bash
# Check Python version
python --version

# Use specific version (if you have 3.10 installed)
python3.10 -m venv venv
source venv/bin/activate
```

### Dependency Installation Fails

```bash
# Clear pip cache
pip cache purge

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Try installing with verbose output
pip install -e . -v
```

### Qdrant Connection Issues

```bash
# Ensure Docker is running
docker ps

# Start Qdrant if not running
docker run -d -p 6333:6333 qdrant/qdrant

# Check connection
curl http://localhost:6333/health
```

### Import Errors

```bash
# Reinstall package in development mode
pip install -e . --force-reinstall

# Or with UV
uv pip install -e . --force-reinstall
```

### Memory Issues

```bash
# Set Python memory limit
export PYTHONMALLOC=malloc
# Then run commands

# Or reduce chunk sizes in .env
CHUNK_SIZE_MEETING_MINUTES=200
CHUNK_SIZE_PROGRESS_REPORT=300
CHUNK_SIZE_RESEARCH_PAPER=500
```

### Port Already in Use

```bash
# Kill process using port 6333
lsof -i :6333 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Or use different port
docker run -d -p 6334:6333 qdrant/qdrant
# Then update .env: QDRANT_URL=http://localhost:6334
```

## Development Setup

### Install Development Tools

```bash
uv sync --extra dev
# or: pip install -e ".[dev]"
```

This installs:
- pytest: Testing framework
- black: Code formatter
- ruff: Linter

### Code Formatting

```bash
# Format code
uv run black src/

# Check linting
uv run ruff check src/

# Fix linting issues
uv run ruff check --fix src/
```

### Pre-commit Hooks (Optional)

```bash
pip install pre-commit

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix]
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
EOF

pre-commit install
```

## Uninstallation

### Remove Virtual Environment

```bash
# Deactivate
deactivate

# Remove venv directory
rm -rf venv
```

### Remove Docker Containers

```bash
# Stop and remove containers
docker-compose down -v

# Or manually
docker stop $(docker ps -q)
docker rm $(docker ps -aq)
```

### Clean Up Files

```bash
# Remove generated files
rm -rf __pycache__ .pytest_cache .coverage
rm -f pipeline_state.json
```

## Next Steps

1. **Review Architecture**: Read ARCHITECTURE.md
2. **Try Examples**: Run `python examples.py`
3. **Upload Documents**: Use Streamlit UI to upload your documents
4. **Search Documents**: Try searching in the UI
5. **Explore API**: Visit http://localhost:8000/docs
6. **Deploy**: See DEPLOYMENT.md for production setup

## Getting Help

### Check Documentation
- README.md: Project overview and usage
- ARCHITECTURE.md: Technical design
- DEPLOYMENT.md: Production deployment
- examples.py: Code examples

### Common Issues
- Port conflicts: Change ports in .env
- Memory issues: Reduce chunk sizes
- Connection errors: Check Qdrant is running
- Import errors: Reinstall with pip install -e .

### Reporting Issues
Create a GitHub issue with:
1. Python version: `python --version`
2. Error message: Full traceback
3. System info: OS and available RAM
4. Steps to reproduce
