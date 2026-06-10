import sys
import os
import json
from typing import Dict, Any

# Ensure we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.rag.engine import RAGEngine

def test_rag_loop():
    print("START: Initializing RAGEngine...")
    engine = RAGEngine()
    
    # 1. Test Router
    print("\nROUTER: Testing Router...")
    q1 = "What is the capital of Japan?"
    r1 = engine.route_query(q1)
    print(f"Question: '{q1}' -> Route: {r1}")
    
    q2 = "Compare the philosophical differences between centralized and decentralized intelligence."
    r2 = engine.route_query(q2)
    print(f"Question: '{q2}' -> Route: {r2}")

    # 2. Test Multi-Query
    print("\nQUERY EXPANSION: Testing Multi-Query Expansion...")
    variations = engine.multi_query_expand("What are the system requirements for installation?")
    print(f"Variations: {variations}")

    # 3. Test Full Query (Mocked context to trigger refinement)
    # Note: This will actually try to hit Ollama and Chroma.
    print("\nPIPELINE: Testing Full Pipeline (Complex Query)...")
    try:
        response = engine.query("Explain the conceptual relationship between the Phase 1 implementation and the Phase 5 agentic loops.")
        print("\n--- RESPONSE ---")
        print(f"Answer: {response['answer'][:200]}...")
        print("\n--- REASONING LOG ---")
        for log in response['reasoning_log']:
            print(f"- {log}")
    except Exception as e:
        print(f"ERROR: Error during full query test: {e}")

if __name__ == "__main__":
    test_rag_loop()
