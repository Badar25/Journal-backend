from fastapi import APIRouter, Depends, HTTPException
from ....services.qdrant_service import qdrant_service
from ....services.gemini_service import gemini_service
from ....core.firebase import get_current_user, firebase_admin
from ....models.response import APIResponse
from ....models.journal import JournalCreate, JournalUpdate, JournalResponse
from ....core.logger import logger
from uuid import uuid4
from pydantic import BaseModel
from ....utils.journal_extractor import JournalTextExtractor
from ....utils.journal_validator import JournalValidator
from ....core.prompt_templates import prompt_templates

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("", response_model=APIResponse) 
async def create_journal(journal: JournalCreate, user_id: str = Depends(get_current_user)):
    logger.info(f"Creating new journal for user: {user_id}")
    
    # Validate journal
    validation_error = JournalValidator.validate_create(journal, user_id)
    if validation_error:
        return validation_error
    
    journal_id = str(uuid4())
    response = qdrant_service.upsert_journal(journal_id, user_id, journal.title, journal.content)
    
    if not response.success:
        return response
        
    logger.info(f"Journal created successfully with ID: {journal_id}")
    return APIResponse.success_response(
        data={"id": journal_id},
        message="Journal created successfully"
    )

@router.put("/{journal_id}", response_model=APIResponse)
async def update_journal(journal_id: str, update: JournalUpdate, user_id: str = Depends(get_current_user)):
    logger.info(f"Updating journal {journal_id} for user: {user_id}")
    
    # Validate update
    validation_error = JournalValidator.validate_update(update)
    if validation_error:
        return validation_error
    
    current = qdrant_service.get_journal(journal_id)
    if not current.success:
        return current
        
    if current.data["userId"] != user_id:
        return APIResponse.error_response(
            error="UNAUTHORIZED",
            message="Not authorized to update this journal"
        )
        
    response = qdrant_service.upsert_journal(
        journal_id,
        user_id,
        update.title if update.title is not None else current.data["title"],
        update.content if update.content is not None else current.data["content"]
    )
    
    if not response.success:
        return response
        
    logger.info(f"Journal {journal_id} updated successfully")
    return APIResponse.success_response(
        data={"id": journal_id},
        message="Journal updated successfully"
    )

@router.get("/", response_model=APIResponse)
async def get_journals(user_id: str = Depends(get_current_user), days: int = None):
    logger.info(f"Fetching journals for user: {user_id}")
    response = qdrant_service.get_journals_by_user(user_id, days=days)
    
    if not response.success:
        return APIResponse.error_response(
            error=response.error,
            message=response.message
        )
     
    journals = response.data.get("journals", [])
    return APIResponse.success_response(
        data=journals,
        message="Journals retrieved successfully"
    )

@router.get("/summary", response_model=APIResponse)
async def get_summary(user_id: str = Depends(get_current_user), days: int = 7):
    logger.info(f"Generating summary for user: {user_id} over last {days} days")
    response = qdrant_service.get_journals_by_user(user_id, days=days)
    
    context, error_response = JournalTextExtractor.process_journals_response(response, "journal entries")
    if error_response:
        return error_response
    
    summary_prompt = prompt_templates.get_summary_prompt(days, context)
    response = gemini_service.generate_response(summary_prompt, context)
    if not response.success:
        return response
        
    logger.info(f"Summary generated successfully for user: {user_id}")
    return APIResponse.success_response(
        data={"response": response.data.get("response", "")},
        message="Summary generated successfully"
    )

@router.post("/chat", response_model=APIResponse)
async def chat_with_journals(chat: ChatRequest, user_id: str = Depends(get_current_user)):
    logger.info(f"Processing chat request for user: {user_id}")
    search_response = qdrant_service.search_journals(chat.message, user_id)
    
    context, error_response = JournalTextExtractor.process_journals_response(search_response, "relevant journals")
    if error_response:
        return error_response
    
    response = gemini_service.generate_response(chat.message, context)
    if not response.success:
        return response
        
    logger.info(f"Chat response generated successfully for user: {user_id}")
    return APIResponse.success_response(
        data={"response": response.data.get("response", "")},
        message="Chat response generated successfully"
    )

@router.delete("/{journal_id}", response_model=APIResponse)
async def delete_journal(journal_id: str, user_id: str = Depends(get_current_user)):
    logger.info(f"Deleting journal {journal_id} for user: {user_id}")
    current = qdrant_service.get_journal(journal_id)
    
    if isinstance(current, APIResponse):
        if not current.success:
            return current
        current = current.data
    
    if not current:
        return APIResponse.error_response(
            error="Journal not found",
            message=f"No journal found with ID: {journal_id}"
        )
    
    if current.get("userId") != user_id:
        return APIResponse.error_response(
            error="Unauthorized",
            message="You don't have permission to delete this journal"
        )
    
    result = qdrant_service.delete_journal(journal_id)
    if result.success:
        return APIResponse.success_response(
            data={"id": journal_id},
            message="Journal deleted successfully"
        )
    return result

@router.delete("/user/all", response_model=APIResponse)
async def delete_user_data(user_id: str = Depends(get_current_user)):
    """Delete all user data including journals and authentication"""
    logger.info(f"Deleting all data for user: {user_id}")
    
    try:
        # Delete all journals from Qdrant
        journals_deletion = qdrant_service.delete_journals_by_user(user_id)
        if not journals_deletion.success:
            return journals_deletion

        # Delete user from Firebase Authentication
        try:
            firebase_admin.auth.delete_user(user_id)
        except Exception as e:
            logger.error(f"Failed to delete Firebase user: {str(e)}")
            return APIResponse.error_response(
                error="AUTH_DELETE_ERROR",
                message="Failed to delete user authentication data"
            )

        return APIResponse.success_response(
            message="User data deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to delete user data: {str(e)}")
        return APIResponse.error_response(
            error="DELETE_ERROR",
            message="Failed to delete user data"
        )