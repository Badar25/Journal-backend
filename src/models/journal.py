from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class JournalCreate(BaseModel):
    title: str
    content: str = ""

class JournalUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class JournalResponse(BaseModel):
    id: str
    title: str
    content: str
    userId: str
    createdAt: str

    class Config:
        from_attributes = True