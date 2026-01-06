# RAG Retrieval Quality Improvements

## Problem Statement

Exact chunks aren't being retrieved for specific queries. Example:
- **Query**: "according to ukbb research paper up-to how many years can Parkinson's be predicted"
- **Issue**: Results ranked higher are from regulatory/task documents instead of research papers
- **Root Cause**: Relevance scoring is undifferentiated across disparate document types

## Core Issues Identified

- [ ] **BM25 scoring completely broken** (all scores = 0.000)
  - Keywords aren't matching even when present in documents
  - Potential stemming/lemmatization issues
  - Vector search dominating scoring

- [ ] **Chunk-level problems**
  - Chunks are too large and mix multiple topics
  - Result 5 (correct answer) buried due to size/context dilution

- [ ] **Undifferentiated relevance scoring**
  - Regulatory blockers and research findings scored on same scale
  - Semantic similarity capturing loose connections (medical context) over topical precision

---

## Strategies to Implement (Priority Order)

### Priority 1: Fix BM25 Search
**Effort**: Low | **Impact**: High

- [ ] Debug BM25 implementation - why are all scores 0?
- [ ] Verify keyword presence in documents (e.g., "UKBB", "Parkinson's", "years", "predict")
- [ ] Implement/fix stemming and lemmatization
- [ ] Reweight BM25 vs vector search (currently vector-dominated)
- [ ] Test keyword matching on Result 5 document

**Success Metric**: BM25 scores > 0 for exact keyword matches

---

### Priority 2: Add Metadata-Driven Filtering
**Effort**: Low-Medium | **Impact**: High

- [ ] Classify documents by type (research_paper, regulatory, task_list, notes, etc.)
- [ ] Add metadata tags to chunks (research_finding, methodology, results, regulatory, etc.)
- [ ] Implement pre-filter: only search relevant document types for query intent
- [ ] For "research fact" queries, exclude regulatory/task documents before scoring

**Success Metric**: UKBB research documents ranked first for research queries

---

### Priority 3: Optimize Chunk Size and Structure
**Effort**: Medium | **Impact**: High

- [ ] Reduce chunk size - one finding per chunk, not entire sections
- [ ] Separate results from context (e.g., methodology as parent, specific finding as child)
- [ ] Add surrounding context to chunks (previous/next chunks as metadata)
- [ ] Test optimal chunk size vs. retrieval quality tradeoff

**Success Metric**: Result 5 ranked #1 with high score

---

### Priority 4: Implement Two-Stage Retrieval + Re-ranking
**Effort**: Medium-High | **Impact**: Very High

- [ ] Build re-ranker (cross-encoder or small LLM)
- [ ] Train/configure to understand query intent
- [ ] First pass: broad retrieval with current system
- [ ] Second pass: re-rank top-k results with domain-specific logic
- [ ] Implement different re-ranking strategies per query type

**Success Metric**: Precision@5 significantly improves

---

### Priority 5: Query Rewriting
**Effort**: Low | **Impact**: Medium

- [ ] Implement query expansion (add domain terms, synonyms)
- [ ] Example: "UKBB Parkinson's prediction timeline" → expand with "UK Biobank", "prospective study", "prediction window"
- [ ] Split complex queries into sub-queries
- [ ] Add explicit intent signals ("research paper says", "study shows")

**Success Metric**: Expanded queries improve retrieval for ambiguous inputs

---

### Priority 6: Semantic Routing
**Effort**: Medium | **Impact**: Medium-High

- [ ] Classify query intent automatically (research_fact, project_timeline, regulatory_info, etc.)
- [ ] Route to specialized retrievers (research DB, project docs, regulatory files)
- [ ] Apply different scoring logic per retriever
- [ ] Combine results with intent-aware scoring

**Success Metric**: Query type classification accuracy > 90%

---

### Priority 7: Query Embedding Fine-tuning
**Effort**: High | **Impact**: Medium

- [ ] Collect query-chunk pairs with manual relevance labels
- [ ] Fine-tune embedding model on labeled data
- [ ] Focus on distinguishing research context from regulatory context
- [ ] Validate on test set before deployment

**Success Metric**: Vector similarity better correlates with manual relevance judgments

---

### Priority 8: Pseudo-Relevance Feedback
**Effort**: Medium | **Impact**: Low-Medium

- [ ] ⚠️ **Only implement after Priority 1-4** (current top-k is noisy)
- [ ] Extract terms from re-ranked results
- [ ] Expand query with high-confidence terms
- [ ] Re-search with expanded query
- [ ] Risk: Can amplify errors if re-ranking not in place

**Success Metric**: Iterative refinement improves recall

---

### Priority 9: Dense Passage Retrieval with Better Context
**Effort**: Low-Medium | **Impact**: Low-Medium

- [ ] Add parent/child chunk relationships
- [ ] Include introduction/summary chunks in context
- [ ] Help embeddings understand discourse flow
- [ ] Test on complex multi-section research papers

**Success Metric**: Passages ranked with better contextual understanding

---

## Testing & Validation

### Test Cases
- [ ] Research fact lookup: "How many years can Parkinson's be predicted? (UKBB study)"
- [ ] Regulatory query: "What are current FDA approval blockers?"
- [ ] Project timeline: "When are in vivo studies due?"
- [ ] Mixed intent: "What does research say about timeline?"

### Metrics to Track
- [ ] Top-1 accuracy (is correct document in position 1?)
- [ ] Top-5 accuracy
- [ ] Mean Reciprocal Rank (MRR)
- [ ] Precision@5 and Recall@5
- [ ] Query type classification accuracy

---

## Notes

- Start with Priority 1-3 before building complex systems
- Monitor BM25 issue - this may solve many problems alone
- Document each fix with before/after metrics
- Consider sample queries from each document type for regression testing
