"""Main RAG pipeline orchestration."""

from pathlib import Path
from typing import Optional
import json
from datetime import datetime
from src.document_loader import DocumentLoader
from src.chunking import IntelligentChunker
from src.vector_store import VectorStore
from src.query_rewriter import QueryRewriter

class RAGPipeline:
    """Orchestrates the entire RAG pipeline."""
    
    def __init__(self):
        self.doc_loader = DocumentLoader()
        self.chunker = IntelligentChunker()
        self.vector_store = VectorStore()
        self.processed_documents = []
    
    def process_document(self, file_path: str) -> dict:
        """
        Process a single document through the entire pipeline.
        
        Returns:
            dict with processing results
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        print(f"Processing: {path.name}")
        
        # Step 1: Load document
        print("  → Loading document...")
        content, metadata = self.doc_loader.load_document(file_path)
        
        # Step 2: Intelligent chunking
        print(f"  → Chunking ({metadata.doc_type})...")
        chunks = self.chunker.chunk(content, metadata)
        
        # Step 3: Add to vector store
        print(f"  → Indexing {len(chunks)} chunks...")
        self.vector_store.add_documents(chunks)
        
        # Track processing
        doc_record = {
            'file': str(path),
            'doc_type': metadata.doc_type,
            'chunks': len(chunks),
            'processed_at': datetime.now().isoformat(),
            'metadata': metadata.to_dict(),
        }
        self.processed_documents.append(doc_record)
        
        print(f"  ✓ Successfully processed: {len(chunks)} chunks")
        
        return {
            'success': True,
            'file': str(path),
            'doc_type': metadata.doc_type,
            'chunk_count': len(chunks),
            'metadata': metadata.to_dict(),
        }
    
    def process_batch(self, directory: str, pattern: str = "**/*") -> dict:
        """
        Process all documents in a directory.
        
        Args:
            directory: Path to directory containing documents
            pattern: Glob pattern for files
        
        Returns:
            dict with batch processing results
        """
        path = Path(directory)
        
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all documents
        supported_formats = {'.pdf', '.docx', '.txt'}
        files = [
            f for f in path.glob(pattern)
            if f.is_file() and f.suffix.lower() in supported_formats
        ]
        
        print(f"Found {len(files)} documents to process")
        
        results = {
            'total_files': len(files),
            'successful': 0,
            'failed': 0,
            'files': [],
            'start_time': datetime.now().isoformat(),
        }
        
        for file_path in files:
            try:
                result = self.process_document(str(file_path))
                results['successful'] += 1
                results['files'].append(result)
            except Exception as e:
                results['failed'] += 1
                results['files'].append({
                    'file': str(file_path),
                    'success': False,
                    'error': str(e),
                })
                print(f"  ✗ Failed to process {file_path.name}: {e}")
        
        results['end_time'] = datetime.now().isoformat()
        
        return results
    
    def search(self, query: str, top_k: int = 5, use_query_expansion: bool = False) -> list[dict]:
        """
        Search the indexed documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_query_expansion: Whether to expand query with synonyms
        
        Returns:
            List of search results with content and metadata
        """
        # Optionally expand query
        if use_query_expansion:
            rewritten = QueryRewriter.rewrite_query(query)
            search_query = rewritten['expanded_query']
        else:
            search_query = query
        
        return self.vector_store.hybrid_search(search_query, top_k=top_k)
    
    def search_by_type(self, query: str, doc_type: str, top_k: int = 5) -> list[dict]:
        """
        Search documents filtered by type.
        
        Args:
            query: Search query
            doc_type: Document type filter (meeting_minutes, progress_report, research_paper)
            top_k: Number of results to return
        
        Returns:
            Filtered search results
        """
        results = self.vector_store.hybrid_search(query, top_k=top_k*2)
        
        # Filter by doc_type
        filtered = [
            r for r in results
            if r.get('metadata', {}).get('doc_type') == doc_type
        ]
        
        return filtered[:top_k]
    
    def search_by_tags(self, query: str, semantic_tags: list[str], top_k: int = 5) -> list[dict]:
        """
        Search documents filtered by semantic tags.
        
        Args:
            query: Search query
            semantic_tags: List of semantic tags to filter by (e.g., ['key-finding', 'results'])
            top_k: Number of results to return
        
        Returns:
            Filtered search results
        """
        results = self.vector_store.hybrid_search(query, top_k=top_k*3)
        
        # Filter by semantic tags
        filtered = [
            r for r in results
            if any(tag in r.get('metadata', {}).get('semantic_tags', []) for tag in semantic_tags)
        ]
        
        return filtered[:top_k]
    
    def search_with_intent(self, query: str, query_intent: str, top_k: int = 5) -> list[dict]:
        """
        Search with automatic intent detection and filtering.
        
        Args:
            query: Search query
            query_intent: Type of query (research_finding, timeline, regulatory, methodology)
            top_k: Number of results to return
        
        Returns:
            Filtered search results
        """
        # Map query intent to document types and tags
        intent_filters = {
            'research_finding': {
                'doc_types': ['research_paper'],
                'tags': ['finding', 'key-finding', 'result', 'results', 'efficacy'],
            },
            'timeline': {
                'doc_types': ['progress_report'],
                'tags': ['timeline'],
            },
            'regulatory': {
                'doc_types': ['general', 'progress_report'],
                'tags': ['regulatory'],
            },
            'methodology': {
                'doc_types': ['research_paper'],
                'tags': ['methodology', 'method'],
            },
        }
        
        filters = intent_filters.get(query_intent, {})
        results = self.vector_store.hybrid_search(query, top_k=top_k*3)
        
        # Apply doc type filter if specified
        if filters.get('doc_types'):
            results = [
                r for r in results
                if r.get('metadata', {}).get('doc_type') in filters['doc_types']
            ]
        
        # Apply semantic tag filter if specified
        if filters.get('tags'):
            results = [
                r for r in results
                if any(tag in r.get('metadata', {}).get('semantic_tags', []) for tag in filters['tags'])
            ]
        
        return results[:top_k]
    
    def get_stats(self) -> dict:
        """Get pipeline statistics."""
        doc_types = {}
        total_chunks = 0
        
        for doc in self.processed_documents:
            doc_type = doc.get('doc_type', 'unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            total_chunks += doc.get('chunks', 0)
        
        return {
            'total_documents': len(self.processed_documents),
            'total_chunks': total_chunks,
            'documents_by_type': doc_types,
            'documents': self.processed_documents,
        }
    
    def save_state(self, filepath: str) -> None:
        """Save pipeline state to file."""
        state = {
            'processed_documents': self.processed_documents,
            'stats': self.get_stats(),
            'saved_at': datetime.now().isoformat(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
    
    def clear(self) -> None:
        """Clear all indexed documents."""
        self.vector_store.delete_collection()
        self.processed_documents = []
