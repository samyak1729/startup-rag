"""Adaptive chunking with parent-child relationships for better retrieval."""

import re
from typing import Optional
from src.document_loader import DocumentMetadata

class ChunkRelationship:
    """Represents relationships between chunks."""
    
    def __init__(self, chunk_id: str, content: str, metadata: dict):
        self.id = chunk_id
        self.content = content
        self.metadata = metadata
        self.parent_id: Optional[str] = None
        self.child_ids: list[str] = []
        self.prev_chunk_id: Optional[str] = None
        self.next_chunk_id: Optional[str] = None

class AdaptiveChunker:
    """
    Produces smaller, more focused chunks with semantic boundaries.
    
    Sizes:
    - Meeting minutes: 600 chars (goal: each decision/action item)
    - Progress reports: 800 chars (goal: each task)
    - Research papers: 1000 chars (goal: specific findings, not entire sections)
    """
    
    def __init__(self):
        # Reduced from original sizes
        self.chunk_sizes = {
            'meeting_minutes': 600,      # was 1200
            'progress_report': 800,      # was 2000
            'research_paper': 1000,      # was 4000
        }
        
        # Semantic boundaries - split on these patterns
        self.semantic_boundaries = {
            'research_paper': [
                (r'(?i)^(1\.|2\.|3\.|[\d]+\.)\s+', 'numbered_item'),
                (r'(?i)^(Figure|Table|Supplementary)\s+', 'figure_table'),
                (r'(?i)^(A\.|B\.|C\.|D\.|E\.|F\.|G\.|H\.)\s+', 'lettered_item'),
                (r'(?i)\n\n+(?=[A-Z])', 'paragraph_break'),
            ],
            'progress_report': [
                (r'(?i)^(✓|✗|⚠)\s+', 'bullet_point'),
                (r'(?i)^[-•]\s+', 'list_item'),
                (r'(?i)^(Completed|In Progress|Upcoming|Blocked):', 'status_marker'),
                (r'\n\n+(?=[A-Z])', 'paragraph_break'),
            ],
            'meeting_minutes': [
                (r'(?i)^[-•]\s+', 'bullet_point'),
                (r'(?i)^(Decision|Action|Discussion):', 'section_marker'),
                (r'(?i)^(Attendees|Date|Time):', 'metadata_marker'),
                (r'\n\n+(?=[A-Z])', 'paragraph_break'),
            ],
        }
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        """
        Split content into focused chunks with semantic boundaries.
        
        Returns:
            List of chunks with metadata including parent/child relationships
        """
        doc_type = metadata.doc_type or 'general'
        target_size = self.chunk_sizes.get(doc_type, 1000)
        boundaries = self.semantic_boundaries.get(doc_type, [])
        
        # First pass: split on semantic boundaries
        semantic_chunks = self._split_on_boundaries(content, boundaries)
        
        # Second pass: merge small chunks and split large chunks
        final_chunks = self._merge_and_split(semantic_chunks, target_size)
        
        # Third pass: build relationships
        chunks_with_ids = []
        for i, chunk_text in enumerate(final_chunks):
            chunk_id = self._generate_chunk_id(metadata.source_file, i)
            chunk_metadata = metadata.to_dict() if hasattr(metadata, 'to_dict') else {}
            chunk_metadata.update({
                'chunk_index': i,
                'total_chunks': len(final_chunks),
                'position': 'first' if i == 0 else 'last' if i == len(final_chunks) - 1 else 'middle',
            })
            
            chunks_with_ids.append({
                'content': chunk_text,
                'metadata': chunk_metadata,
            })
        
        # Add chain relationships
        self._build_chunk_chain(chunks_with_ids)
        
        return chunks_with_ids
    
    @staticmethod
    def _split_on_boundaries(content: str, boundaries: list[tuple]) -> list[str]:
        """Split content on semantic boundaries."""
        if not boundaries:
            return [content]
        
        # Use first boundary pattern to split
        pattern, _ = boundaries[0]
        parts = re.split(f'({pattern})', content)
        
        # Reconstruct: recombine patterns with their text
        chunks = []
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and re.match(pattern, parts[i]):
                # Pattern matched - combine with next part
                chunk = parts[i] + parts[i + 1]
                i += 2
            else:
                chunk = parts[i]
                i += 1
            
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [content]
    
    @staticmethod
    def _merge_and_split(chunks: list[str], target_size: int) -> list[str]:
        """Merge small chunks and split large chunks."""
        result = []
        current = ""
        
        for chunk in chunks:
            # If adding this chunk keeps us under target, add it
            if len(current) + len(chunk) <= target_size * 1.2:  # 20% tolerance
                current += chunk
            else:
                # If current has content, save it
                if current.strip():
                    result.append(current)
                
                # If this chunk itself is too large, split it
                if len(chunk) > target_size * 1.5:
                    # Split on whitespace
                    sub_chunks = AdaptiveChunker._split_large_chunk(chunk, target_size)
                    result.extend(sub_chunks)
                else:
                    current = chunk
        
        # Add final chunk
        if current.strip():
            result.append(current)
        
        return result
    
    @staticmethod
    def _split_large_chunk(text: str, target_size: int) -> list[str]:
        """Split a large chunk on whitespace."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1
            if current_size + word_size > target_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    @staticmethod
    def _generate_chunk_id(source_file: Optional[str], index: int) -> str:
        """Generate consistent chunk ID."""
        file_hash = hash(source_file or "unknown") & 0x7fffffff
        return f"{file_hash}_{index}"
    
    @staticmethod
    def _build_chunk_chain(chunks: list[dict]) -> None:
        """Build prev/next relationships between chunks."""
        for i, chunk in enumerate(chunks):
            if i > 0:
                chunk['metadata']['prev_chunk_index'] = i - 1
            if i < len(chunks) - 1:
                chunk['metadata']['next_chunk_index'] = i + 1

