from typing import List
from langchain_community.embeddings import HuggingFaceEmbeddings

class DocumentEmbedder:
    """Handles converting text chunks into numerical vector embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # This model runs locally on your CPU/GPU
        # The first time you run this, it will download (~80MB)
        self.client = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'}, # Change to 'cuda' if you have an NVIDIA GPU
            encode_kwargs={'normalize_embeddings': True} # Better for cosine similarity
        )

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single string (the user's question)."""
        return self.client.embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of strings (the document chunks)."""
        return self.client.embed_documents(texts)

# Example Usage
if __name__ == "__main__":
    embedder = DocumentEmbedder()
    # vector = embedder.embed_query("How do I apply for leave?")
    # print(len(vector)) # Should be 384
