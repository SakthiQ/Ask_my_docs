import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from .rag.loader import DocumentLoader
from .rag.chunker import DocumentChunker
from .rag.vectorstore import VectorStoreManager
from .rag.engine import RAGEngine

router = APIRouter()

# Initialize components
loader = DocumentLoader()
chunker = DocumentChunker()
vsm = VectorStoreManager()
engine = RAGEngine()

# Ensure upload directory exists
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    citations: list

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Handles file upload, text extraction, and vector ingestion."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Load document
        docs = loader.load_any(file_path)
        
        # 2. Chunk document
        chunks = chunker.chunk_documents(docs)
        
        # 3. Add to vector store
        vsm.add_chunks(chunks)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks": len(chunks),
            "message": f"Successfully ingested {file.filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """Processes a natural language query and returns an answer with citations."""
    try:
        response = engine.query(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
