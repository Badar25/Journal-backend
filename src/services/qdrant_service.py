from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from fastapi import HTTPException
from ..core.config import settings
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantServiceError(Exception):
    """Base exception for QdrantService errors"""
    pass

class QdrantService:
    def __init__(self):
        try:
            self.client = QdrantClient(settings.qdrant_url)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.collection_name = "journals"
            self._ensure_collection_exists()
        except Exception as e:
            logger.error(f"Failed to initialize QdrantService: {str(e)}")
            raise QdrantServiceError(f"Failed to initialize Qdrant service: {str(e)}")

    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections().collections
            if not any(c.name == self.collection_name for c in collections):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                logger.info("Created 'journals' collection")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Database initialization failed: {str(e)}")

    def generate_embedding(self, text: str) -> list[float]:
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process text embedding")

    def upsert_journal(self, journal_id: str, user_id: str, title: str, content: str):
        try:
            if not all([journal_id, user_id, title, content]):
                raise HTTPException(status_code=400, detail="Missing required fields")

            if len(content.split()) > 999:
                raise HTTPException(status_code=400, detail="Content exceeds 999 words")

            vector = self.generate_embedding(content)
            point = PointStruct(
                id=journal_id,
                vector=vector,
                payload={"userId": user_id, "title": title, "content": content, "createdAt": str(datetime.now())}
            )
            self.client.upsert(self.collection_name, points=[point])
            return journal_id
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to upsert journal: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to save journal: {str(e)}")

    def get_journals_by_user(self, user_id: str) -> list[dict]:
        try:
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required")

            filter = Filter(must=[FieldCondition(key="userId", match=MatchValue(value=user_id))])
            results = self.client.scroll(self.collection_name, scroll_filter=filter, limit=100, with_payload=True)
            return [{"id": p.id, **p.payload} for p in results[0]]
        except Exception as e:
            logger.error(f"Failed to get journals for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve journals")

    def get_journal(self, journal_id: str) -> dict:
        try:
            if not journal_id:
                raise HTTPException(status_code=400, detail="Journal ID is required")

            result = self.client.retrieve(self.collection_name, ids=[journal_id], with_payload=True)
            if not result:
                raise HTTPException(status_code=404, detail="Journal not found")
            return {"id": result[0].id, **result[0].payload}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get journal {journal_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve journal")

    def delete_journal(self, journal_id: str):
        try:
            if not journal_id:
                raise HTTPException(status_code=400, detail="Journal ID is required")

            self.client.delete(self.collection_name, points_selector=[journal_id])
        except Exception as e:
            logger.error(f"Failed to delete journal {journal_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete journal")

    def search_journals(self, query: str, user_id: str, limit: int = 3) -> list[dict]:
        try:
            if not query or not user_id:
                raise HTTPException(status_code=400, detail="Query and user ID are required")

            query_vector = self.generate_embedding(query)
            filter = Filter(must=[FieldCondition(key="userId", match=MatchValue(value=user_id))])
            results = self.client.search(
                self.collection_name,
                query_vector=query_vector,
                query_filter=filter,
                limit=limit,
                with_payload=True
            )
            return [{"id": r.id, **r.payload} for r in results]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to search journals: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to search journals")

qdrant_service = QdrantService()