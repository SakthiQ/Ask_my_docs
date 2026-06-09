import os
import yaml
from typing import Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .vectorstore import VectorStoreManager
from .reranker import DocumentReranker

class RAGEngine:
    """The Central Brain: Connects Hybrid Search, Re-ranking, and LLM Generation."""

    def __init__(self):
        self.vsm = VectorStoreManager()
        self.reranker = DocumentReranker()
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3")
        self.threshold = 0.0  # Minimum relevance score

        # Initialize the local LLM via Ollama
        self.llm = ChatOllama(model=self.model_name, temperature=0)

        # Load prompt from YAML
        self.prompt = self._load_prompt("prompts/rag_v1.yaml")

    def _load_prompt(self, path: str) -> ChatPromptTemplate:
        """Loads prompt template from a YAML file."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            return ChatPromptTemplate.from_template(config["template"])
        else:
            # Fallback prompt if YAML is missing
            return ChatPromptTemplate.from_template(
                "Answer the question based on the context.\n"
                "Context: {context}\nQuestion: {question}\nAnswer:"
            )

    def query(self, question: str) -> Dict[str, Any]:
        """Full RAG pipeline: Hybrid Search -> Re-rank -> Generate."""

        # 1. Hybrid Search (Vector + BM25) - Get 10 candidates
        initial_results = self.vsm.search(question, k=10)

        if not initial_results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "citations": []
            }

        # 2. Re-rank - Pick the best 3
        reranked = self.reranker.rerank(question, initial_results, top_n=3)

        # 3. Threshold Check - Is the best result actually relevant?
        best_score = max([c.get("rerank_score", -10) for c in reranked])
        if best_score < self.threshold:
            return {
                "answer": "I'm sorry, I cannot find any relevant information in the uploaded documents to answer that question.",
                "citations": []
            }

        # 4. Generate Answer using LLM
        context_text = "\n\n".join([r["content"] for r in reranked])
        chain = self.prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context_text, "question": question})

        # 5. Format Citations
        citations = []
        for r in reranked:
            citations.append({
                "source": r["metadata"].get("source", "Unknown"),
                "page": r["metadata"].get("page", "N/A"),
                "relevance_score": round(r.get("rerank_score", 0), 4)
            })

        return {
            "answer": answer,
            "citations": citations
        }
