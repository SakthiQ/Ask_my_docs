from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router

app = FastAPI(
    title="Ask My Documents API",
    description="A privacy-first local RAG platform using Ollama and ChromaDB.",
    version="1.0.0"
)

# Enable CORS for frontend (e.g., Streamlit or React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to Ask My Documents API. Visit /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
