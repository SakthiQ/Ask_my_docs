from typing import List, Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker: # <--- Check this name!
    def __init__(self, chunk_size: int = 600, chunk_overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def chunk_documents(self, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        for doc in docs:
            text_splits = self.splitter.split_text(doc["content"])
            for i, split in enumerate(text_splits):
                chunk_metadata = doc["metadata"].copy()
                chunk_metadata["chunk_id"] = i
                chunks.append({
                    "content": split,
                    "metadata": chunk_metadata
                })
        return chunks
