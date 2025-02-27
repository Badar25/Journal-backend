import google.generativeai as genai
from fastapi import HTTPException
from ..core.config import settings
from ..models.response import APIResponse

class GeminiServiceError(Exception):
    """Base exception for GeminiService errors"""
    pass

class GeminiService:
    def __init__(self):
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            raise GeminiServiceError(f"Failed to initialize Gemini service: {str(e)}")

    def generate_response(self, query: str, context: str) -> APIResponse:
        if not query:
            return APIResponse.error_response(
                error="INVALID_QUERY",
                message="Query cannot be empty"
            )
        if not context:
            return APIResponse.error_response(
                error="INVALID_CONTEXT",
                message="Context cannot be empty"
            )

        try:
            prompt = f"Based on this context from my journals: '{context}', answer this: '{query}'"
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                return APIResponse.error_response(
                    error="EMPTY_RESPONSE",
                    message="Gemini API returned empty response"
                )
            
            return APIResponse.success_response(
                data={"response": response.text},
                message="Response generated successfully"
            )
            
        except Exception as e:
            return APIResponse.error_response(
                error="GEMINI_ERROR",
                message=f"Something went wrong: {str(e)}"
            )

gemini_service = GeminiService()