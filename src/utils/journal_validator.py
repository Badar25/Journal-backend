from typing import Optional
from ..models.response import APIResponse
from ..models.journal import JournalCreate, JournalUpdate
from ..core.logger import logger

class JournalValidator:
    MAX_TITLE_LENGTH = 200
    MAX_CONTENT_LENGTH = 1000 
    
    @staticmethod
    def validate_create(journal: JournalCreate, user_id: str) -> Optional[APIResponse]:
        """Validate journal creation request."""
        # Check for empty fields
        if (not journal.title or not journal.title.strip()) and (not journal.content or not journal.content.strip()):
            logger.warning(f"Journal creation failed: Both title and content are empty for user {user_id}")
            return APIResponse.error_response(
                error="EMPTY_FIELDS",
                message="At least one field (title or content) must be provided"
            )
        
        # Title length validation
        if journal.title and len(journal.title) > JournalValidator.MAX_TITLE_LENGTH:
            return APIResponse.error_response(
                error="TITLE_TOO_LONG",
                message=f"Title must not exceed {JournalValidator.MAX_TITLE_LENGTH} characters"
            )
        
        # Content length validation
        if journal.content and len(journal.content) > JournalValidator.MAX_CONTENT_LENGTH:
            return APIResponse.error_response(
                error="CONTENT_TOO_LONG",
                message=f"Content must not exceed {JournalValidator.MAX_CONTENT_LENGTH} characters"
            )
        
        return None

    @staticmethod
    def validate_update(update: JournalUpdate) -> Optional[APIResponse]:
        """Validate journal update request."""
        if update.title is not None and len(update.title) > JournalValidator.MAX_TITLE_LENGTH:
            return APIResponse.error_response(
                error="TITLE_TOO_LONG",
                message=f"Title must not exceed {JournalValidator.MAX_TITLE_LENGTH} characters"
            )
        
        if update.content is not None and len(update.content) > JournalValidator.MAX_CONTENT_LENGTH:
            return APIResponse.error_response(
                error="CONTENT_TOO_LONG",
                message=f"Content must not exceed {JournalValidator.MAX_CONTENT_LENGTH} characters"
            )
        
        return None
