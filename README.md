# Ask My Docs

An AI-powered document intelligence platform that enables users to upload documents, search knowledge, and interact with them using natural language through a Retrieval-Augmented Generation (RAG) pipeline.

## Overview

Ask My Docs transforms static documents into an interactive knowledge base. Users can upload PDFs, research papers, reports, contracts, manuals, and other documents, then ask questions and receive context-aware answers grounded in the uploaded content.

The system combines semantic search, vector embeddings, and Large Language Models (LLMs) to provide accurate, explainable responses with source attribution.

## Features

### Document Processing

* PDF document upload
* Automatic text extraction
* Intelligent text chunking
* Metadata preservation

### Retrieval-Augmented Generation (RAG)

* Embedding generation
* Vector similarity search
* Context retrieval
* Grounded AI responses

### AI-Powered Question Answering

* Natural language queries
* Context-aware responses
* Multi-document search
* Conversational interaction

### Knowledge Retrieval

* Semantic document search
* Relevant chunk retrieval
* Source references
* Reduced hallucinations

## System Architecture

```text
User Query
    │
    ▼
Retriever
    │
    ▼
Vector Database
    │
    ▼
Relevant Chunks
    │
    ▼
LLM
    │
    ▼
Answer + Citations
```

## Technology Stack

### Frontend

* Streamlit

### Backend

* Python
* LangChain

### AI Components

* OpenAI GPT Models
* OpenAI Embeddings

### Vector Database

* FAISS

### Document Processing

* PyPDF

### Environment Management

* Python Virtual Environment
* python-dotenv

## Project Structure

```text
ask-my-docs/
│
├── backend/
│   ├── app.py
│   ├── rag.py
│   ├── embeddings.py
│   └── document_loader.py
│
├── frontend/
│   └── streamlit_app.py
│
├── data/
│   └── uploaded_documents/
│
├── vectorstore/
│
├── requirements.txt
├── README.md
└── .env
```

## Workflow

### Step 1: Document Upload

Users upload one or more PDF documents.

### Step 2: Text Extraction

The system extracts document content and metadata.

### Step 3: Chunking

Large documents are split into manageable chunks.

### Step 4: Embedding Generation

Each chunk is converted into vector embeddings.

### Step 5: Vector Storage

Embeddings are stored in a FAISS vector database.

### Step 6: Query Processing

User questions are embedded and matched against stored vectors.

### Step 7: Retrieval

Most relevant chunks are retrieved.

### Step 8: Answer Generation

The LLM generates responses using retrieved context.

## Installation

### Clone Repository

```bash
git clone https://github.com/SakthiQ/ask-my-docs.git
cd ask-my-docs
```

### Create Virtual Environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux / Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
```

### Run Application

Backend:

```bash
python backend/app.py
```

Frontend:

```bash
streamlit run frontend/streamlit_app.py
```

## Example Usage

Upload:

* Research Papers
* Company Policies
* Legal Contracts
* Technical Documentation
* Academic Notes
* Product Manuals

Example Questions:

* Summarize this document.
* What are the key findings?
* Explain section 4.
* What risks are identified?
* Compare topics discussed in the uploaded files.

## Future Enhancements

* Multi-document conversations
* Persistent chat history
* Role-based access control
* PostgreSQL integration
* Hybrid search
* Enterprise document management
* Agentic workflows
* MCP integration
* Citation highlighting
* Cloud deployment

## Applications

* Enterprise Knowledge Management
* Research Assistance
* Legal Document Analysis
* Academic Study Assistant
* Policy Search Systems
* Internal Documentation Search

## Learning Outcomes

This project demonstrates:

* Retrieval-Augmented Generation (RAG)
* Vector Databases
* Semantic Search
* LLM Integration
* Prompt Engineering
* Information Retrieval
* AI System Design
* Production AI Architecture

## Author

Sakthi Narayan

Computer Science Student | AI/ML Enthusiast | Full-Stack AI Developer