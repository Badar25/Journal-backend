import pytest
from fastapi.testclient import TestClient
from src.main import app as fastapi_app  # Rename to avoid confusion

@pytest.fixture
def app():
    return fastapi_app  # Return the actual FastAPI instance

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def mock_user_id():
    return "test_user_123"

@pytest.fixture
def sample_journal():
    return {
        "title": "Test Journal",
        "content": "This is a test journal entry"
    }