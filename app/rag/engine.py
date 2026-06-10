import os
import yaml
import json
from typing import Dict, Any, List, Optional
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from .vectorstore import VectorStoreManager
from .reranker import DocumentReranker

class RAGEngine:
    """The Central Brain: Orchestrates Agentic Loops, Router, and Research."""

    def __init__(self):
        self.vsm = VectorStoreManager()
        self.reranker = DocumentReranker()
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3")
        self.llm = ChatOllama(model=self.model_name, temperature=0)
        self.json_llm = ChatOllama(model=self.model_name, temperature=0, format="json")
        self.threshold = -5.0  # Rerank score threshold
        self.reasoning_log = []
        
        # Load the enterprise prompt from YAML
        self.prompt_template = self._load_template("prompts/enterprise_rag_v1.yaml")

    def _load_template(self, path: str) -> str:
        """Loads prompt template from a YAML file."""
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            return config["template"]
        return "{context}\n\n{question}"

    def _log(self, message: str):
        """Helper to log both to console and the reasoning trace."""
        logger.info(message)
        self.reasoning_log.append(message)

    def route_query(self, question: str) -> str:
        """Decider: Determines if a query is NORMAL or requires HYDE."""
        prompt = ChatPromptTemplate.from_template(
            "Analyze the following user question and decide if it is a 'DIRECT' factual question "
            "or an 'ABSTRACT/CONCEPTUAL' question that would benefit from a hypothetical answer (HyDE).\n"
            "Return ONLY a JSON object with a 'route' key (value: 'DIRECT' or 'HYDE') and a 'reason' key.\n"
            "Question: {question}"
        )
        chain = prompt | self.json_llm | JsonOutputParser()
        try:
            decision = chain.invoke({"question": question})
            self._log(f"Routing Decision: {decision['route']} ({decision['reason']})")
            return decision['route']
        except Exception as e:
            logger.error(f"Router failed: {e}")
            return "DIRECT"

    def generate_hyde_doc(self, question: str) -> str:
        """Generates a hypothetical document to use as a search query."""
        self._log("HyDE: Generating hypothetical document for semantic search...")
        prompt = ChatPromptTemplate.from_template(
            "Write a detailed hypothetical technical document or paragraph that would answer this question. "
            "Do not start with 'Here is...', just write the content.\nQuestion: {question}"
        )
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke({"question": question})

    def multi_query_expand(self, question: str) -> List[str]:
        """Generates 3 variations of the query to improve retrieval recall."""
        self._log("Recall: Generating multi-query variations...")
        prompt = ChatPromptTemplate.from_template(
            "Generate 3 different variations of the following question to retrieve diverse context. "
            "Return a JSON list of strings with the key 'queries'.\nQuestion: {question}"
        )
        chain = prompt | self.json_llm | JsonOutputParser()
        try:
            variations = chain.invoke({"question": question})
            queries = variations.get("queries", [question])
            self._log(f"Variations: {queries}")
            return queries
        except:
            return [question]

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def query(self, question: str) -> Dict[str, Any]:
        """Entry point for the Optimized Agentic RAG pipeline."""
        self.reasoning_log = []
        self._log(f"User Question: {question}")

        # FAST PATH: Check for simple/short queries (e.g. greetings or 1-2 keywords)
        words = question.strip().split()
        if len(words) <= 3:
            self._log("Fast Path: Simple query detected. Skipping complex routing.")
            initial_results = self.vsm.search(question, k=10)
            reranked = self.reranker.rerank(question, initial_results, top_n=10)
            return self._generate_final_answer(question, reranked)

        # 1. Routing & Multi-Query
        route = self.route_query(question)
        search_queries = []
        
        if route == "HYDE":
            hyde_doc = self.generate_hyde_doc(question)
            search_queries = [hyde_doc]
        else:
            search_queries = self.multi_query_expand(question)

        # 2. Retrieval & Reranking
        all_candidates = []
        for q in search_queries:
            all_candidates.extend(self.vsm.search(q, k=10))
        
        # Deduplicate candidates by content
        unique_candidates = {c["content"]: c for c in all_candidates}.values()
        
        # Rerank
        self._log(f"Reranking {len(unique_candidates)} unique candidates...")
        reranked = self.reranker.rerank(question, list(unique_candidates), top_n=12)
        
        # SHORT CIRCUIT: If top score is very high, skip Critique to save time
        best_score = max([c.get("rerank_score", -10) for c in reranked]) if reranked else -10
        if best_score > 3.0:
            self._log(f"Confidence: High (Score {best_score}). Skipping critique loop.")
            return self._generate_final_answer(question, reranked[:10])

        # 3. Agentic Loop: Critique & Refinement
        final_context = self._agentic_refinement(question, reranked)

        # 4. Final Answer Generation
        return self._generate_final_answer(question, final_context)

    def _generate_final_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synthesizes the final response using the Enterprise template."""
        self._log("Synthesizing final answer with Enterprise Template...")
        
        if not context_chunks:
             return {
                "answer": "I couldn't find any relevant information to answer that question.",
                "citations": [],
                "reasoning_log": self.reasoning_log
            }

        context_text = "\n\n".join([c["content"] for c in context_chunks[:10]])
        prompt = ChatPromptTemplate.from_template(self.prompt_template)
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            answer = chain.invoke({"context": context_text, "question": question})
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            answer = "Error generating answer. Please try again."

        # Form Citations
        citations = []
        for r in context_chunks[:10]:
            citations.append({
                "source": r["metadata"].get("source", "Unknown"),
                "page": r["metadata"].get("page", "N/A"),
                "score": round(r.get("rerank_score", 0), 2)
            })

        return {
            "answer": answer,
            "citations": citations,
            "reasoning_log": self.reasoning_log
        }

    def _agentic_refinement(self, question: str, initial_context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Critiques the context and performs sub-search if needed."""
        self._log("Critique: Evaluating context sufficiency...")
        
        best_score = max([c.get("rerank_score", -10) for c in initial_context]) if initial_context else -10
        
        # If score is extremely low, we definitely need corrective search
        if best_score < -10.0:
            self._log("Warning: Initial retrieval quality is extremely low. Attempting corrective search...")

        prompt = ChatPromptTemplate.from_template(
            "Evaluate if the following context is SUFFICIENT to answer the user question. "
            "Return JSON with 'status' (SUFFICIENT or INSUFFICIENT) and 'missing_info' (string).\n"
            "Question: {question}\nContext (Sample): {context}"
        )
        # Only send top 3 for critique to save tokens/time
        context_sample = "\n\n".join([c["content"] for c in initial_context[:3]])
        chain = prompt | self.json_llm | JsonOutputParser()
        
        try:
            eval_result = chain.invoke({"question": question, "context": context_sample})
            if eval_result["status"] == "INSUFFICIENT":
                self._log(f"Corrective Loop: Missing info identified: {eval_result['missing_info']}")
                # Perform a targeted sub-search
                sub_results = self.vsm.search(eval_result["missing_info"], k=5)
                initial_context.extend(sub_results)
                # Re-rerank
                initial_context = self.reranker.rerank(question, initial_context, top_n=10)
                self._log("Successfully refined context through corrective loop.")
            else:
                self._log("Critique: Context deemed sufficient.")
        except Exception as e:
            self._log(f"Critique failed: {e}. Proceeding with initial context.")

        return initial_context
