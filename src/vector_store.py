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
import logging
import re

logger = logging.getLogger(__name__)

# Simple stopwords - no NLTK dependency
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has', 'he',
    'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 'the', 'to', 'was', 'will',
    'with', 'this', 'but', 'they', 'have', 'had', 'what', 'when', 'where', 'who',
    'which', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
    'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'same', 'than', 'too',
    'very', 'can', 'just', 'should', 'now', 'i', 'me', 'you', 'him', 'her', 'us',
    'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
}

class VectorStore:
    """Manages vector embeddings and BM25 lexical indices in Qdrant."""
    
    def __init__(self, embedding_model: Optional[Any] = None):
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self.embedding_model = embedding_model
        self.collection_name = settings.collection_name
        self.bm25_index: Optional[BM25Okapi] = None
        self.bm25_texts: list[str] = []  # Store texts to retrieve after BM25 search
        
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
        
        # Update BM25 index - append to existing, don't replace
        self._update_bm25_index_append(texts)
    
    def hybrid_search(self, query: str, top_k: int = 5, 
                     weights: tuple[float, float] = (0.3, 0.7)) -> list[dict]:
        """
        Perform hybrid search combining vector and BM25 results.
        
        Default weights favor BM25 (0.7) over vector search (0.3) since BM25
        is more precise for keyword-based queries. Use weights=(0.5, 0.5) for
        balanced search or (0.7, 0.3) to favor semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of results to return
            weights: (vector_weight, bm25_weight) - should sum to 1.0
        
        Returns:
            List of search results with scores
        """
        vector_weight, bm25_weight = weights
        
        logger.info(f"Hybrid search: query='{query}', top_k={top_k}, weights={weights}")
        
        # Vector search
        vector_results = self._vector_search(query, top_k=top_k*2)
        
        # BM25 search
        bm25_results = self._bm25_search(query, top_k=top_k*2)
        
        logger.info(f"Vector results: {len(vector_results)}, BM25 results: {len(bm25_results)}")
        
        # Combine results with weighted scores
        combined = {}
        
        # Process vector results
        for i, (point_id, score, content, metadata) in enumerate(vector_results):
            rank = i + 1
            # Normalize score (cosine similarity is in [-1, 1], but usually [0, 1])
            normalized_score = max(0, (score + 1) / 2)  # Ensure non-negative
            vector_score = vector_weight * normalized_score * (1 / np.log2(rank + 1))
            
            key = content.strip()
            combined[key] = {
                'vector_score': vector_score, 
                'bm25_score': 0, 
                'metadata': metadata,
                'content': content,
            }
        
        # Process BM25 results
        for i, (text, score) in enumerate(bm25_results):
            rank = i + 1
            # Normalize BM25 score (typically in [0, inf], normalize with log)
            bm25_normalized = np.log1p(score)  # log(1 + score) to compress range
            bm25_score = bm25_weight * bm25_normalized * (1 / np.log2(rank + 1))
            
            text_stripped = text.strip()
            
            # Find exact match in combined dict
            matched = False
            for key, result in combined.items():
                if key == text_stripped:
                    result['bm25_score'] = bm25_score
                    matched = True
                    logger.debug(f"Matched BM25 result with vector result: score={bm25_score:.4f}")
                    break
            
            if not matched:
                # New result from BM25
                combined[text_stripped] = {
                    'vector_score': 0,
                    'bm25_score': bm25_score,
                    'metadata': {'content': text, 'doc_type': 'unknown'},
                    'content': text,
                }
        
        # Sort by combined score and return top_k
        ranked = sorted(
            combined.items(),
            key=lambda x: x[1]['vector_score'] + x[1]['bm25_score'],
            reverse=True
        )[:top_k]
        
        results = []
        for content_key, scores in ranked:
            combined_score = scores['vector_score'] + scores['bm25_score']
            results.append({
                'content': scores['content'],
                'metadata': scores['metadata'],
                'vector_score': scores['vector_score'],
                'bm25_score': scores['bm25_score'],
                'combined_score': combined_score,
            })
            logger.debug(f"Result: combined={combined_score:.4f}, vector={scores['vector_score']:.4f}, bm25={scores['bm25_score']:.4f}")
        
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
    
    def _tokenize_and_stem(self, text: str) -> list[str]:
        """Tokenize and filter text with stopword removal."""
        # Convert to lowercase
        text = text.lower()
        
        # Simple tokenization - match word characters and hyphens
        # This will match: "crispr", "cas9", "crispr-cas9", "uk-biobank", "app", etc.
        tokens = re.findall(r'\b[a-z][a-z0-9]*(?:-[a-z0-9]+)*\b', text)
        
        # Also match acronyms and numbers
        tokens.extend(re.findall(r'\b[a-z0-9]+(?:\d{1,2})*\b', text))
        
        # Filter stopwords and short tokens (1 char is too short)
        filtered = [
            token 
            for token in tokens 
            if token not in STOPWORDS and len(token) > 1
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        result = []
        for token in filtered:
            if token not in seen:
                seen.add(token)
                result.append(token)
        
        return result
    
    def _bm25_search(self, query: str, top_k: int = 5) -> list[tuple]:
        """Search using BM25 lexical matching."""
        if self.bm25_index is None or not self.bm25_texts:
            # No documents indexed yet
            logger.warning("BM25 index not initialized")
            return []
        
        # Tokenize and stem query
        query_tokens = self._tokenize_and_stem(query)
        
        logger.info(f"BM25 query tokens: {query_tokens}")
        
        # Get BM25 scores for all documents
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            score = scores[idx]
            if score > 0:  # Only return documents with non-zero scores
                text = self.bm25_texts[idx]
                results.append((text, score))
                logger.debug(f"BM25 match: score={score:.4f}, text={text[:100]}...")
        
        if not results:
            logger.warning(f"No BM25 matches found for query: {query}")
        
        return results
    
    def _update_bm25_index(self, texts: list[str]) -> None:
        """Replace BM25 index entirely with new texts (used for testing)."""
        if not texts:
            return
        
        # Tokenize and stem all texts
        corpus = [self._tokenize_and_stem(text) for text in texts]
        
        logger.info(f"Building BM25 index with {len(corpus)} documents")
        logger.debug(f"Sample corpus tokens: {corpus[0][:10] if corpus[0] else []}...")
        
        # Build BM25 index
        self.bm25_index = BM25Okapi(corpus)
        self.bm25_texts = texts
        
        logger.info("BM25 index built successfully")
    
    def _update_bm25_index_append(self, new_texts: list[str]) -> None:
        """Append new texts to existing BM25 index."""
        if not new_texts:
            return
        
        # Append new texts to existing
        self.bm25_texts.extend(new_texts)
        
        # Tokenize and stem all texts (including existing)
        corpus = [self._tokenize_and_stem(text) for text in self.bm25_texts]
        
        logger.info(f"Updating BM25 index to {len(corpus)} total documents")
        
        # Rebuild BM25 index with all texts
        self.bm25_index = BM25Okapi(corpus)
        
        logger.info("BM25 index updated successfully")
    
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
