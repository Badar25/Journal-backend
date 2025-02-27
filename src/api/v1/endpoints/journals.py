from fastapi import APIRouter, Depends, HTTPException
from ....services.qdrant_service import qdrant_service
from ....services.gemini_service import gemini_service
from ....core.firebase import get_current_user
from ....models.journal import JournalCreate, JournalUpdate, JournalResponse
from ....core.logger import logger
from uuid import uuid4
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/", response_model=dict)
async def create_journal(journal: JournalCreate, user_id: str = Depends(get_current_user)):
    logger.info(f"Creating new journal for user: {user_id}")
    journal_id = str(uuid4())
    qdrant_service.upsert_journal(journal_id, user_id, journal.title, journal.content)
    logger.info(f"Journal created successfully with ID: {journal_id}")
    return {"id": journal_id, "message": "Journal created"}

@router.get("/", response_model=dict)
async def get_journals(user_id: str = Depends(get_current_user)):
    logger.info(f"Fetching journals for user: {user_id}")
    journals = qdrant_service.get_journals_by_user(user_id)
    return {"journals": journals}

@router.get("/{journal_id}", response_model=JournalResponse)
async def get_journal(journal_id: str):
    logger.info(f"Fetching journal with ID: {journal_id}")
    journal = qdrant_service.get_journal(journal_id)
    if not journal:
        logger.warning(f"Journal not found: {journal_id}")
        raise HTTPException(status_code=404, detail="Journal not found")
    return journal

@router.put("/{journal_id}", response_model=dict)
async def update_journal(journal_id: str, update: JournalUpdate, user_id: str = Depends(get_current_user)):
    logger.info(f"Updating journal {journal_id} for user: {user_id}")
    current = qdrant_service.get_journal(journal_id)
    if not current or current["userId"] != user_id:
        logger.warning(f"Unauthorized journal update attempt: {journal_id} by user: {user_id}")
        raise HTTPException(status_code=403, detail="Not authorized or journal not found")
    qdrant_service.upsert_journal(
        journal_id,
        user_id,
        update.title if update.title is not None else current["title"],
        update.content if update.content is not None else current["content"]
    )
    logger.info(f"Journal {journal_id} updated successfully")
    return {"id": journal_id, "message": "Journal updated"}

@router.delete("/{journal_id}", response_model=dict)
async def delete_journal(journal_id: str, user_id: str = Depends(get_current_user)):
    logger.info(f"Deleting journal {journal_id} for user: {user_id}")
    current = qdrant_service.get_journal(journal_id)
    if not current or current["userId"] != user_id:
        logger.warning(f"Unauthorized journal deletion attempt: {journal_id} by user: {user_id}")
        raise HTTPException(status_code=403, detail="Not authorized or journal not found")
    qdrant_service.delete_journal(journal_id)
    logger.info(f"Journal {journal_id} deleted successfully")
    return {"message": "Journal deleted"}

@router.post("/chat", response_model=dict)
async def chat_with_journals(chat: ChatRequest, user_id: str = Depends(get_current_user)):
    logger.info(f"Processing chat request for user: {user_id}")
    relevant_journals = qdrant_service.search_journals(chat.message, user_id)
    context = "\n".join([j["content"] for j in relevant_journals])
    response = gemini_service.generate_response(chat.message, context)
    logger.info(f"Chat response generated successfully for user: {user_id}")
    return {
        "message": response
    }