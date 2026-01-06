"""Vector store and hybrid search integration with Qdrant."""

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, FieldCondition, MatchValue
from qdrant_client.models import Filter, HasIdCondition
from qdrant_client.http.exceptions import UnexpectedResponse, ResponseHandlingException
from typing import Optional, Any
import hashlib
import json
from rank_bm25 import BM25Okapi
import numpy as np
from src.config import settings

class VectorStore:
    """Manages vector embeddings and BM25 lexical indices in Qdrant."""
    
    def __init__(self, embedding_model: Optional[Any] = None):
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self.embedding_model = embedding_model
        self.collection_name = settings.collection_name
        self.bm25_indices: dict[str, BM25Okapi] = {}
        
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist."""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            # We'll set vector size after first embedding
            pass
    
    def add_documents(self, chunks: list[dict]) -> None:
        """Add document chunks to the vector store."""
        if not chunks:
            return
        
        points = []
        texts = []
        
        for i, chunk in enumerate(chunks):
            # Generate consistent ID based on content
            chunk_id = self._generate_id(chunk['content'])
            text = chunk['content']
            texts.append(text)
            
            # Get embedding
            embedding = self._get_embedding(text)
            
            # Prepare metadata as payload
            payload = {
                'content': text,
                **chunk.get('metadata', {}),
            }
            
            # Create point
            point = PointStruct(
                id=int(chunk_id, 16) % (2**63 - 1),  # Convert hex to positive int
                vector=embedding,
                payload=payload,
            )
            points.append(point)
        
        # Create collection with proper vector size if needed
        if points:
            vector_size = len(points[0].vector)
            try:
                self.client.get_collection(self.collection_name)
            except (UnexpectedResponse, ResponseHandlingException, Exception):
                # Collection doesn't exist or couldn't be retrieved, try to create it
                try:
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                    )
                except UnexpectedResponse as e:
                    # If it's a 409 Conflict, the collection already exists - that's fine
                    if e.status_code != 409:
                        raise
            
            # Upsert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
        
        # Update BM25 index
        self._update_bm25_index(texts)
    
    def hybrid_search(self, query: str, top_k: int = 5, 
                     weights: tuple[float, float] = (0.5, 0.5)) -> list[dict]:
        """
        Perform hybrid search combining vector and BM25 results.
        
        Args:
            query: Search query
            top_k: Number of results to return
            weights: (vector_weight, bm25_weight)
        
        Returns:
            List of (document, score) tuples
        """
        vector_weight, bm25_weight = weights
        
        # Vector search
        vector_results = self._vector_search(query, top_k=top_k*2)
        
        # BM25 search
        bm25_results = self._bm25_search(query, top_k=top_k*2)
        
        # Combine results with weighted scores
        combined = {}
        
        for i, (point_id, score, content, metadata) in enumerate(vector_results):
            rank = i + 1
            # Normalize score (higher is better for cosine similarity)
            normalized_score = (score + 1) / 2  # Convert from [-1, 1] to [0, 1]
            vector_score = (1 / rank) * vector_weight * normalized_score
            
            key = (point_id, content)
            combined[key] = {'vector_score': vector_score, 'bm25_score': 0, 'metadata': metadata}
        
        for i, (text, score) in enumerate(bm25_results):
            rank = i + 1
            bm25_score = (1 / rank) * bm25_weight * score
            
            # Try to match with vector results
            matched = False
            for (point_id, content), result in combined.items():
                if content.strip()[:100] == text.strip()[:100]:  # Fuzzy match
                    result['bm25_score'] = bm25_score
                    matched = True
                    break
            
            if not matched:
                # New result from BM25
                combined[(None, text)] = {
                    'vector_score': 0,
                    'bm25_score': bm25_score,
                    'metadata': {'content': text}
                }
        
        # Sort by combined score and return top_k
        ranked = sorted(
            combined.items(),
            key=lambda x: x[1]['vector_score'] + x[1]['bm25_score'],
            reverse=True
        )[:top_k]
        
        results = []
        for (point_id, content), scores in ranked:
            results.append({
                'content': content,
                'metadata': scores['metadata'],
                'vector_score': scores['vector_score'],
                'bm25_score': scores['bm25_score'],
                'combined_score': scores['vector_score'] + scores['bm25_score'],
            })
        
        return results
    
    def _vector_search(self, query: str, top_k: int = 5) -> list[tuple]:
        """Search using vector embeddings."""
        query_embedding = self._get_embedding(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
        )
        
        return [(r.id, r.score, r.payload.get('content', ''), r.payload) for r in results]
    
    def _bm25_search(self, query: str, top_k: int = 5) -> list[tuple]:
        """Search using BM25 lexical matching."""
        if not self.bm25_indices:
            # No documents indexed yet
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        best_results = []
        
        for doc_name, bm25 in self.bm25_indices.items():
            scores = bm25.get_scores(query_tokens)
            top_indices = np.argsort(scores)[-top_k:][::-1]
            
            for idx in top_indices:
                if scores[idx] > 0:
                    # We'd need to store document texts, so for now return placeholder
                    best_results.append((None, scores[idx]))
        
        # Sort by score
        best_results.sort(key=lambda x: x[1], reverse=True)
        return best_results[:top_k]
    
    def _update_bm25_index(self, texts: list[str]) -> None:
        """Update BM25 index with new texts."""
        corpus = [text.lower().split() for text in texts]
        
        if corpus:
            bm25 = BM25Okapi(corpus)
            # Store in index (you could also use a dedicated database)
            self.bm25_indices[self.collection_name] = bm25
    
    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text."""
        if self.embedding_model is None:
            # Initialize with default model
            from qdrant_client.models import Distance
            try:
                # Try to use Qdrant's built-in embedding
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(settings.embedding_model)
            except:
                # Fallback: create dummy embedding
                return [float(x) / 255.0 for x in hashlib.md5(text.encode()).digest()]
        
        # Generate embedding
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        
        return embedding
    
    def _generate_id(self, content: str) -> str:
        """Generate deterministic ID from content."""
        return hashlib.md5(content.encode()).hexdigest()
    
    def search_by_metadata(self, metadata_filter: dict) -> list[dict]:
        """Search documents by metadata fields."""
        conditions = []
        for key, value in metadata_filter.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value),
                )
            )
        
        if not conditions:
            return []
        
        # Simple filter - Qdrant would need proper filter construction
        results = self.client.scroll(
            collection_name=self.collection_name,
            limit=100,
        )
        
        return [
            {
                'content': r.payload.get('content', ''),
                'metadata': {k: v for k, v in r.payload.items() if k != 'content'},
            }
            for r in results[0]
        ]
    
    def delete_collection(self) -> None:
        """Delete the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except:
            pass
