# Ask My Documents – Local-Model RAG Platform
![GitHub License](https://img.shields.io/github/license/SakthiQ/ask-my-docs)  ![Python](https://img.shields.io/badge/python-3.14%2B-blue)  ![Status](https://img.shields.io/badge/status-beta-orange)

---

## 🎯 Overview
**Ask My Documents** is a privacy-first Retrieval-Augmented Generation (RAG) system that lets users upload PDFs, DOCX, or Markdown files, ask natural-language questions, and receive answers **backed by exact citations** (file name, page, paragraph).  

All processing runs **locally** using a small embedding model (`all-MiniLM-L6-v2`) and a local LLM served by **Ollama** (e.g., `llama3`). No external API keys are required beyond the optional OpenAI key for fallback.

---

## 🏗️ Architecture
```mermaid
flowchart LR
    subgraph User
        Q[User Question]
        U[Upload Document]
    end
    subgraph Backend
        R[Retriever] --> V[Vector DB (Chroma)]
        Q --> R
        V --> L[LLM (Ollama)]
        L --> A[Answer + Citations]
    end
    U --> D[Document Loader]
    D --> C[Chunker]
    C --> E[Embedder]
    E --> V
    style User fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Backend fill:#e6f7ff,stroke:#333,stroke-width:1px
```

---

## ✨ Features (MVP)
- 📂 Upload PDFs, DOCX, Markdown
- 🧹 Text extraction with page/paragraph metadata
- 📏 Token-aware recursive chunking (600-token chunks, 100-token overlap)
- 🔗 Local embeddings (`all-MiniLM-L6-v2`)
- 📦 Persistent vector store (ChromaDB)
- 🤖 Local LLM inference via Ollama (e.g., `llama3`)
- 📑 Answers include **exact source citations**

---

## 🛠️ Tech Stack
| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI, Uvicorn |
| **Vector DB** | ChromaDB (local) |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **LLM** | Ollama (any local model, default `llama3`) |
| **Document Parsing** | PyPDF, python-docx |
| **Chunking** | LangChain RecursiveCharacterTextSplitter (token-aware) |
| **Testing** | Pytest |

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

## 📈 Next Steps (Phase 2 & 3)
- **Hybrid Search** – combine BM25 keyword search with vector similarity.
- **Re-ranking** – use a cross-encoder (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`).
- **Hallucination Guard** – verify that citations exist in the retrieved chunks.
- **Prompt Versioning** – store prompts in `prompts/` as YAML.
- **Evaluation Suite** – RAGAS, DeepEval, and a golden QA dataset.
- **Docker & CI/CD** – containerise the service and add GitHub Actions for automated testing.


---

## Acknowledgements
- **LangChain** – for the elegant text-splitting utilities.
- **ChromaDB** – for a lightweight, pure-Python vector store.
- **Ollama** – for making local LLM inference painless.
- **Sentence-Transformers** – for the fast embedding model.
