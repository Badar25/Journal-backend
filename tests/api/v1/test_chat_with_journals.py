import unittest
from unittest.mock import patch, Mock
from src.models.response import APIResponse
from src.api.v1.endpoints.journals import chat_with_journals, ChatRequest

class TestChatWithJournals(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user_id = "test_user_123"
        self.chat_request = ChatRequest(message="Test question")
        self.test_context = "Test journal context"
        self.test_response = "Test chat response"

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_successful_chat_response(self, mock_gemini, mock_extractor, 
                                         mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.search_journals.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_extractor.process_journals_response.return_value = (self.test_context, None)
        mock_gemini.generate_response.return_value = APIResponse.success_response(
            data={"response": self.test_response}
        )

        # Execute
        response = await chat_with_journals(self.chat_request, self.user_id)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(response.data["response"], self.test_response)
        self.assertEqual(response.message, "Chat response generated successfully")
        
        # Verify mock calls
        mock_qdrant.search_journals.assert_called_once_with(self.chat_request.message, self.user_id)
        mock_extractor.process_journals_response.assert_called_once()
        mock_gemini.generate_response.assert_called_once_with(self.chat_request.message, self.test_context)
        mock_logger.info.assert_called()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    async def test_journal_search_error(self, mock_extractor, mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.search_journals.return_value = APIResponse.success_response(
            data={"journals": []}
        )
        error_response = APIResponse.error_response(
            error="NO_RELEVANT_JOURNALS",
            message="No relevant journals found"
        )
        mock_extractor.process_journals_response.return_value = (None, error_response)

        # Execute
        response = await chat_with_journals(self.chat_request, self.user_id)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "NO_RELEVANT_JOURNALS")
        self.assertEqual(response.message, "No relevant journals found")
        
        # Verify mock calls
        mock_qdrant.search_journals.assert_called_once()
        mock_extractor.process_journals_response.assert_called_once()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_gemini_service_error(self, mock_gemini, mock_extractor, 
                                      mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.search_journals.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_extractor.process_journals_response.return_value = (self.test_context, None)
        mock_gemini.generate_response.return_value = APIResponse.error_response(
            error="GENERATION_ERROR",
            message="Failed to generate response"
        )

        # Execute
        response = await chat_with_journals(self.chat_request, self.user_id)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "GENERATION_ERROR")
        self.assertEqual(response.message, "Failed to generate response")
        
        # Verify mock calls
        mock_qdrant.search_journals.assert_called_once()
        mock_extractor.process_journals_response.assert_called_once()
        mock_gemini.generate_response.assert_called_once()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    async def test_empty_message(self, mock_qdrant, mock_logger):
        # Setup
        empty_chat = ChatRequest(message="")

        # Execute
        response = await chat_with_journals(empty_chat, self.user_id)

        # Verify mock calls
        mock_qdrant.search_journals.assert_called_once_with("", self.user_id)

if __name__ == '__main__':
    unittest.main()