from fastapi import APIRouter, Depends, HTTPException
from ....services.qdrant_service import qdrant_service
from ....services.gemini_service import gemini_service
from ....core.firebase import get_current_user
from ....models.response import APIResponse
from ....models.journal import JournalCreate, JournalUpdate, JournalResponse
from ....core.logger import logger
from uuid import uuid4
from pydantic import BaseModel
 
router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/", response_model=APIResponse)
async def create_journal(journal: JournalCreate, user_id: str = Depends(get_current_user)):
    logger.info(f"Creating new journal for user: {user_id}")
    if (not journal.title or not journal.title.strip()) and (not journal.content or not journal.content.strip()):
        logger.warning(f"Journal creation failed: Both title and content are empty for user {user_id}")
        return APIResponse.error_response(error="At least one field (title or content) must be provided", message="Validation Error")
    
    journal_id = str(uuid4())
    qdrant_service.upsert_journal(journal_id, user_id, journal.title, journal.content)
    logger.info(f"Journal created successfully with ID: {journal_id}")
    return APIResponse.success_response(
        data={"id": journal_id},
        message="Journal created successfully"
    )

@router.get("/", response_model=APIResponse)
async def get_journals(user_id: str = Depends(get_current_user), days: int = None):
    logger.info(f"Fetching journals for user: {user_id}")
    journals = qdrant_service.get_journals_by_user(user_id, days=days)
    return APIResponse.success_response(data={"journals": journals})

@router.get("/summary", response_model=APIResponse)
async def get_summary(user_id: str = Depends(get_current_user), days: int = 7):
    logger.info(f"Generating summary for user: {user_id} over last {days} days")
    journals = qdrant_service.get_journals_by_user(user_id, days=days)
    if not journals:
        return APIResponse.success_response(
            data={"summary": None},
            message=f"No journals found in the last {days} days"
        )
    
    context = "\n".join([f"{j['title']}: {j['content']}" for j in journals])
    summary_prompt = (
        f"Summarize my journal entries from the last {days} days based only on the provided context. "
        "Do not provide guidance, disclaimers, or mention missing information. "
        "Focus strictly on key themes, emotions, and recurring topics in a 4-5 line narrative summary. "
        "Address me directly as 'you' since these are my journals, avoiding third-person references. "
        f"Context: '{context}'"
    )
    summary = gemini_service.generate_response(summary_prompt, context)
    logger.info(f"Summary generated successfully for user: {user_id}")
    return APIResponse.success_response(
        data={"summary": summary},
        message="Summary generated successfully"
    )

# Also fix the remaining endpoints to use APIResponse
@router.put("/{journal_id}", response_model=APIResponse)
async def update_journal(journal_id: str, update: JournalUpdate, user_id: str = Depends(get_current_user)):
    logger.info(f"Updating journal {journal_id} for user: {user_id}")
    current = qdrant_service.get_journal(journal_id)
    if not current:
        return APIResponse.error_response(
            error="Journal not found",
            message=f"No journal found with ID: {journal_id}"
        )
    if current["userId"] != user_id:
        return APIResponse.error_response(
            error="Unauthorized",
            message="Not authorized to update this journal"
        )
    qdrant_service.upsert_journal(
        journal_id,
        user_id,
        update.title if update.title is not None else current["title"],
        update.content if update.content is not None else current["content"]
    )
    logger.info(f"Journal {journal_id} updated successfully")
    return APIResponse.success_response(
        data={"id": journal_id},
        message="Journal updated successfully"
    )

@router.delete("/{journal_id}", response_model=APIResponse)
async def delete_journal(journal_id: str, user_id: str = Depends(get_current_user)):
    logger.info(f"Deleting journal {journal_id} for user: {user_id}")
    current = qdrant_service.get_journal(journal_id)
    if not current:
        return APIResponse.error_response(
            error="Journal not found",
            message=f"No journal found with ID: {journal_id}"
        )
    if current["userId"] != user_id:
        return APIResponse.error_response(
            error="Unauthorized",
            message="Not authorized to delete this journal"
        )
    qdrant_service.delete_journal(journal_id)
    logger.info(f"Journal {journal_id} deleted successfully")
    return APIResponse.success_response(
        message="Journal deleted successfully"
    )

@router.post("/chat", response_model=APIResponse)
async def chat_with_journals(chat: ChatRequest, user_id: str = Depends(get_current_user)):
    logger.info(f"Processing chat request for user: {user_id}")
    relevant_journals = qdrant_service.search_journals(chat.message, user_id)
    context = "\n".join([j["content"] for j in relevant_journals])
    response = gemini_service.generate_response(chat.message, context)
    logger.info(f"Chat response generated successfully for user: {user_id}")
    return APIResponse.success_response(
        data={"response": response},
        message="Chat response generated successfully"
    )