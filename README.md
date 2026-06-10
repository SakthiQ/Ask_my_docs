# Ask My Documents – Local-Model RAG Platform
![GitHub License](https://img.shields.io/github/license/SakthiQ/ask-my-docs)  
![Python](https://img.shields.io/badge/python-3.11%2B-blue)  
![Status](https://img.shields.io/badge/status-beta-orange)

---

## 🎯 Overview
**Ask My Documents** is a privacy-first Retrieval-Augmented Generation (RAG) system that lets users upload PDFs, DOCX, or Markdown files, ask natural-language questions, and receive answers **backed by exact citations** (file name, page, paragraph).  

All processing runs **locally** using a small embedding model (`all-MiniLM-L6-v2`) and a local LLM served by **Ollama** (e.g., `llama3`). No external API keys are required beyond the optional OpenAI key for fallback.

---

## 🏗️ Architecture
```mermaid
flowchart TD
    subgraph User
        Q[User Question]
        U[Upload Document]
    end
    subgraph "Agentic Research Layer (Phase 5)"
        R[Router: Normal vs HyDE]
        MQ[Multi-Query Expansion]
        AL[Corrective Loop / Critique]
        Reason[Reasoning Trace UI]
    end
    subgraph Backend
        VS[Vector Store / Hybrid Search]
        RK[Cross-Encoder Rerank]
        L[LLM (Ollama)]
        A[Answer + Citations]
    end
    
    Q --> R
    R --> MQ
    MQ --> VS
    VS --> RK
    RK --> AL
    AL -->|Insufficient| MQ
    AL -->|Sufficient| L
    L --> A
    A --> Reason
    
    U --> DL[Loader] --> CH[Chunker] --> EB[Embedder] --> VS
    
    style User fill:#f9f9f9,stroke:#333
    style "Agentic Research Layer (Phase 5)" fill:#fff4e6,stroke:#d9480f
    style Backend fill:#e6f7ff,stroke:#0050b3
```

---

## ✨ Features
- 🤖 **Agentic Research Loops**: Self-critiquing cycles that verify answer quality and perform corrective searches if info is missing.
- 🛣️ **Smart Routing (HyDE)**: Automatically detects conceptual questions and generates "Hypothetical Documents" for better retrieval.
- 🧠 **Reasoning Trace UI**: Real-time visibility into the agent's internal steps (Planning -> Retrieval -> Critique).
- 🔍 **Hybrid Search & Reranking**: Combines Vector (Chroma) + Keyword (BM25) search with a Cross-Encoder for maximum accuracy.
- 📑 **Exact Citations**: Answers include file names, page numbers, and relevance scores.
- 🔒 **Privacy First**: 100% local processing; all data stays on your machine.

---

## 🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Loguru, Tenacity |
| **Vector DB** | ChromaDB & BM25Okapi |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **LLM Inference** | Ollama (Llama 3) |
| **UI** | Streamlit |

---

## 🚀 Getting Started

### Prerequisites
1. **Python 3.11+** (recommended via `pyenv` or the system installer)
2. **Ollama** – download from [https://ollama.com/download](https://ollama.com/download) and install.
3. Pull a local model (e.g., `llama3`):
   ```powershell
   ollama pull llama3
   ```
4. (Optional) **GPU** – if you have an NVIDIA GPU, set `device='cuda'` in `embedder.py`.

### Installation
```powershell
# Clone the repo
git clone https://github.com/SakthiQ/ask-my-docs.git
cd ask-my-docs

# Create a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```text
# If you ever want to fall back to OpenAI embeddings (optional)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
# Ollama model name (default is llama3)
OLLAMA_MODEL=llama3
```

---

## 📚 Usage

### 1️⃣ Start the API server
```powershell
uvicorn app.main:app --reload
```
The server will be reachable at `http://127.0.0.1:8000`.

### 2️⃣ Upload a document
`POST /upload` with `multipart/form-data` (field name `file`). Example using `curl`:
```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@/path/to/Policy.pdf"
```
You will see a JSON response confirming ingestion.

### 3️⃣ Ask a question
`POST /query` with JSON body `{ "question": "What is the leave policy?" }`
```bash
curl -X POST "http://127.0.0.1:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the leave policy?"}'
```
Response example:
```json
{
  "answer": "Employees receive 20 paid leave days annually.",
  "citations": [
    {
      "source": "Policy.pdf",
      "page": 4,
      "paragraph": 2
    }
  ]
}
```

---

## 📁 Project Structure
```text
ask-my-docs/
│
├─ app/
│   ├─ main.py          # FastAPI entry point
│   ├─ routes.py        # /upload & /query endpoints
│   └─ rag/
│       ├─ loader.py    # PDF/DOCX/MD extraction
│       ├─ chunker.py   # Token-aware recursive splitter
│       ├─ embedder.py  # Local sentence-transformer embeddings
│       ├─ vectorstore.py
│       └─ engine.py    # RAG Orchestration (Chroma + Ollama)
│
├─ frontend/
│   └─ streamlit_app.py # Streamlit Chat UI
│
├─ data/                # Uploaded files
├─ tests/               # Pytest suite
├─ requirements.txt
└─ README.md
```

---

## 🧪 Testing
A minimal sanity-check script is provided in `test_ingestion.py`. Run it with:
```powershell
python test_ingestion.py
```
It will:
1. Load a sample PDF (place any PDF in `data/` and update the path).
2. Chunk, embed, and store the vectors.
3. Perform a similarity search and print the top result.

---

## 📈 Future Roadmap
- [x] **Hybrid Search** (Vector + BM25)
- [x] **Re-ranking** (Cross-Encoder)
- [x] **Agentic Reasoning** (Critique Loops)
- [x] **Observeability** (Reasoning Trace)
- [ ] **Evaluation Suite** – RAGAS / DeepEval integration.
- [ ] **Docker Deployment** – Complete containerization for easy scaling.
- [ ] **Knowledge Graph** – GraphRAG integration for complex relationship discovery.


---

## Acknowledgements
- **LangChain** – for the elegant text-splitting utilities.
- **ChromaDB** – for a lightweight, pure-Python vector store.
- **Ollama** – for making local LLM inference painless.
- **Sentence-Transformers** – for the fast embedding model.
