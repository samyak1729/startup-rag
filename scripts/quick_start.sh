#!/bin/bash

# Quick start script for Biotech Startup RAG System

set -e

echo "🧬 Biotech Startup RAG - Quick Start"
echo "===================================="
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "1. Starting Qdrant vector database..."
docker run -d --name qdrant-rag -p 6333:6333 qdrant/qdrant:latest > /dev/null 2>&1 || true

# Wait for Qdrant to be ready
echo "   Waiting for Qdrant to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "   ✓ Qdrant is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ Qdrant failed to start"
        exit 1
    fi
    sleep 1
done

echo ""
echo "2. Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv sync > /dev/null 2>&1
    echo "   ✓ Dependencies installed with UV"
else
    pip install -q -e . 2>/dev/null || pip3 install -q -e .
    echo "   ✓ Dependencies installed with pip"
fi

echo ""
echo "3. Creating sample .env file..."
cp .env.example .env 2>/dev/null || true
echo "   ✓ .env file created"

echo ""
echo "✨ Setup Complete!"
echo ""
echo "Next steps:"
echo ""
echo "Terminal 1 - Start FastAPI backend:"
echo "  uv run python -m uvicorn src.api:app --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Start Streamlit frontend:"
echo "  uv run streamlit run app.py"
echo ""
echo "Then open:"
echo "  - Streamlit UI: http://localhost:8501"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Qdrant: http://localhost:6333"
echo ""
echo "To process sample documents:"
echo "  uv run python -c \"from src.rag_pipeline import RAGPipeline; p = RAGPipeline(); p.process_batch('samples')\""
echo ""
