from pydantic import BaseModel, EmailStr # type: ignore
import uuid

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: uuid.UUID

    class Config:
        orm_mode = True
