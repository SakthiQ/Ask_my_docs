import os
from typing import List, Dict, Any
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .vectorstore import VectorStoreManager

class RAGEngine:
    def __init__(self):
        self.vsm = VectorStoreManager()
        self.model_name = os.getenv("OLLAMA_MODEL", "llama3")
        
        # Initialize the local LLM via Ollama
        self.llm = ChatOllama(
            model=self.model_name,
            temperature=0,
        )
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        You are a helpful AI assistant that answers questions based on the provided context.
        
        Context:
        {context}
        
        Question: 
        {question}
        
        Answer the question accurately using ONLY the provided context. 
        If the answer is not in the context, say "I don't have enough information in the documents to answer this."
        Always provide a professional and concise response.
        """)

    def query(self, question: str) -> Dict[str, Any]:
        # 1. Retrieve relevant chunks
        results = self.vsm.search(question, k=4)
        
        if not results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents.",
                "citations": []
            }
        
        # 2. Format context for the LLM
        context_text = "\n\n".join([r["content"] for r in results])
        
        # 3. Generate answer
        chain = self.prompt | self.llm | StrOutputParser()
        answer = chain.invoke({
            "context": context_text,
            "question": question
        })
        
        # 4. Extract citations
        citations = [r["metadata"] for r in results]
        
        return {
            "answer": answer,
            "citations": citations
        }
