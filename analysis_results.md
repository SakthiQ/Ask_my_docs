# [Draft] Architecture Analysis & Performance Optimization

## Goal
To evaluate the current "Ask My Documents" RAG platform and provide recommendations for reducing processing time, improving error handling, and weighing a potential transition to a Go-based backend.

## 1. Performance Optimization (Reducing Processing Time)

The current system has several bottlenecks that slow down document ingestion and query response times.

### Current Bottlenecks
- **BM25 Re-indexing**: In `VectorStoreManager.add_chunks`, the BM25 index is rebuilt from scratch (`BM25Okapi(tokenized_corpus)`) for every new document. As more documents are added, this operation becomes quadratically slower.
- **Synchronous Ingestion**: The `/upload` endpoint waits for the entire pipeline (loading -> chunking -> embedding -> indexing) to complete before responding. For large files, this causes timeouts.
- **Model Initialization**: The LLM and Embedding models are initialized on every class instantiation if not managed correctly as singletons.
- **Redundant Reranking**: The reranker currently processes all 10 candidates from hybrid search; this can be optimized if the initial vector scores are high enough.

### Recommended Improvements
- **Incremental BM25**: Use a vector-native retrieval (like Chroma's built-in) or a more efficient BM25 implementation that supports incremental updates.
- **Asynchronous Processing**: Implement FastAPI `BackgroundTasks` so the API returns a "Processing" status immediately while ingestion happens in the background.
- **Parallel Chunk Embedding**: Use Python's `multiprocessing` or `concurrent.futures` to embed chunks in parallel (if the GPU/CPU can handle the concurrency).
- **Embeddings Caching**: Store embeddings on disk and only generate them if the file content changes.

---

## 2. Robust Backend & Error Handling

The user mentioned "errors that came just now." Likely, these are raw Python stack traces or `500 Internal Server Error` responses.

### Shortcomings
- **Raw Detail Leakage**: `HTTPException(detail=str(e))` exposes raw Python errors to the user, which is insecure and unhelpful for a non-technical user.
- **Lack of Input Validation**: Beyond basic Pydantic types, there's little validation for file types, size limits, or corrupted PDFs.
- **Missing Distributed Tracing/Logging**: There is no structured logging to identify *where* in the pipeline (Ollama, Chroma, or Python code) the failure occurred.

### Proposed Fixes
- **Custom Exception Handlers**: Implement a global exception handler in `main.py` that maps specific errors (e.g., `FileNotFoundError`, `OllamaTimeout`) to user-friendly messages.
- **Health Checks**: Add a `/health` endpoint to verify if Ollama and Chroma are actually running before attempting a query.
- **Validation Middleware**: Add middleware to check file MAGIC numbers (to ensure a .pdf is actually a PDF) and enforce size limits.

---

## 3. Go (Golang) vs. Python for RAG

The user asked if switching to Go would be faster.

### Comparison Table

| Feature | Python (Current) | Go (Golang) |
| :--- | :--- | :--- |
| **Concurrency** | Limited by Global Interpreter Lock (GIL) | **Superior** (Goroutines handle thousands of tasks) |
| **AI Ecosystem** | **Excellent** (LangChain, LlamaIndex, PyTorch, HF) | Developing (LangChainGo is less mature) |
| **Execution Speed** | Slower (Interpreted) | **Faster** (Compiled Binary) |
| **Development Speed** | High (Rapid prototyping) | Moderate (Strong typing, more boilerplate) |
| **Memory Footprint** | Large | Small |

### My Verdict
While **Go is significantly faster** for building the "pipes" (the API, file handling, and concurrency), it will **not significantly speed up the AI processing** (embeddings and LLM generation).

Most AI libraries (like ChromaDB or Ollama) are already written in C++ or Go behind the scenes. Python simply acts as the orchestrator. If you switch to Go:
- You will gain better handling of 1,000+ simultaneous uploads.
- You will lose the rich set of libraries that make advanced RAG (like Hybrid Search and Re-ranking) easy to implement and maintain.

**Recommendation**: Keep the Python backend for its AI ecosystem, but **architect it like a Go service**: use asynchronous task queues (Celery/Redis) and split the ingestion service from the query service.
