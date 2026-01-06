"""Biotech Startup RAG System"""

__version__ = "0.1.0"
__author__ = "BioGen Therapeutics"

from src.rag_pipeline import RAGPipeline
from src.config import settings

__all__ = ["RAGPipeline", "settings"]
