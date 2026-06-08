import os
from typing import List, Dict, Any
# pyrefly: ignore [missing-import]
from langchain_chroma import Chroma
from .embedder import DocumentEmbedder

class VectorStoreManager:
    """Manages the ChromaDB vector database."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.embedder = DocumentEmbedder()
        
        # Initialize (or load) the Chroma database
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedder.client,
            collection_name="document_collection"
        )

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Adds text chunks and their metadata to the database."""
        texts = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        # IDs help prevent duplicate chunks if you run the same file twice
        ids = [f"{m['source']}_{m['chunk_id']}" for m in metadatas]
        
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        # Chroma saves to disk automatically in newer versions.

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Searches for the top K most relevant chunks."""
        results = self.vector_store.similarity_search(query, k=k)
        
        return [
            {
                "content": res.page_content,
                "metadata": res.metadata
            }
            for res in results
        ]

# Example Usage
if __name__ == "__main__":
    vsm = VectorStoreManager()