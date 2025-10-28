from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ChatMemoryBase(BaseModel):
    question:str
    answer:str

class ChatMemoryCreate(ChatMemoryBase):
    user_id:UUID

class ChatMemoryResponse(ChatMemoryBase):
    id:UUID
    user_id:UUID
    created_at: datetime

    class Config:
        orm_mode = True