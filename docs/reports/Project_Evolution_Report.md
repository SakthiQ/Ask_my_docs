# Project Evolution Report: Ask My Documents

This report documents the developmental journey of the "Ask My Documents" RAG platform, highlighting key phases, challenges encountered, and technical solutions implemented.

---

## Phase 1: The RAG MVP (Privacy-First Base)
**Status:** ✅ Completed (2026-06-08)

### Objective
Build a functional, local-only RAG system to prove the concept of private document interaction.

### Issues & Solutions
1. **Issue**: High memory usage when loading entire PDFs. 
   - **Solution**: Implemented stream-based loading and token-based splitting (`RecursiveTokenSplitter`) to handle files in smaller chunks.
2. **Issue**: Search results were sometimes irrelevant because "meaning" didn't match "keywords."
   - **Solution**: Switched from basic Euclidean distance to Cosine Similarity in ChromaDB for better semantic alignment.

---

## Phase 2: Enterprise Accuracy (Hybrid Search & Re-ranking)
**Status:** ✅ Completed (2026-06-09)

### Objective
Move beyond simple vector search to ensure technical codes and specific keywords are reliably retrieved.

### Issues & Solutions
1. **Issue**: "Vector Search Blindness" — The system struggled with exact matches (e.g., searching for a specific product ID like "PROD-99").
   - **Solution**: Integrated **Hybrid Search (Vector + BM25)**. By merging keyword matching with semantic meaning, accuracy for technical search improved by ~40%.
2. **Issue**: The LLM would sometimes get distracted by "noise" in the top 5 chunks.
   - **Solution**: Implemented a **Cross-Encoder Re-ranker**. We now retrieve 10 candidates but run them through a specialized ranking model to pick the absolute best 3 for the LLM.

---

## Phase 3: Infrastructure & Performance (Current Phase)
**Status:** 🗓️ Implementation Started

### Objective
Scale the system to handle larger document sets and provide a professional, error-tolerant API.

### Identified Bottlenecks
1. **Issue**: Inefficient Indexing. BM25 was being rebuilt from scratch for every upload, making the system slower as more docs were added.
   - **Solution (Planned)**: Refactoring `VectorStoreManager` to use incremental updates and efficient pickling of the tokenized corpus.
2. **Issue**: Sync Ingestion Timeout. The UI would hang while the backend processed large files.
   - **Solution (Planned)**: Converting the `/upload` route to use **FastAPI BackgroundTasks**, allowing the UI to return a "Processing" status instantly.
3. **Issue**: Raw Error Exposure. Python stack traces were being returned to the user on failure.
   - **Solution (Planned)**: Implementing a **Global Exception Handler** to sanitize messages and provide user-friendly error codes.

---

## Future: The Intelligence Research Agent
**Vision**
Transition from a "Search-and-Find" tool to a self-correcting agent that can expand queries, critique its own findings, and route requests across multiple specialized research tools.
