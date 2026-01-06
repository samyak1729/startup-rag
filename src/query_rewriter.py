"""Query rewriting and expansion for improved retrieval."""

import re
from typing import Optional

class QueryRewriter:
    """Expands and rewrites queries to improve retrieval quality."""
    
    # Domain-specific synonyms for biotech
    DOMAIN_SYNONYMS = {
        'UKBB': ['UK Biobank', 'UK Biobank cohort', 'biobank'],
        'PD': ['Parkinson disease', "Parkinson's disease", 'Parkinson', 'parkinsonism'],
        'AD': ['Alzheimer disease', "Alzheimer's disease", 'Alzheimer'],
        'FDA': ['FDA approval', 'regulatory approval', 'FDA requirement'],
        'safety': ['toxicity', 'adverse effect', 'side effect', 'safety profile', 'tolerability'],
        'efficacy': ['effectiveness', 'efficiency', 'efficacy', 'clinical benefit'],
        'timeline': ['schedule', 'deadline', 'milestone', 'due date', 'target date'],
        'in vivo': ['in vivo study', 'animal model', 'preclinical'],
        'in vitro': ['in vitro study', 'cell culture', 'laboratory'],
        'CRISPR': ['CRISPR-Cas9', 'CRISPR', 'gene editing', 'genome editing'],
        'AAV': ['adeno-associated virus', 'AAV vector', 'gene therapy'],
        'prediction': ['predict', 'predictive', 'forecast', 'prognostic'],
        'reduction': ['decrease', 'improvement', 'reduction'],
        'results': ['findings', 'outcomes', 'results', 'results section'],
    }
    
    # Intent markers
    INTENT_MARKERS = {
        'research_finding': [
            'research shows', 'study found', 'paper says', 'research paper',
            'according to', 'demonstrated', 'revealed', 'showed'
        ],
        'timeline': [
            'when', 'due', 'deadline', 'schedule', 'milestone',
            'plan', 'upcoming', 'q1', 'q2', 'q3', 'q4'
        ],
        'regulatory': [
            'FDA', 'approval', 'regulatory', 'requirement', 'compliance',
            'blocker', 'requirement', 'regulation'
        ],
        'methodology': [
            'how', 'method', 'approach', 'procedure', 'technique',
            'design', 'conducted', 'performed'
        ],
    }
    
    @staticmethod
    def rewrite_query(query: str, detect_intent: bool = True) -> dict:
        """
        Rewrite and expand query.
        
        Args:
            query: Original query
            detect_intent: Whether to detect query intent
        
        Returns:
            Dict with:
            - expanded_query: Original + synonyms
            - synonyms_added: List of added terms
            - detected_intent: Detected query intent (if detect_intent=True)
            - sub_queries: Split complex queries
        """
        expanded = QueryRewriter._expand_with_synonyms(query)
        intent = QueryRewriter._detect_intent(query) if detect_intent else None
        sub_queries = QueryRewriter._split_complex_query(query)
        
        return {
            'original': query,
            'expanded': expanded,
            'expanded_query': f"{query} {' '.join(expanded)}",
            'synonyms_added': expanded,
            'detected_intent': intent,
            'sub_queries': sub_queries,
        }
    
    @staticmethod
    def _expand_with_synonyms(query: str) -> list[str]:
        """Find and add synonyms from domain knowledge."""
        added_terms = set()
        query_lower = query.lower()
        
        for term, synonyms in QueryRewriter.DOMAIN_SYNONYMS.items():
            if term.lower() in query_lower:
                # Add additional synonyms
                for syn in synonyms:
                    if syn.lower() not in query_lower:
                        added_terms.add(syn)
        
        return list(added_terms)
    
    @staticmethod
    def _detect_intent(query: str) -> Optional[str]:
        """Detect query intent from markers."""
        query_lower = query.lower()
        
        for intent, markers in QueryRewriter.INTENT_MARKERS.items():
            # Count how many markers match
            matches = sum(1 for marker in markers if marker in query_lower)
            if matches > 0:
                return intent
        
        return None
    
    @staticmethod
    def _split_complex_query(query: str) -> list[str]:
        """Split complex multi-part queries into sub-queries."""
        # Look for logical operators
        if ' and ' in query.lower():
            parts = re.split(r'\s+and\s+', query, flags=re.IGNORECASE)
            return [p.strip() for p in parts if p.strip()]
        
        # Look for multiple question marks
        if query.count('?') > 1:
            parts = query.split('?')
            return [p.strip() + '?' for p in parts if p.strip()]
        
        # Single query - return as-is
        return [query]
    
    @staticmethod
    def suggest_weights(query_intent: Optional[str]) -> tuple[float, float]:
        """
        Suggest optimal weights based on query intent.
        
        Returns:
            (vector_weight, bm25_weight)
        """
        if query_intent == 'research_finding':
            # Exact matches important for research findings
            return (0.2, 0.8)
        elif query_intent == 'timeline':
            # Exact keyword matches for dates/deadlines
            return (0.3, 0.7)
        elif query_intent == 'regulatory':
            # Keyword-based for compliance
            return (0.2, 0.8)
        elif query_intent == 'methodology':
            # More semantic matching
            return (0.5, 0.5)
        else:
            # Default balanced
            return (0.3, 0.7)

