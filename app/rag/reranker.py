from typing import List, Dict, Any
from sentence_transformers import CrossEncoder

class DocumentReranker:
    """Uses a Cross-Encoder to re-rank chunks for maximum relevance."""

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        # This model is specifically trained for ranking pairs of (Question, Text)
        # It is about 150MB and runs locally.
        self.model = CrossEncoder(model_name, max_length=512)

    def rerank(self, query: str, chunks: List[Dict[str, Any]], top_n: int = 4) -> List[Dict[str, Any]]:
        """Scores each chunk against the query and returns the best ones."""
        if not chunks:
            return []

        # 1. Prepare pairs for the model: [(query, chunk1), (query, chunk2), ...]
        pairs = [[query, chunk["content"]] for chunk in chunks]
        
        # 2. Get scores
        scores = self.model.predict(pairs)
        
        # 3. Attach scores to chunks and sort
        for i, score in enumerate(scores):
            chunks[i]["rerank_score"] = float(score)
            
        # Sort by score descending (highest first)
        reranked_chunks = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
        
        return reranked_chunks[:top_n]

# Example Usage
if __name__ == "__main__":
    print("Reranker is ready.")
