import os
import pickle
from typing import List, Dict, Any
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi
from .embedder import DocumentEmbedder

class VectorStoreManager:
    """Manages Hybrid Search (Vector + BM25)."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.bm25_path = os.path.join(persist_directory, "bm25_index.pkl")
        self.embedder = DocumentEmbedder()
        
        # 1. Initialize Vector Store (Chroma)
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedder.client,
            collection_name="document_collection"
        )
        
        # 2. Initialize BM25 members
        self.bm25 = None
        self.chunks_cache = [] # Stores raw chunks for BM25 retrieval
        self._load_bm25()

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def _load_bm25(self):
        """Loads BM25 index from disk if it exists."""
        if os.path.exists(self.bm25_path):
            with open(self.bm25_path, "rb") as f:
                data = pickle.load(f)
                self.bm25 = data["index"]
                self.chunks_cache = data["chunks"]

    def _save_bm25(self):
        """Saves BM25 index to disk."""
        with open(self.bm25_path, "wb") as f:
            pickle.dump({"index": self.bm25, "chunks": self.chunks_cache}, f)

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Adds chunks to BOTH Vector Store and BM25 index."""
        # Add to Chroma
        texts = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [f"{m['source']}_{m['chunk_id']}" for m in metadatas]
        self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)

        # Update BM25
        self.chunks_cache.extend(chunks)
        tokenized_corpus = [self._tokenize(c["content"]) for c in self.chunks_cache]
        self.bm25 = BM25Okapi(tokenized_corpus)
        self._save_bm25()

    def hybrid_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Combines Vector and BM25 results."""
        # 1. Get Vector Results
        vector_results = self.vector_store.similarity_search(query, k=k*2)
        
        # 2. Get BM25 Results
        tokenized_query = self._tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Pair chunks with scores and sort
        bm25_results = sorted(
            zip(self.chunks_cache, bm25_scores),
            key=lambda x: x[1],
            reverse=True
        )[:k*2]

        # 3. Simple Fusion: Combine and take unique top results
        # In a real app, you'd use RRF, but this is a great start!
        seen_content = set()
        combined = []
        
        # Alternate between them to give equal weight
        for v_res, (b_res, b_score) in zip(vector_results, bm25_results):
            if v_res.page_content not in seen_content:
                combined.append({"content": v_res.page_content, "metadata": v_res.metadata})
                seen_content.add(v_res.page_content)
            
            if b_res["content"] not in seen_content:
                combined.append(b_res)
                seen_content.add(b_res["content"])

        return combined[:k]

    def search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Fallback to hybrid search."""
        if self.bm25:
            return self.hybrid_search(query, k)
        return self.search_vector_only(query, k)

    def search_vector_only(self, query: str, k: int = 4):
        results = self.vector_store.similarity_search(query, k=k)
        return [{"content": res.page_content, "metadata": res.metadata} for res in results]
