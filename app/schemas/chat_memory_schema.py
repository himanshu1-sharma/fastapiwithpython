from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class ChatMemoryBase(BaseModel):
    user_id:UUID
    question:str
    answer:str

class ChatMemoryCreate(ChatMemoryBase):
    pass
    
class ChatMemoryResponse(ChatMemoryBase):
    id:UUID
    created_at: datetime

    class Config:
        orm_mode = True