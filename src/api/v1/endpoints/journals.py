from fastapi import APIRouter, Depends, HTTPException
from ....services.qdrant_service import qdrant_service
from ....services.gemini_service import gemini_service
from ....core.firebase import get_current_user
from ....models.journal import JournalCreate, JournalUpdate, JournalResponse
from uuid import uuid4
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/", response_model=dict)
async def create_journal(journal: JournalCreate, user_id: str = Depends(get_current_user)):
    journal_id = str(uuid4())
    qdrant_service.upsert_journal(journal_id, user_id, journal.title, journal.content)
    return {"id": journal_id, "message": "Journal created"}

@router.get("/", response_model=dict)
async def get_journals(user_id: str = Depends(get_current_user)):
    journals = qdrant_service.get_journals_by_user(user_id)
    return {"journals": journals}

@router.get("/{journal_id}", response_model=JournalResponse)
async def get_journal(journal_id: str):
    journal = qdrant_service.get_journal(journal_id)
    if not journal:
        raise HTTPException(status_code=404, detail="Journal not found")
    return journal

@router.put("/{journal_id}", response_model=dict)
async def update_journal(journal_id: str, update: JournalUpdate, user_id: str = Depends(get_current_user)):
    current = qdrant_service.get_journal(journal_id)
    if not current or current["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized or journal not found")
    qdrant_service.upsert_journal(
        journal_id,
        user_id,
        update.title if update.title is not None else current["title"],
        update.content if update.content is not None else current["content"]
    )
    return {"id": journal_id, "message": "Journal updated"}

@router.delete("/{journal_id}", response_model=dict)
async def delete_journal(journal_id: str, user_id: str = Depends(get_current_user)):
    current = qdrant_service.get_journal(journal_id)
    if not current or current["userId"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized or journal not found")
    qdrant_service.delete_journal(journal_id)
    return {"message": "Journal deleted"}

@router.post("/chat", response_model=dict)
async def chat_with_journals(chat: ChatRequest, user_id: str = Depends(get_current_user)):
    relevant_journals = qdrant_service.search_journals(chat.message, user_id)
    context = "\n".join([j["content"] for j in relevant_journals])
    response = gemini_service.generate_response(chat.message, context)
    return {"reply": response}