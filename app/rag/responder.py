import os
import yaml
from typing import List, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMResponder:
    """Handles generating answers using a local LLM based on YAML prompts and thresholds."""

    def __init__(self, model_name: str = "llama3", prompt_file: str = "prompts/rag_v1.yaml"):
        self.llm = ChatOllama(model=model_name, temperature=0)
        self.output_parser = StrOutputParser()
        self.prompt_file = prompt_file
        self.threshold = 0.0 # <--- OUR CUTOFF THRESHOLD
        self.prompt_config = self._load_prompt()

    def _load_prompt(self) -> Dict[str, Any]:
        """Loads the prompt template from a YAML file."""
        if not os.path.exists(self.prompt_file):
            raise FileNotFoundError(f"Prompt file not found at {self.prompt_file}")
        
        with open(self.prompt_file, 'r') as f:
            return yaml.safe_load(f)

    def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Constructs a prompt and gets an answer, but ONLY if the threshold is met."""
        
        # 1. THRESHOLD CHECK
        # We look at the best score from the reranker
        max_score = max([c.get("rerank_score", -10) for c in context_chunks]) if context_chunks else -10
        
        if max_score < self.threshold:
            return "I'm sorry, I cannot find any relevant information in the uploaded documents to answer that question."

        # 2. Combine context if threshold is passed
        context_text = "\n\n".join([c["content"] for c in context_chunks])
        
        # 3. Create the prompt using the YAML template
        prompt = ChatPromptTemplate.from_template(self.prompt_config["template"])
        
        # 4. Run the chain
        chain = prompt | self.llm | self.output_parser
        
        return chain.invoke({"context": context_text, "question": question})