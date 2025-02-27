import unittest
from unittest.mock import patch, Mock
from src.models.response import APIResponse
from src.api.v1.endpoints.journals import get_summary

class TestGetSummary(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user_id = "test_user_123"
        self.days = 7
        self.test_context = "Test journal entry content"
        self.test_summary = "Test summary response"

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    @patch('src.api.v1.endpoints.journals.prompt_templates')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_successful_summary_generation(self, mock_gemini, mock_templates, 
                                              mock_extractor, mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_extractor.process_journals_response.return_value = (self.test_context, None)
        mock_templates.get_summary_prompt.return_value = "Generate summary"
        mock_gemini.generate_response.return_value = APIResponse.success_response(
            data={"response": self.test_summary}
        )

        # Execute
        response = await get_summary(self.user_id, self.days)

        # Verify
        self.assertTrue(response.success)
        self.assertEqual(response.data["response"], self.test_summary)
        self.assertEqual(response.message, "Summary generated successfully")
        
        # Verify mock calls
        mock_qdrant.get_journals_by_user.assert_called_once_with(self.user_id, days=self.days)
        mock_extractor.process_journals_response.assert_called_once()
        mock_templates.get_summary_prompt.assert_called_once_with(self.days, self.test_context)
        mock_gemini.generate_response.assert_called_once()
        mock_logger.info.assert_called()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    async def test_journal_extraction_error(self, mock_extractor, mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": []}
        )
        error_response = APIResponse.error_response(
            error="NO_JOURNALS",
            message="No journals found"
        )
        mock_extractor.process_journals_response.return_value = (None, error_response)

        # Execute
        response = await get_summary(self.user_id, self.days)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "NO_JOURNALS")
        self.assertEqual(response.message, "No journals found")
        
        # Verify mock calls
        mock_qdrant.get_journals_by_user.assert_called_once()
        mock_extractor.process_journals_response.assert_called_once()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    @patch('src.api.v1.endpoints.journals.JournalTextExtractor')
    @patch('src.api.v1.endpoints.journals.prompt_templates')
    @patch('src.api.v1.endpoints.journals.gemini_service')
    async def test_gemini_service_error(self, mock_gemini, mock_templates, 
                                      mock_extractor, mock_qdrant, mock_logger):
        # Setup mocks
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": [{"content": "Test content"}]}
        )
        mock_extractor.process_journals_response.return_value = (self.test_context, None)
        mock_templates.get_summary_prompt.return_value = "Generate summary"
        mock_gemini.generate_response.return_value = APIResponse.error_response(
            error="GENERATION_ERROR",
            message="Failed to generate summary"
        )

        # Execute
        response = await get_summary(self.user_id, self.days)

        # Verify
        self.assertFalse(response.success)
        self.assertEqual(response.error, "GENERATION_ERROR")
        self.assertEqual(response.message, "Failed to generate summary")
        
        # Verify mock calls
        mock_qdrant.get_journals_by_user.assert_called_once()
        mock_extractor.process_journals_response.assert_called_once()
        mock_gemini.generate_response.assert_called_once()

    @patch('src.api.v1.endpoints.journals.logger')
    @patch('src.api.v1.endpoints.journals.qdrant_service')
    async def test_custom_days_parameter(self, mock_qdrant, mock_logger):
        # Setup mock
        mock_qdrant.get_journals_by_user.return_value = APIResponse.success_response(
            data={"journals": []}
        )
        
        custom_days = 30

        # Execute
        await get_summary(self.user_id, custom_days)

        # Verify mock calls with custom days parameter
        mock_qdrant.get_journals_by_user.assert_called_once_with(self.user_id, days=custom_days)
        mock_logger.info.assert_called_with(
            f"Generating summary for user: {self.user_id} over last {custom_days} days"
        )

if __name__ == '__main__':
    unittest.main()