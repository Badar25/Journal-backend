import unittest
from unittest.mock import patch, Mock
from uuid import UUID
from src.models.journal import JournalCreate
from src.models.response import APIResponse
from src.api.v1.endpoints.journals import create_journal

class TestCreateJournal(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.journal = JournalCreate(title="Test Journal", content="Test Content")
        self.user_id = "test_user_123"
        
    @patch('src.api.v1.endpoints.journals.JournalValidator')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.logger')
    async def test_successful_journal_creation(self, mock_logger, mock_qdrant, mock_validator):
        # Setup mocks
        mock_validator.validate_create.return_value = None
        mock_qdrant.upsert_journal.return_value = APIResponse.success_response(
            data={"id": "test_id"},
            message="Journal created successfully"
        )

        # Execute
        response = await create_journal(self.journal, self.user_id)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(response.message, "Journal created successfully")
        self.assertTrue(UUID(response.data["id"]))
        
        # Verify mock calls
        mock_validator.validate_create.assert_called_once_with(self.journal, self.user_id)
        mock_logger.info.assert_called()
        mock_qdrant.upsert_journal.assert_called_once()

    @patch('src.api.v1.endpoints.journals.JournalValidator')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.logger')
    async def test_validation_error(self, mock_logger, mock_qdrant, mock_validator):
        # Setup validation error
        validation_error = APIResponse.error_response(
            error="VALIDATION_ERROR",
            message="Validation failed"
        )
        mock_validator.validate_create.return_value = validation_error

        # Execute
        response = await create_journal(self.journal, self.user_id)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "VALIDATION_ERROR")
        self.assertEqual(response.message, "Validation failed")
        
        # Verify mocks
        mock_validator.validate_create.assert_called_once_with(self.journal, self.user_id)
        mock_qdrant.upsert_journal.assert_not_called()

    @patch('src.api.v1.endpoints.journals.JournalValidator')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.logger')
    async def test_qdrant_service_error(self, mock_logger, mock_qdrant, mock_validator):
        # Setup mocks
        mock_validator.validate_create.return_value = None
        mock_qdrant.upsert_journal.return_value = APIResponse.error_response(
            error="SAVE_ERROR",
            message="Failed to save journal"
        )

        # Execute
        response = await create_journal(self.journal, self.user_id)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "SAVE_ERROR")
        self.assertEqual(response.message, "Failed to save journal")
        
        # Verify mock calls
        mock_validator.validate_create.assert_called_once_with(self.journal, self.user_id)
        mock_qdrant.upsert_journal.assert_called_once()

    @patch('src.api.v1.endpoints.journals.JournalValidator')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.logger')
    async def test_empty_user_id(self, mock_logger, mock_qdrant, mock_validator):
        # Setup validation error for empty user ID
        validation_error = APIResponse.error_response(
            error="INVALID_USER",
            message="User ID cannot be empty"
        )
        mock_validator.validate_create.return_value = validation_error

        # Execute
        response = await create_journal(self.journal, "")

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "INVALID_USER")
        self.assertEqual(response.message, "User ID cannot be empty")
        
        # Verify mocks
        mock_validator.validate_create.assert_called_once_with(self.journal, "")
        mock_qdrant.upsert_journal.assert_not_called()

if __name__ == '__main__':
    unittest.main()