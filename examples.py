"""
Examples of using the Biotech Startup RAG System
"""

from src.rag_pipeline import RAGPipeline
from pathlib import Path
import json

def example_1_process_single_document():
    """Example 1: Process a single document"""
    print("=" * 60)
    print("Example 1: Process Single Document")
    print("=" * 60)
    
    pipeline = RAGPipeline()
    
    # Process a single document
    result = pipeline.process_document("samples/sample_meeting_minutes.txt")
    
    print(f"\nDocument Type Detected: {result['doc_type']}")
    print(f"Chunks Created: {result['chunk_count']}")
    print(f"Metadata: {json.dumps(result['metadata'], indent=2)}")
    
    return pipeline

def example_2_batch_processing(pipeline):
    """Example 2: Batch process all samples"""
    print("\n" + "=" * 60)
    print("Example 2: Batch Processing")
    print("=" * 60)
    
    # Clear previous documents
    pipeline.clear()
    
    # Process all samples
    results = pipeline.process_batch("samples", pattern="*.txt")
    
    print(f"\nTotal Files: {results['total_files']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    
    for file_result in results['files']:
        if file_result.get('success'):
            print(f"  ✓ {file_result['file']}: {file_result['chunk_count']} chunks")
        else:
            print(f"  ✗ {file_result['file']}: {file_result['error']}")

def example_3_basic_search(pipeline):
    """Example 3: Basic hybrid search"""
    print("\n" + "=" * 60)
    print("Example 3: Basic Hybrid Search")
    print("=" * 60)
    
    query = "CRISPR gene therapy safety"
    results = pipeline.search(query, top_k=3)
    
    print(f"\nQuery: '{query}'")
    print(f"Results: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Combined Score: {result['combined_score']:.4f}")
        print(f"  Vector Score: {result['vector_score']:.4f}")
        print(f"  BM25 Score: {result['bm25_score']:.4f}")
        print(f"Content Preview: {result['content'][:200]}...")
        print(f"Metadata: {result['metadata']}")

def example_4_filtered_search(pipeline):
    """Example 4: Search with document type filter"""
    print("\n" + "=" * 60)
    print("Example 4: Filtered Search by Document Type")
    print("=" * 60)
    
    query = "completed tasks progress"
    
    # Search in progress reports only
    results = pipeline.search_by_type(query, doc_type="progress_report", top_k=3)
    
    print(f"\nQuery: '{query}'")
    print(f"Filter: Progress Reports Only")
    print(f"Results: {len(results)}")
    
    for i, result in enumerate(results, 1):
        doc_type = result['metadata'].get('doc_type', 'unknown')
        print(f"\n--- Result {i} ({doc_type}) ---")
        print(f"Score: {result['combined_score']:.4f}")
        print(f"Content: {result['content'][:150]}...")

def example_5_statistics(pipeline):
    """Example 5: View system statistics"""
    print("\n" + "=" * 60)
    print("Example 5: System Statistics")
    print("=" * 60)
    
    stats = pipeline.get_stats()
    
    print(f"\nTotal Documents: {stats['total_documents']}")
    print(f"Total Chunks: {stats['total_chunks']}")
    
    if stats['total_documents'] > 0:
        avg_chunks = stats['total_chunks'] / stats['total_documents']
        print(f"Average Chunks per Document: {avg_chunks:.1f}")
    
    print(f"\nDocuments by Type:")
    for doc_type, count in stats['documents_by_type'].items():
        print(f"  {doc_type}: {count}")
    
    print(f"\nProcessed Documents:")
    for doc in stats['documents']:
        print(f"  - {Path(doc['file']).name}")
        print(f"    Type: {doc['doc_type']}")
        print(f"    Chunks: {doc['chunks']}")
        print(f"    Processed: {doc['processed_at']}")

def example_6_multiple_queries(pipeline):
    """Example 6: Run multiple related searches"""
    print("\n" + "=" * 60)
    print("Example 6: Multiple Related Queries")
    print("=" * 60)
    
    queries = [
        "regulatory approval timeline",
        "manufacturing challenges",
        "safety study results",
        "action items next week",
    ]
    
    for query in queries:
        results = pipeline.search(query, top_k=2)
        print(f"\nQuery: '{query}'")
        print(f"Results: {len(results)}")
        if results:
            top_result = results[0]
            print(f"  Best match (score: {top_result['combined_score']:.3f})")
            print(f"  Content: {top_result['content'][:100]}...")

def example_7_metadata_search(pipeline):
    """Example 7: Search by metadata"""
    print("\n" + "=" * 60)
    print("Example 7: Metadata Exploration")
    print("=" * 60)
    
    stats = pipeline.get_stats()
    
    print(f"\nDocuments with metadata:")
    for doc in stats['documents']:
        print(f"\nFile: {Path(doc['file']).name}")
        print(f"Type: {doc['doc_type']}")
        print(f"Chunks: {doc['chunks']}")
        if doc.get('metadata'):
            print(f"Additional metadata:")
            for key, value in doc['metadata'].items():
                if key not in ['doc_type', 'chunk_type']:
                    print(f"  {key}: {value}")

def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║  Biotech Startup RAG System - Examples" + " " * 20 + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Create pipeline
    pipeline = RAGPipeline()
    
    # Run examples
    example_1_process_single_document()
    example_2_batch_processing(pipeline)
    example_3_basic_search(pipeline)
    example_4_filtered_search(pipeline)
    example_5_statistics(pipeline)
    example_6_multiple_queries(pipeline)
    example_7_metadata_search(pipeline)
    
    # Save state
    print("\n" + "=" * 60)
    print("Saving Pipeline State")
    print("=" * 60)
    pipeline.save_state("pipeline_state.json")
    print("✓ State saved to pipeline_state.json")
    
    print("\n✨ All examples completed successfully!")

if __name__ == "__main__":
    main()
