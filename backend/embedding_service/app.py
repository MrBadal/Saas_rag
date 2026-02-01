"""
Self-Hosted Embedding Service
Uses sentence-transformers for free, local embeddings
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Local Embedding Service")

# Load model on startup (cached in memory)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
logger.info(f"Loading embedding model: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)
logger.info("Model loaded successfully")

class EmbeddingRequest(BaseModel):
    texts: List[str]

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    dimensions: int

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": MODEL_NAME}

@app.post("/embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """Generate embeddings for input texts"""
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        # Generate embeddings
        embeddings = model.encode(request.texts, convert_to_numpy=True)
        
        # Convert to list format
        embeddings_list = embeddings.tolist()
        
        return EmbeddingResponse(
            embeddings=embeddings_list,
            model=MODEL_NAME,
            dimensions=len(embeddings_list[0])
        )
    
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {
        "service": "Local Embedding Service",
        "model": MODEL_NAME,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
