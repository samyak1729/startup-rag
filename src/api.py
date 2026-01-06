"""FastAPI backend for RAG system."""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import tempfile
from pathlib import Path

from src.rag_pipeline import RAGPipeline
from src.config import settings

# Initialize FastAPI app and RAG pipeline
app = FastAPI(
    title="Biotech Startup RAG API",
    description="Retrieve information from biotech startup documents",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag_pipeline = RAGPipeline()

# Request/Response models
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    doc_type: Optional[str] = None

class SearchResult(BaseModel):
    content: str
    metadata: dict
    vector_score: float
    bm25_score: float
    combined_score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int

class UploadResponse(BaseModel):
    success: bool
    file: str
    doc_type: str
    chunk_count: int
    metadata: dict

class BatchProcessResponse(BaseModel):
    total_files: int
    successful: int
    failed: int
    files: list
    start_time: str
    end_time: str

class StatsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    documents_by_type: dict
    documents: list

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Biotech Startup RAG API",
        "version": "0.1.0",
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics."""
    return rag_pipeline.get_stats()

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a single document.
    
    Supported formats: PDF, DOCX, TXT
    """
    # Validate file extension
    supported_ext = {'.pdf', '.docx', '.txt'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in supported_ext:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported: {supported_ext}",
        )
    
    # Save to temporary file
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            suffix=file_ext,
            delete=False,
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process document
        result = rag_pipeline.process_document(tmp_path)
        
        return UploadResponse(
            success=result['success'],
            file=file.filename,
            doc_type=result['doc_type'],
            chunk_count=result['chunk_count'],
            metadata=result['metadata'],
        )
    
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}",
        )
    
    finally:
        # Cleanup
        if tmp_path:
            try:
                Path(tmp_path).unlink()
            except:
                pass

@app.post("/upload-batch")
async def upload_batch(directory: str = Query(...)):
    """
    Process all documents in a directory.
    """
    try:
        result = rag_pipeline.process_batch(directory)
        return BatchProcessResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_documents(query: SearchQuery):
    """
    Search indexed documents using hybrid search (vector + BM25).
    
    Optional filters:
    - doc_type: meeting_minutes, progress_report, research_paper
    """
    if not query.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        if query.doc_type:
            results = rag_pipeline.search_by_type(
                query.query,
                doc_type=query.doc_type,
                top_k=query.top_k,
            )
        else:
            results = rag_pipeline.search(query.query, top_k=query.top_k)
        
        # Convert results to response format
        formatted_results = [
            SearchResult(
                content=r['content'],
                metadata=r['metadata'],
                vector_score=r['vector_score'],
                bm25_score=r['bm25_score'],
                combined_score=r['combined_score'],
            )
            for r in results
        ]
        
        return SearchResponse(
            query=query.query,
            results=formatted_results,
            total=len(formatted_results),
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_documents():
    """Clear all indexed documents."""
    try:
        rag_pipeline.clear()
        return {
            "status": "success",
            "message": "All documents cleared",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "qdrant_url": settings.qdrant_url,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
    )
