import os
import pickle
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi
from .embedder import DocumentEmbedder

class VectorStoreManager:
    """Manages Hybrid Search (Vector + BM25) with Atomic Transactions and Hashing."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.registry_path = os.path.join(persist_directory, "document_registry.json")
        self.bm25_path = os.path.join(persist_directory, "bm25_index.pkl")
        self.embedder = DocumentEmbedder()
        self.strategy_version = "v1.0" # Current chunking/embedding strategy
        
        # 1. Initialize Vector Store (Chroma)
        self.vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedder.client,
            collection_name="document_collection"
        )
        
        # 2. Initialize Hashing & BM25 members
        self.registry = self._load_registry()
        self.bm25 = None
        self.chunks_cache = [] 
        self.tokenized_corpus = []
        self._load_bm25()

    def _calculate_hash(self, text: str) -> str:
        """Generates SHA-256 hash of the content."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _load_registry(self) -> Dict[str, Any]:
        """Loads the document registry from disk."""
        if os.path.exists(self.registry_path):
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_registry(self):
        """Saves the document registry to disk."""
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=4)

    def _tokenize(self, text: str) -> List[str]:
        return text.lower().split()

    def _load_bm25(self):
        """Loads BM25 index and tokenized corpus from disk."""
        if os.path.exists(self.bm25_path):
            try:
                with open(self.bm25_path, "rb") as f:
                    data = pickle.load(f)
                    self.bm25 = data["index"]
                    self.chunks_cache = data["chunks"]
                    self.tokenized_corpus = data.get("tokenized_corpus", [])
                logger.info(f"Loaded BM25 index with {len(self.chunks_cache)} chunks.")
            except Exception as e:
                logger.error(f"Failed to load BM25 index: {e}")
                self.chunks_cache = []
                self.tokenized_corpus = []

    def _save_bm25(self):
        """Saves BM25 index and tokenized corpus to disk."""
        try:
            with open(self.bm25_path, "wb") as f:
                pickle.dump({
                    "index": self.bm25, 
                    "chunks": self.chunks_cache,
                    "tokenized_corpus": self.tokenized_corpus
                }, f)
            logger.debug("BM25 index saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save BM25 index: {e}")

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        """Adds chunks with content hashing and registry updates."""
        if not chunks:
            return

        # 1. Calculate Content Hash for the entire document (using first chunk's metadata source as key)
        # In this implementation, we assume all chunks belong to the same document
        source_name = chunks[0]["metadata"].get("source", "unknown")
        full_text = "".join([c["content"] for c in chunks])
        content_hash = self._calculate_hash(full_text)

        # 2. Check Registry for Duplicates
        if content_hash in self.registry:
            logger.info(f"Document '{source_name}' (Hash: {content_hash[:8]}) already exists. Skipping.")
            return

        # 3. New Document - Attempt Atomic Ingestion
        texts = [c["content"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        ids = [f"{content_hash}_{i}" for i in range(len(chunks))]
        
        try:
            # PHASE 1: Vector Ingestion (Heavy AI Work)
            self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            
            try:
                # PHASE 2: Logic Ingestion (BM25 & Registry)
                new_tokens = [self._tokenize(c["content"]) for c in chunks]
                
                # Update memory
                self.chunks_cache.extend(chunks)
                self.tokenized_corpus.extend(new_tokens)
                
                # Rebuild and Persist
                self.bm25 = BM25Okapi(self.tokenized_corpus)
                self._save_bm25()

                self.registry[content_hash] = {
                    "filename": source_name,
                    "chunk_count": len(chunks),
                    "ingested_at": datetime.now().isoformat(),
                    "strategy_version": self.strategy_version,
                    "ids": ids
                }
                self._save_registry()
                logger.info(f"Atomic success: '{source_name}' registered.")

            except Exception as e:
                # PHASE 3: ROLLBACK (Chroma partial sync)
                logger.error(f"Logic failure during ingestion. Rolling back Vector Store: {e}")
                self.vector_store.delete(ids=ids)
                raise e

        except Exception as e:
            logger.error(f"Incomplete Ingestion for '{source_name}': {e}")
            raise e

    def delete_document(self, content_hash: str):
        """Removes a document from both Chroma and BM25 using its hash."""
        if content_hash not in self.registry:
            logger.error(f"Hash {content_hash} not found in registry.")
            return

        doc_data = self.registry[content_hash]
        ids_to_remove = doc_data["ids"]

        # 1. Remove from Chroma
        try:
            self.vector_store.delete(ids=ids_to_remove)
        except Exception as e:
            logger.error(f"Failed to delete from Chroma: {e}")

        # 2. Clean BM25 Cache and Corpus
        # We find indices of chunks that AREN'T in the deleted set
        remaining_chunks = []
        remaining_tokens = []
        for chunk, tokens in zip(self.chunks_cache, self.tokenized_corpus):
            # If chunk is from this document, skip it
            if chunk["metadata"].get("source") == doc_data["filename"]:
                 continue
            remaining_chunks.append(chunk)
            remaining_tokens.append(tokens)
        
        self.chunks_cache = remaining_chunks
        self.tokenized_corpus = remaining_tokens
        
        # 3. Rebuild BM25 from clean corpus
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None
        
        self._save_bm25()

        # 4. Remove from Registry
        del self.registry[content_hash]
        self._save_registry()
        logger.info(f"Document '{doc_data['filename']}' successfully purged from system.")

    def hybrid_search(self, query: str, k: int = 4, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Combines Vector and BM25 results with optional metadata filtering."""
        # 1. Get Vector Results (Filtered)
        vector_results = self.vector_store.similarity_search(query, k=k*2, filter=filter)
        
        # 2. Get BM25 Results
        # Note: rank_bm25 doesn't natively support filtering easily without custom logic.
        # We will filter the chunks_cache first if filter is provided.
        tokenized_query = self._tokenize(query)
        
        target_chunks = self.chunks_cache
        target_tokens = self.tokenized_corpus
        
        if filter:
            # Simple metadata filtering for BM25
            filtered_indices = [
                i for i, c in enumerate(self.chunks_cache)
                if all(c["metadata"].get(k) == v for k, v in filter.items())
            ]
            target_chunks = [self.chunks_cache[i] for i in filtered_indices]
            target_tokens = [self.tokenized_corpus[i] for i in filtered_indices]
            
            if not target_chunks:
                # Fallback to vector results only if filter matches nothing in BM25
                return [{"content": res.page_content, "metadata": res.metadata} for res in vector_results[:k]]
            
            # Re-run BM25 on filtered subset
            temp_bm25 = BM25Okapi(target_tokens)
            bm25_scores = temp_bm25.get_scores(tokenized_query)
        else:
            bm25_scores = self.bm25.get_scores(tokenized_query) if self.bm25 else []
        
        # Pair chunks with scores and sort
        bm25_results = sorted(
            zip(target_chunks, bm25_scores),
            key=lambda x: x[1],
            reverse=True
        )[:k*2] if any(bm25_scores) else []

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

    def search(self, query: str, k: int = 4, filter: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Fallback to hybrid search with filtering."""
        if self.bm25:
            return self.hybrid_search(query, k, filter)
        return self.search_vector_only(query, k, filter)

    def search_vector_only(self, query: str, k: int = 4, filter: Dict[str, Any] = None):
        results = self.vector_store.similarity_search(query, k=k, filter=filter)
        return [{"content": res.page_content, "metadata": res.metadata} for res in results]
