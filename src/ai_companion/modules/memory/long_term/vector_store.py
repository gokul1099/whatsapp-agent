import os
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import List, Optional
from openai import OpenAI
from ai_companion.settings import settings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Memory:
    """Represents a memory entry in the vector store"""
    text: str
    metadata: dict
    score: Optional[float] = None

    @property
    def id(self):
        return self.metadata.get("id")

    @property
    def timestamp(self) -> Optional[datetime]:
        ts = self.metadata.get("timestamp")
        return datetime.fromisoformat(ts) if ts else None


class VectorStore:
    REQUIRED_ENV_VARS= ["QDRANT_URL", "QDRANT_API_KEY"]
    EMBEDDING_MODEL = settings.MEMORY_EMBEDDING_MODEL
    COLLECTION_NAME= "long_term_memory"
    SIMILARITY_THRESHOLD= 0.9

    _instance: Optional["VectorStore"] = None
    _initialized: bool = False

    def __new__(cls) -> None:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self.model = OpenAI()
            self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, port=settings.QDRANT_PORT)
            self._initialized = True
    
    def _is_collection_exists(self) -> bool:
        """Chek if the collection is already present in the vector database"""
        return self.client.collection_exists(collection_name=self.COLLECTION_NAME)

    def _create_collection(self) -> None:
        """Create a new collection for storing memories"""
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )
    
    def find_simialar_memory(self, text:str) -> Optional[Memory]:
        """Find if a similar memory already exists
        
        Args:
            text: The text to search for
        
        Returns:
            Optional Memory if a similar one if found
        """
        results = self.search_memories(query=text, k =1)
        if results and results[0].score >= self.SIMILARITY_THRESHOLD:
            return results[0]
        return None

    def store_memory(self, text: str, metadata: dict) -> None:
        """Store a new memory in the vector store or update if similar exists

        Args:
            text: The text contentn of the memory
            metadata: Additional information about the memory(timestamp, type, etc)
        """

        if not self._is_collection_exists():
            self._create_collection()
        
        similar_memory= self.find_simialar_memory(text)
        if similar_memory and similar_memory.id:
            metadata["id"] = similar_memory.id
        
        embedding = self.model.embeddings.create(model=settings.MEMORY_EMBEDDING_MODEL,input=text).data[0].embedding
        point = PointStruct(
            id=metadata.get("id", hash(text)),
            vector=embedding,
            payload = {
                "text" : text,
                **metadata
            },
        )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point]
        )

    def search_memories(self, query: str, k: int = 5) -> List[Memory]:
        """Search for similar moments in the vector store

        Args:
            query: Text to search for
            k:Number of results to return
        
        Returns:
            List of Memory Object
        """
        if not self._is_collection_exists():
            return []

        query_embedding = self.model.embeddings.create(model=settings.MEMORY_EMBEDDING_MODEL,input=query).data[0].embedding
        response =  self.client.query_points(
            collection_name= self.COLLECTION_NAME,
            query= query_embedding,
            limit=k
        )
        
        return [
            Memory(
                text=point.payload["text"],
                metadata=point.payload,
                score=point.score,
            )
            for point in response.points
        ]
        

@lru_cache
def get_vector_store() -> VectorStore:
    """Get or create a VectorStore singleton instance """
    return VectorStore()

    
    
