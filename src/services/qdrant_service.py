from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, Range
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from ..core.config import settings
from ..models.response import APIResponse
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        try:
            self.client = QdrantClient(settings.qdrant_url)
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.collection_name = "journals"
            self._ensure_collection_exists()
        except Exception as e:
            logger.error(f"Failed to initialize QdrantService: {str(e)}")
            return APIResponse.error_response(
                error="INITIALIZATION_ERROR",
                message=f"Failed to initialize Qdrant service: {str(e)}"
            )

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
            return APIResponse.error_response(
                error="DATABASE_INIT_ERROR",
                message=f"Database initialization failed: {str(e)}"
            )

    def generate_embedding(self, text: str) -> list[float]:
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return APIResponse.error_response(
                error="EMBEDDING_ERROR",
                message="Failed to process text embedding"
            )

    def upsert_journal(self, journal_id: str, user_id: str, title: str, content: str):
        try:
            if not all([journal_id, user_id, title, content]):
                return APIResponse.error_response(
                    error="MISSING_FIELDS",
                    message="Missing required fields"
                )

            if len(content.split()) > 999:
                return APIResponse.error_response(
                    error="CONTENT_TOO_LONG",
                    message="Content exceeds 999 words"
                )

            vector = self.generate_embedding(content)
            created_at = datetime.now().timestamp()
            point = PointStruct(
                id=journal_id,
                vector=vector,
                payload={
                    "userId": user_id,
                    "title": title,
                    "content": content,
                    "createdAt": created_at
                }
            )
            self.client.upsert(self.collection_name, points=[point])
            return APIResponse.success_response(
                data={"id": journal_id},
                message="Journal created successfully"
            )
        except Exception as e:
            logger.error(f"Failed to upsert journal: {str(e)}")
            return APIResponse.error_response(
                error="SAVE_ERROR",
                message=f"Failed to save journal: {str(e)}"
            )

    def get_journals_by_user(self, user_id: str, days: int = None):
        try:
            if not user_id:
                return APIResponse.error_response(
                    error="MISSING_USER_ID",
                    message="User ID is required"
                )

            filters = [FieldCondition(key="userId", match=MatchValue(value=user_id))]
            if days is not None:
                start_timestamp = (datetime.now() - timedelta(days=days)).timestamp()
                end_timestamp = datetime.now().timestamp()
                filters.append(
                    FieldCondition(
                        key="createdAt",
                        range=Range(gte=start_timestamp, lte=end_timestamp)
                    )
                )

            filter = Filter(must=filters)
            results = self.client.scroll(self.collection_name, scroll_filter=filter, limit=100, with_payload=True)
            journals = [{"id": p.id, **p.payload} for p in results[0]]
            return APIResponse.success_response(
                data={"journals": journals},
                message="Journals retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Failed to get journals for user {user_id}: {str(e)}")
            return APIResponse.error_response(
                error="RETRIEVAL_ERROR",
                message=f"Failed to retrieve journals: {str(e)}"
            )

    def get_journal(self, journal_id: str):
        try:
            if not journal_id:
                return APIResponse.error_response(
                    error="MISSING_JOURNAL_ID",
                    message="Journal ID is required"
                )

            result = self.client.retrieve(self.collection_name, ids=[journal_id], with_payload=True)
            if not result:
                return APIResponse.error_response(
                    error="JOURNAL_NOT_FOUND",
                    message="Journal not found"
                )
            return APIResponse.success_response(
                data={"id": result[0].id, **result[0].payload},
                message="Journal retrieved successfully"
            )
        except Exception as e:
            logger.error(f"Failed to get journal {journal_id}: {str(e)}")
            return APIResponse.error_response(
                error="RETRIEVAL_ERROR",
                message="Failed to retrieve journal"
            )

    def delete_journal(self, journal_id: str):
        try:
            if not journal_id:
                return APIResponse.error_response(
                    error="MISSING_JOURNAL_ID",
                    message="Journal ID is required"
                )

            self.client.delete(self.collection_name, points_selector=[journal_id])
            return APIResponse.success_response(
                message="Journal deleted successfully"
            )
        except Exception as e:
            logger.error(f"Failed to delete journal {journal_id}: {str(e)}")
            return APIResponse.error_response(
                error="DELETE_ERROR",
                message="Failed to delete journal"
            )

    def search_journals(self, query: str, user_id: str, limit: int = 3):
        try:
            if not query or not user_id:
                return APIResponse.error_response(
                    error="MISSING_PARAMETERS",
                    message="Query and user ID are required"
                )

            query_vector = self.generate_embedding(query)
            # Check if embedding generation failed (if so, return the http resp)
            if isinstance(query_vector, APIResponse):  
                return query_vector

            filter = Filter(must=[FieldCondition(key="userId", match=MatchValue(value=user_id))])
            results = self.client.search(
                self.collection_name,
                query_vector=query_vector,
                query_filter=filter,
                limit=limit,
                with_payload=True
            )
            journals = []
            for result in results:
                journal_data = {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "title": result.payload.get("title", ""),
                    "userId": result.payload.get("userId", ""),
                    "createdAt": result.payload.get("createdAt", "")
                }
                journals.append(journal_data)

            return APIResponse.success_response(
                data={"journals": journals},
                message="Search completed successfully"
            )
        except Exception as e:
            logger.error(f"Failed to search journals: {str(e)}")
            return APIResponse.error_response(
                error="SEARCH_ERROR",
                message="Failed to search journals"
            )

qdrant_service = QdrantService()