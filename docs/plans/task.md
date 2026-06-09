# Task: Phase 2 - Advanced Retrieval & Intelligence

## Status: [/] In Progress

### [ ] Step 2.1: Hybrid Search Integration
- [ ] Install `rank_bm25` dependency
- [ ] Add BM25 indexing to `vectorstore.py`
- [ ] Implement Reciprocal Rank Fusion (RRF) logic

### [ ] Step 2.2: Re-ranking (Performance Layer)
- [ ] Add `reranker.py` with Cross-Encoder support
- [ ] Update `responder.py` to use re-ranked chunks

### [ ] Step 2.3: Prompt Management
- [ ] Create `prompts/` directory
- [ ] Externalize prompts to YAML
- [ ] implement `PromptLoader` utility

### [ ] Step 2.4: Hallucination Prevention
- [ ] Define "Self-Correction" prompt
- [ ] Implement verification logic in `responder.py`
