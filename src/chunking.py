"""Intelligent chunking strategies based on document type."""

from langchain_text_splitters import CharacterTextSplitter
from typing import Optional, Any
from src.document_loader import DocumentMetadata

# Wrapper class to mimic chonkie's chunk interface
class ChunkObject:
    def __init__(self, text: str):
        self.text = text

class ChunkingStrategy:
    """Base class for chunking strategies."""
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        raise NotImplementedError

class MeetingMinutesChunker(ChunkingStrategy):
    """
    For meeting minutes:
    - Smaller chunks (300 tokens) to preserve action items, decisions
    - Group by sections: agenda, decisions, action items
    """
    
    def __init__(self, chunk_size: int = 1200):  # ~300 tokens at ~4 chars per token
        self.chunker = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200)
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        """Chunk meeting minutes with structural awareness."""
        chunks = []
        sections = self._parse_sections(content)
        
        for section_title, section_content in sections:
            text_chunks = self.chunker.split_text(section_content)
            
            for i, chunk in enumerate(text_chunks):
                chunk_metadata = {
                    **metadata.to_dict(),
                    'section': section_title,
                    'doc_type': 'meeting_minutes',
                    'chunk_type': 'structured_section',
                }
                
                chunks.append({
                    'content': chunk,
                    'metadata': chunk_metadata,
                })
        
        return chunks
    
    @staticmethod
    def _parse_sections(content: str) -> list[tuple[str, str]]:
        """Parse meeting minutes into logical sections."""
        sections = []
        current_section = "General"
        current_content = []
        
        section_keywords = [
            'agenda', 'attendees', 'decisions', 'action items',
            'discussion', 'next steps', 'follow up'
        ]
        
        for line in content.split('\n'):
            line_lower = line.lower().strip()
            
            # Check if line starts a new section
            if any(keyword in line_lower for keyword in section_keywords):
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                    current_content = []
                current_section = line
            else:
                current_content.append(line)
        
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections

class ProgressReportChunker(ChunkingStrategy):
    """
    For progress reports:
    - Medium chunks (500 tokens)
    - Preserve context of completed vs. in-progress tasks
    """
    
    def __init__(self, chunk_size: int = 2000):  # ~500 tokens at ~4 chars per token
        self.chunker = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=200)
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        """Chunk progress reports with task-aware context."""
        chunks = []
        sections = self._parse_task_sections(content)
        
        for task_type, task_content in sections:
            text_chunks = self.chunker.split_text(task_content)
            
            for chunk in text_chunks:
                chunk_metadata = {
                    **metadata.to_dict(),
                    'task_type': task_type,
                    'doc_type': 'progress_report',
                    'chunk_type': 'task_based',
                }
                
                chunks.append({
                    'content': chunk,
                    'metadata': chunk_metadata,
                })
        
        return chunks
    
    @staticmethod
    def _parse_task_sections(content: str) -> list[tuple[str, str]]:
        """Parse progress report by task status."""
        sections = []
        current_section = "General"
        current_content = []
        
        task_keywords = {
            'completed': ['completed', 'done', 'finished'],
            'in_progress': ['in progress', 'working on', 'underway'],
            'upcoming': ['upcoming', 'next', 'planned', 'milestones'],
            'blocked': ['blocked', 'impediments', 'challenges', 'issues'],
        }
        
        for line in content.split('\n'):
            line_lower = line.lower().strip()
            
            # Detect task category
            for category, keywords in task_keywords.items():
                if any(kw in line_lower for kw in keywords) and ':' in line:
                    if current_content:
                        sections.append((current_section, '\n'.join(current_content)))
                        current_content = []
                    current_section = category
                    break
            
            current_content.append(line)
        
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections

class ResearchPaperChunker(ChunkingStrategy):
    """
    For research papers:
    - Larger chunks (1000 tokens) to preserve experimental context
    - Semantic chunking to maintain coherence
    - Preserve citations and methodology details
    """
    
    def __init__(self, chunk_size: int = 4000):  # ~1000 tokens at ~4 chars per token
        # Use character splitter for context preservation
        self.chunker = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=400)
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        """Chunk research paper with semantic awareness."""
        chunks = []
        sections = self._parse_paper_structure(content)
        
        for section_name, section_content in sections:
            text_chunks = self.chunker.split_text(section_content)
            
            for chunk in text_chunks:
                chunk_metadata = {
                    **metadata.to_dict(),
                    'section': section_name,
                    'doc_type': 'research_paper',
                    'chunk_type': 'semantic',
                }
                
                chunks.append({
                    'content': chunk,
                    'metadata': chunk_metadata,
                })
        
        return chunks
    
    @staticmethod
    def _parse_paper_structure(content: str) -> list[tuple[str, str]]:
        """Parse research paper structure."""
        paper_sections = [
            'abstract', 'introduction', 'methodology', 'results',
            'discussion', 'conclusion', 'references', 'appendix'
        ]
        
        sections = []
        current_section = "General"
        current_content = []
        
        for line in content.split('\n'):
            line_lower = line.lower().strip()
            
            # Check for major sections
            for section in paper_sections:
                if section in line_lower and (line_lower == section or 
                                             line_lower.startswith(section + ' ') or
                                             line_lower.startswith(section.upper())):
                    if current_content:
                        sections.append((current_section, '\n'.join(current_content)))
                        current_content = []
                    current_section = section.title()
                    break
            
            current_content.append(line)
        
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections

class IntelligentChunker:
    """Routes to appropriate chunker based on document type."""
    
    def __init__(self):
        self.chunkers = {
            'meeting_minutes': MeetingMinutesChunker(),
            'progress_report': ProgressReportChunker(),
            'research_paper': ResearchPaperChunker(),
        }
        self.default_chunker = CharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    
    def chunk(self, content: str, metadata: DocumentMetadata) -> list[dict]:
        """Route to appropriate chunker based on document type."""
        doc_type = metadata.doc_type or 'general'
        
        if doc_type in self.chunkers:
            return self.chunkers[doc_type].chunk(content, metadata)
        else:
            # Default chunking for unknown types
            text_chunks = self.default_chunker.split_text(content)
            return [
                {
                    'content': chunk,
                    'metadata': {
                        **metadata.to_dict(),
                        'doc_type': 'general',
                        'chunk_type': 'default',
                    }
                }
                for chunk in text_chunks
            ]
