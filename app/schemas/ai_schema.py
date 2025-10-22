# app/schemas/ai_schema.py
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime


class AIBase(BaseModel):
    prompt: str
    response: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class AIResponseCreate(AIBase):
    pass


class AIResponseOut(AIBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
