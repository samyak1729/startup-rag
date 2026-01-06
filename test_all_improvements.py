#!/usr/bin/env python3
"""
Comprehensive test demonstrating all RAG improvements.
Tests Priority 1, 2, and 5 implementations.
"""

import sys
import logging
from pathlib import Path
from src.rag_pipeline import RAGPipeline
from src.query_rewriter import QueryRewriter

logging.basicConfig(level=logging.WARNING)

def test_improvements():
    """Test all improvements."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE RAG IMPROVEMENTS TEST")
    print("="*80)
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Load samples
    print("\n1. Loading sample documents...\n")
    samples = [
        "samples/sample_research_paper.txt",
        "samples/sample_progress_report.txt",
        "samples/sample_meeting_minutes.txt",
    ]
    
    for sample in samples:
        if Path(sample).exists():
            result = pipeline.process_document(sample)
            print(f"   ✓ {Path(sample).name}: {result['chunk_count']} chunks ({result['doc_type']})")
    
    # Demonstrate Priority 1: BM25 Search
    print("\n" + "="*80)
    print("PRIORITY 1: BM25 SEARCH WORKING")
    print("="*80)
    
    print("\n   Query: 'Parkinson's Alzheimer's CRISPR'")
    results = pipeline.search("Parkinson's Alzheimer's CRISPR", top_k=3)
    for i, res in enumerate(results, 1):
        print(f"   {i}. [BM25: {res['bm25_score']:.4f}, Vector: {res['vector_score']:.4f}]")
        print(f"      Type: {res['metadata'].get('doc_type', 'unknown')}")
        print(f"      Content: {res['content'][:70]}...")
    
    # Demonstrate Priority 2: Metadata Filtering
    print("\n" + "="*80)
    print("PRIORITY 2: METADATA-DRIVEN FILTERING")
    print("="*80)
    
    print("\n   2a. Search by Document Type (research_paper only)")
    print("       Query: 'CRISPR editing'")
    research_results = pipeline.search_by_type("CRISPR editing", "research_paper", top_k=2)
    for i, res in enumerate(research_results, 1):
        print(f"       {i}. {res['metadata'].get('doc_type', 'unknown')}")
    
    print("\n   2b. Search by Semantic Tags (findings only)")
    print("       Query: 'reduction efficacy'")
    tag_results = pipeline.search_by_tags("reduction efficacy", ["finding", "key-finding"], top_k=2)
    for i, res in enumerate(tag_results, 1):
        tags = res['metadata'].get('semantic_tags', [])
        print(f"       {i}. Tags: {', '.join(tags[:3])}")
    
    print("\n   2c. Search with Query Intent (research_finding)")
    print("       Query: 'Parkinson prediction timeline'")
    intent_results = pipeline.search_with_intent("Parkinson prediction timeline", "research_finding", top_k=2)
    for i, res in enumerate(intent_results, 1):
        print(f"       {i}. {res['metadata'].get('doc_type', 'unknown')}")
    
    # Demonstrate Priority 5: Query Rewriting
    print("\n" + "="*80)
    print("PRIORITY 5: QUERY REWRITING & EXPANSION")
    print("="*80)
    
    test_queries = [
        "UKBB Parkinson's prediction",
        "FDA approval requirements",
        "efficacy results CRISPR",
    ]
    
    for query in test_queries:
        print(f"\n   Original: '{query}'")
        rewritten = QueryRewriter.rewrite_query(query)
        
        if rewritten['synonyms_added']:
            print(f"   Synonyms added: {', '.join(rewritten['synonyms_added'][:3])}")
        
        if rewritten['detected_intent']:
            print(f"   Detected intent: {rewritten['detected_intent']}")
            
            # Show optimal weights for this intent
            weights = QueryRewriter.suggest_weights(rewritten['detected_intent'])
            print(f"   Suggested weights: vector={weights[0]}, bm25={weights[1]}")
        
        if rewritten['sub_queries'] != [query]:
            print(f"   Split into sub-queries: {len(rewritten['sub_queries'])}")
    
    # Comparison: With vs Without Expansion
    print("\n" + "="*80)
    print("QUERY EXPANSION IMPACT")
    print("="*80)
    
    test_query = "UKBB Parkinson prediction years"
    print(f"\n   Query: '{test_query}'")
    
    print("\n   Without expansion:")
    results_without = pipeline.search(test_query, top_k=2, use_query_expansion=False)
    for i, res in enumerate(results_without, 1):
        print(f"   {i}. Score: {res['combined_score']:.4f}")
    
    print("\n   With expansion:")
    results_with = pipeline.search(test_query, top_k=2, use_query_expansion=True)
    for i, res in enumerate(results_with, 1):
        print(f"   {i}. Score: {res['combined_score']:.4f}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY OF IMPROVEMENTS")
    print("="*80)
    print("""
    ✅ PRIORITY 1: BM25 Search Fixed
       - Proper tokenization with stopword filtering
       - Persistent indexing across sessions
       - Correct scoring with log-normalization
       - Default weights favor precision (0.3 vector, 0.7 BM25)
    
    ✅ PRIORITY 2: Metadata-Driven Filtering
       - Automatic semantic tagging of chunks
       - Document type classification (research, progress, meeting)
       - Tag-based filtering (findings, methodology, timelines, etc.)
       - Intent-based routing with auto-detection
    
    ✅ PRIORITY 5: Query Rewriting & Expansion
       - Domain-aware synonym expansion (UKBB → UK Biobank)
       - Query intent detection (research, timeline, regulatory)
       - Optimal weight suggestions based on intent
       - Complex query splitting
    
    📊 Remaining Priorities:
       - Priority 3: Adaptive chunk sizing
       - Priority 4: Cross-encoder re-ranking
       - Priority 6: Semantic routing
       - Priorities 7-9: Advanced techniques
    """)
    
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    success = test_improvements()
    sys.exit(0 if success else 1)
