"""Load documents from various formats."""

from pathlib import Path
from typing import Optional, Tuple
import json
from datetime import datetime
import PyPDF2
from docx import Document as DocxDocument

class DocumentMetadata:
    def __init__(self):
        self.doc_type: Optional[str] = None
        self.title: Optional[str] = None
        self.created_date: Optional[str] = None
        self.modified_date: Optional[str] = None
        self.authors: list[str] = []
        self.source_file: Optional[str] = None
        self.page_number: Optional[int] = None
        
    def to_dict(self) -> dict:
        return {
            k: v for k, v in self.__dict__.items() 
            if v is not None and v != []
        }

class DocumentLoader:
    """Loads documents and extracts metadata based on file type."""
    
    def __init__(self):
        self.doc_type_detectors = {
            'meeting': self._detect_meeting_minutes,
            'progress': self._detect_progress_report,
            'research': self._detect_research_paper,
        }
    
    def load_document(self, file_path: str) -> Tuple[str, DocumentMetadata]:
        """Load document and extract metadata."""
        path = Path(file_path)
        
        if path.suffix.lower() == '.pdf':
            content, metadata = self._load_pdf(file_path)
        elif path.suffix.lower() == '.docx':
            content, metadata = self._load_docx(file_path)
        elif path.suffix.lower() == '.txt':
            content, metadata = self._load_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        
        # Detect document type
        metadata.doc_type = self._detect_document_type(content)
        metadata.source_file = str(path)
        
        return content, metadata
    
    def _load_pdf(self, file_path: str) -> Tuple[str, DocumentMetadata]:
        """Extract text and metadata from PDF."""
        metadata = DocumentMetadata()
        text_content = []
        
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            
            # Extract metadata
            if reader.metadata:
                metadata.title = reader.metadata.get('/Title')
                metadata.created_date = reader.metadata.get('/CreationDate')
                metadata.authors = [reader.metadata.get('/Author')] if reader.metadata.get('/Author') else []
            
            # Extract text from all pages
            for page_num, page in enumerate(reader.pages, 1):
                text_content.append(page.extract_text())
        
        return '\n'.join(text_content), metadata
    
    def _load_docx(self, file_path: str) -> Tuple[str, DocumentMetadata]:
        """Extract text and metadata from DOCX."""
        metadata = DocumentMetadata()
        doc = DocxDocument(file_path)
        
        # Extract metadata
        if doc.core_properties:
            props = doc.core_properties
            metadata.title = props.title
            metadata.authors = [props.author] if props.author else []
            metadata.created_date = str(props.created) if props.created else None
            metadata.modified_date = str(props.modified) if props.modified else None
        
        # Extract text
        text_content = [para.text for para in doc.paragraphs]
        return '\n'.join(text_content), metadata
    
    def _load_txt(self, file_path: str) -> Tuple[str, DocumentMetadata]:
        """Load plain text file."""
        metadata = DocumentMetadata()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content, metadata
    
    def _detect_document_type(self, content: str) -> str:
        """Detect document type based on content patterns."""
        content_lower = content.lower()
        
        # Meeting minutes detection
        if self._detect_meeting_minutes(content_lower):
            return 'meeting_minutes'
        
        # Progress report detection
        if self._detect_progress_report(content_lower):
            return 'progress_report'
        
        # Research paper detection
        if self._detect_research_paper(content_lower):
            return 'research_paper'
        
        return 'general'
    
    @staticmethod
    def _detect_meeting_minutes(content: str) -> bool:
        """Detect meeting minutes patterns."""
        patterns = [
            'minutes of meeting',
            'meeting agenda',
            'attendees:',
            'action items',
            'next meeting',
            'date:',
            'time:',
            'discussed',
        ]
        content_lower = content.lower()
        matches = sum(1 for pattern in patterns if pattern in content_lower)
        return matches >= 3
    
    @staticmethod
    def _detect_progress_report(content: str) -> bool:
        """Detect progress report patterns."""
        patterns = [
            'progress report',
            'completed',
            'in progress',
            'completed tasks',
            'upcoming milestones',
            'status update',
            'week of',
            'monthly report',
        ]
        content_lower = content.lower()
        matches = sum(1 for pattern in patterns if pattern in content_lower)
        return matches >= 3
    
    @staticmethod
    def _detect_research_paper(content: str) -> bool:
        """Detect research paper patterns."""
        patterns = [
            'abstract',
            'introduction',
            'methodology',
            'results',
            'conclusion',
            'references',
            'hypothesis',
            'experiment',
            'analysis',
        ]
        content_lower = content.lower()
        matches = sum(1 for pattern in patterns if pattern in content_lower)
        return matches >= 3
