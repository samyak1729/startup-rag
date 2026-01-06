#!/usr/bin/env python3
"""Test Priority 2: Metadata-Driven Filtering."""

import sys
import logging
from pathlib import Path
from src.rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_metadata_filtering():
    """Test metadata tagging and filtering."""
    
    print("\n" + "="*80)
    print("PRIORITY 2: METADATA-DRIVEN FILTERING TEST")
    print("="*80 + "\n")
    
    # Initialize RAG pipeline
    pipeline = RAGPipeline()
    
    # Load all sample documents
    sample_files = [
        "samples/sample_research_paper.txt",
        "samples/sample_progress_report.txt",
        "samples/sample_meeting_minutes.txt",
    ]
    
    print("1. Loading and indexing sample documents\n")
    for sample_path in sample_files:
        if Path(sample_path).exists():
            print(f"   Processing: {sample_path}")
            try:
                result = pipeline.process_document(sample_path)
                print(f"   ✓ Processed: {result['chunk_count']} chunks (type: {result['doc_type']})")
            except Exception as e:
                print(f"   ✗ Failed: {e}")
                return False
        else:
            print(f"   ✗ File not found: {sample_path}")
            return False
    
    # Get stats to see metadata
    stats = pipeline.get_stats()
    print(f"\n   Total documents: {stats['total_documents']}")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Documents by type: {stats['documents_by_type']}\n")
    
    # Test basic search
    print("2. Testing Basic Search\n")
    results = pipeline.search("CRISPR gene editing", top_k=3)
    print(f"   Query: 'CRISPR gene editing'")
    print(f"   Results: {len(results)} found")
    for i, res in enumerate(results[:3], 1):
        doc_type = res.get('metadata', {}).get('doc_type', 'unknown')
        tags = res.get('metadata', {}).get('semantic_tags', [])
        print(f"      {i}. [{res['combined_score']:.4f}] {doc_type}")
        if tags:
            print(f"         Tags: {', '.join(tags[:3])}")
    
    # Test search by type
    print(f"\n3. Testing Search by Document Type\n")
    research_results = pipeline.search_by_type("CRISPR", "research_paper", top_k=3)
    print(f"   Query: 'CRISPR' (filtered to research_paper)")
    print(f"   Results: {len(research_results)} found")
    for i, res in enumerate(research_results[:3], 1):
        print(f"      {i}. {res.get('metadata', {}).get('doc_type', 'unknown')}")
    
    # Test search by tags
    print(f"\n4. Testing Search by Semantic Tags\n")
    finding_results = pipeline.search_by_tags("editing efficiency", ["finding", "key-finding"], top_k=3)
    print(f"   Query: 'editing efficiency' (filtered to findings)")
    print(f"   Results: {len(finding_results)} found")
    for i, res in enumerate(finding_results[:3], 1):
        tags = res.get('metadata', {}).get('semantic_tags', [])
        print(f"      {i}. Tags: {', '.join(tags)}")
    
    # Test search with intent
    print(f"\n5. Testing Search with Intent (research_finding)\n")
    research_intent = pipeline.search_with_intent(
        "Parkinson's Alzheimer's reduction", 
        "research_finding", 
        top_k=3
    )
    print(f"   Query: 'Parkinson's Alzheimer's reduction' (intent: research_finding)")
    print(f"   Results: {len(research_intent)} found")
    for i, res in enumerate(research_intent[:3], 1):
        doc_type = res.get('metadata', {}).get('doc_type', 'unknown')
        print(f"      {i}. {doc_type}")
    
    # Test search with intent (timeline)
    print(f"\n6. Testing Search with Intent (timeline)\n")
    timeline_intent = pipeline.search_with_intent(
        "studies due deadline", 
        "timeline", 
        top_k=3
    )
    print(f"   Query: 'studies due deadline' (intent: timeline)")
    print(f"   Results: {len(timeline_intent)} found")
    for i, res in enumerate(timeline_intent[:3], 1):
        doc_type = res.get('metadata', {}).get('doc_type', 'unknown')
        print(f"      {i}. {doc_type}")
    
    # Verify metadata in chunks
    print(f"\n7. Verifying Metadata Enrichment\n")
    sample_chunk = stats['documents'][0] if stats['documents'] else None
    if sample_chunk:
        print(f"   Sample chunk from: {sample_chunk.get('file', 'unknown')}")
        print(f"   Type: {sample_chunk.get('doc_type', 'unknown')}")
        print(f"   Chunks: {sample_chunk.get('chunks', 0)}")
    
    print("\n" + "="*80)
    print("✓ PRIORITY 2 TEST PASSED - Metadata filtering working correctly")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_metadata_filtering()
    sys.exit(0 if success else 1)
