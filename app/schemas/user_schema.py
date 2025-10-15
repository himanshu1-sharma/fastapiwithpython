from pydantic import BaseModel, EmailStr # type: ignore
import uuid
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
