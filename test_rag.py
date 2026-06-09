from app.rag.vectorstore import VectorStoreManager
from app.rag.responder import LLMResponder
from app.rag.reranker import DocumentReranker

def run_rag_test():
    vsm = VectorStoreManager()
    responder = LLMResponder()
    reranker = DocumentReranker()

    query =  "What is the recipe for chocolate cake?"
    
    print(f"\n[USER]: {query}")
    
    # 1. Step 1: Initial Retrieval (Get 10 potential candidates)
    print("⏳ Step 1: Retrieving candidates (Hybrid Search)...")
    initial_chunks = vsm.search(query, k=10)
    
    # 2. Step 2: Re-ranking (Pick the best 3)
    print("⏳ Step 2: Re-ranking for maximum accuracy...")
    best_chunks = reranker.rerank(query, initial_chunks, top_n=3)
    
    # Print the scores so you can see the AI thinking!
    for i, chunk in enumerate(best_chunks):
        print(f"   - Match {i+1} Score: {chunk['rerank_score']:.4f}")

    # 3. Step 3: Generation
    print("⏳ Step 3: Generating final answer...")
    answer = responder.generate_answer(query, best_chunks)

    print(f"\n[AI RESPONSE]:\n{answer}\n")

if __name__ == "__main__":
    run_rag_test()