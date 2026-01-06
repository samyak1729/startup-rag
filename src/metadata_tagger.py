"""Metadata tagging for chunks based on content analysis."""

import re
from typing import Optional
from src.document_loader import DocumentMetadata

class MetadataTagger:
    """Adds semantic tags to chunks based on content patterns."""
    
    # Research paper section patterns
    RESEARCH_TAGS = {
        'abstract': r'(?i)^(abstract|summary)',
        'introduction': r'(?i)^(introduction|background|literature review)',
        'methodology': r'(?i)^(methodology|methods|materials|procedure)',
        'results': r'(?i)^(results|findings|outcome)',
        'discussion': r'(?i)^(discussion|interpretation)',
        'conclusion': r'(?i)^(conclusion|summary|implications)',
        'references': r'(?i)^(references|bibliography|citations)',
    }
    
    # General content tags
    CONTENT_TAGS = {
        'finding': r'(?i)(find|discover|show|demonstrate|reveal|conclude)',
        'methodology': r'(?i)(method|approach|technique|procedure|analyze|test)',
        'result': r'(?i)(result|outcome|found|showed|proved|significant)',
        'regulatory': r'(?i)(fda|approval|regulation|regulatory|compliance|requirement)',
        'timeline': r'(?i)(timeline|schedule|deadline|date|week|month|quarter|q[1-4])',
        'metric': r'(?i)(improvement|reduction|increase|decrease|percent|%)',
        'safety': r'(?i)(safety|toxicity|adverse|effect|side effect|risk)',
        'efficacy': r'(?i)(efficacy|effective|efficient|performance|success)',
    }
    
    @staticmethod
    def tag_chunk(chunk_content: str, metadata: DocumentMetadata) -> dict:
        """
        Add semantic tags to a chunk.
        
        Args:
            chunk_content: The text content of the chunk
            metadata: Document metadata
        
        Returns:
            Dict with added 'semantic_tags' and 'chunk_category' fields
        """
        tags = []
        category = 'general'
        
        # Tag based on document type
        doc_type = metadata.doc_type or 'general'
        
        if doc_type == 'research_paper':
            section_tag = MetadataTagger._detect_research_section(chunk_content)
            if section_tag:
                tags.append(section_tag)
                category = section_tag
        
        # Add content-based tags
        for tag_name, pattern in MetadataTagger.CONTENT_TAGS.items():
            if re.search(pattern, chunk_content):
                tags.append(tag_name)
        
        # Add important markers
        if MetadataTagger._is_key_finding(chunk_content):
            tags.append('key-finding')
        
        if MetadataTagger._has_metrics(chunk_content):
            tags.append('with-metrics')
        
        # Return metadata with tags
        metadata_dict = metadata.to_dict() if hasattr(metadata, 'to_dict') else {}
        metadata_dict['semantic_tags'] = tags
        metadata_dict['chunk_category'] = category
        
        return metadata_dict
    
    @staticmethod
    def _detect_research_section(content: str) -> Optional[str]:
        """Detect which section of a research paper this is."""
        content_lower = content.lower()
        
        for section, pattern in MetadataTagger.RESEARCH_TAGS.items():
            if re.search(pattern, content_lower):
                return section
        
        return None
    
    @staticmethod
    def _is_key_finding(content: str) -> bool:
        """Check if content contains a key finding or significant result."""
        patterns = [
            r'(?i)(significant|important|remarkable|novel|unprecedented)',
            r'(?i)(\d+\%.*reduction|reduction.*\d+\%)',  # Percentage improvements
            r'(?i)(p\s*[<≤]\s*0\.0\d)',  # P-values
            r'(?i)(proved|demonstrated|showed.*statistically)',
        ]
        return any(re.search(pattern, content) for pattern in patterns)
    
    @staticmethod
    def _has_metrics(content: str) -> bool:
        """Check if content contains quantitative metrics."""
        # Look for numbers with units or percentages
        return bool(re.search(r'\d+\.?\d*\s*(%|times|fold|years|days|weeks)', content))
