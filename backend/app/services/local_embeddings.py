"""
Custom Embeddings class for local embedding service
Compatible with LangChain's Embeddings interface
"""
from typing import List
import requests
from langchain_core.embeddings import Embeddings
import logging

logger = logging.getLogger(__name__)

class LocalEmbeddings(Embeddings):
    """Custom embeddings using local embedding service"""
    
    def __init__(self, service_url: str = "http://localhost:8001"):
        self.service_url = service_url
        self._verify_service()
    
    def _verify_service(self):
        """Verify embedding service is running"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            response.raise_for_status()
            logger.info(f"Connected to embedding service: {response.json()}")
        except Exception as e:
            logger.error(f"Cannot connect to embedding service at {self.service_url}: {e}")
            raise ConnectionError(f"Embedding service unavailable: {e}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        try:
            response = requests.post(
                f"{self.service_url}/embeddings",
                json={"texts": texts},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["embeddings"]
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embeddings = self.embed_documents([text])
        return embeddings[0]
