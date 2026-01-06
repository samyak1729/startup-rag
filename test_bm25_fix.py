#!/usr/bin/env python3
"""Test BM25 search fixes."""

import sys
import logging
from src.rag_pipeline import RAGPipeline
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_bm25_fix():
    """Test that BM25 search is working correctly."""
    
    print("\n" + "="*80)
    print("BM25 SEARCH FIX VALIDATION TEST")
    print("="*80 + "\n")
    
    # Initialize RAG pipeline
    pipeline = RAGPipeline()
    
    # Load sample research paper
    sample_path = "samples/sample_research_paper.txt"
    if not Path(sample_path).exists():
        print(f"ERROR: Sample file not found: {sample_path}")
        return False
    
    print(f"1. Processing sample document: {sample_path}")
    try:
        result = pipeline.process_document(sample_path)
        print(f"   ✓ Document processed: {result['chunk_count']} chunks")
    except Exception as e:
        print(f"   ✗ Failed to process document: {e}")
        return False
    
    # Test case 1: Search for exact keywords
    test_queries = [
        {
            "query": "Parkinson's Alzheimer's CRISPR",
            "expected_match": "should find research paper results",
            "keywords": ["CRISPR", "Parkinson", "Alzheimer"]
        },
        {
            "query": "APP gene mutation editing efficiency",
            "expected_match": "should find discussion of 94% editing",
            "keywords": ["APP", "editing", "efficiency"]
        },
        {
            "query": "amyloid-beta reduction cognitive improvement",
            "expected_match": "should find results section about 68% reduction",
            "keywords": ["amyloid", "cognitive", "reduction"]
        },
    ]
    
    print(f"\n2. Testing BM25 Search Quality\n")
    
    all_passed = True
    for i, test in enumerate(test_queries, 1):
        print(f"   Test {i}: {test['query']}")
        print(f"   Expected: {test['expected_match']}")
        
        results = pipeline.search(test['query'], top_k=5)
        
        if not results:
            print(f"   ✗ FAILED: No results returned")
            all_passed = False
            continue
        
        # Check if top result has non-zero BM25 score
        top_result = results[0]
        bm25_score = top_result.get('bm25_score', 0)
        vector_score = top_result.get('vector_score', 0)
        combined_score = top_result.get('combined_score', 0)
        
        print(f"   BM25 Score: {bm25_score:.4f}")
        print(f"   Vector Score: {vector_score:.4f}")
        print(f"   Combined Score: {combined_score:.4f}")
        
        if bm25_score == 0:
            print(f"   ✗ FAILED: BM25 score is 0 (should be > 0)")
            all_passed = False
        else:
            print(f"   ✓ PASSED: BM25 found relevant results")
        
        # Show top 3 results
        print(f"\n   Top 3 Results:")
        for j, res in enumerate(results[:3], 1):
            content_preview = res['content'][:80].replace('\n', ' ')
            print(f"      {j}. [{res['combined_score']:.4f}] {content_preview}...")
        
        print()
    
    # Test case 2: Verify keyword matching
    print(f"3. Testing Keyword Matching\n")
    
    keyword_tests = [
        ("UKBB", "UK Biobank study reference"),
        ("CRISPR", "Gene editing technology"),
        ("Parkinson", "Neurodegenerative disease"),
        ("efficacy", "Clinical outcome measurement"),
    ]
    
    for keyword, description in keyword_tests:
        print(f"   Searching for: '{keyword}' ({description})")
        results = pipeline.search(keyword, top_k=3)
        
        if results and results[0]['bm25_score'] > 0:
            print(f"   ✓ Found: BM25 score = {results[0]['bm25_score']:.4f}")
        else:
            print(f"   ✗ Not found (BM25 score = 0)")
            all_passed = False
    
    print("\n" + "="*80)
    if all_passed:
        print("✓ BM25 FIX VALIDATION PASSED")
    else:
        print("✗ BM25 FIX VALIDATION FAILED - Some tests did not pass")
    print("="*80 + "\n")
    
    return all_passed

if __name__ == "__main__":
    success = test_bm25_fix()
    sys.exit(0 if success else 1)
