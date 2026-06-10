import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
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
    reasoning_log: list = []

def process_document_background(file_path: str, filename: str):
    """Worker function to process document in the background."""
    try:
        # 1. Load document
        docs = loader.load_any(file_path)
        
        # 2. Chunk document
        chunks = chunker.chunk_documents(docs)
        
        # 3. Add to vector store
        vsm.add_chunks(chunks)
        print(f"Background Task: Successfully ingested {filename}")
    except Exception as e:
        print(f"Background Task Error for {filename}: {e}")

@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Handles file upload and triggers background ingestion."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    try:
        # Save the file locally (fast)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger the heavy AI work in the background
        background_tasks.add_task(process_document_background, file_path, file.filename)
        
        return {
            "status": "processing",
            "filename": file.filename,
            "message": f"File '{file.filename}' uploaded successfully. Processing started in the background."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents():
    """Returns a list of all ingested documents from the registry."""
    return vsm.registry

@router.delete("/documents/{content_hash}")
async def delete_document(content_hash: str):
    """Deletes a document from the system using its hash."""
    try:
        vsm.delete_document(content_hash)
        return {"status": "success", "message": f"Document {content_hash} deleted."}
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
