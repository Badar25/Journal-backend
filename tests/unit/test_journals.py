import pytest
from unittest.mock import patch, Mock
from fastapi import Depends
from src.models.journal import JournalCreate, JournalUpdate
from src.utils.journal_validator import JournalValidator
from src.models.response import APIResponse
from src.core.firebase import get_current_user

class TestJournalOperations:
    @pytest.fixture(autouse=True)
    def setup_auth(self, app):
        # Override the dependency
        async def override_get_current_user():
            return "test_user_123"
        
        app.dependency_overrides[get_current_user] = override_get_current_user
        yield
        app.dependency_overrides = {}

    @pytest.mark.asyncio
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    async def test_create_journal(self, mock_qdrant, client, mock_user_id, sample_journal):
        # Setup mock
        mock_qdrant.upsert_journal.return_value = APIResponse.success_response(
            data={"id": "test_id"}
        )

        # Test journal creation
        response = client.post("/v1/journals/", json=sample_journal)
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "id" in response.json()["data"]

    @pytest.mark.asyncio
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_get_summary(self, mock_gemini, mock_qdrant, client, mock_user_id):
        # Setup mocks
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_gemini.generate_response.return_value = APIResponse.success_response(
            data={"response": "Summary of journals"}
        )

        # Test summary generation
        response = client.get("/v1/journals/summary")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "response" in response.json()["data"]

    @pytest.mark.asyncio
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_chat_with_journals(self, mock_gemini, mock_qdrant, client, mock_user_id):
        # Setup mocks
        mock_qdrant.search_journals.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_gemini.generate_response.return_value = APIResponse.success_response(
            data={"response": "Chat response"}
        )

        # Test chat functionality
        response = client.post("/v1/journals/chat", json={"message": "Test question"})
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "response" in response.json()["data"]

    @pytest.mark.asyncio
    async def test_authentication(self, client, app):
        # Remove auth override for this test
        app.dependency_overrides = {}
        
        # Test unauthorized access
        response = client.get("/v1/journals/")
        assert response.status_code in [401, 403]  # Accept either unauthorized or forbidden
    
        response = client.post("/v1/journals/", json={"title": "Test", "content": "Test"})
        assert response.status_code in [401, 403]  # Accept either unauthorized or forbidden

    @pytest.mark.asyncio
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    async def test_journal_extraction(self, mock_qdrant, client, mock_user_id):
        # Setup mock
        journals_data = [
            {"content": "First entry"},
            {"content": "Second entry"}
        ]
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": journals_data}
        )
    
        # Test journals retrieval
        response = client.get("/v1/journals/")
        
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Check the actual journals data
        response_journals = response.json()["data"]["journals"]["data"]["journals"]
        assert len(response_journals) == 2
        assert response_journals == journals_data