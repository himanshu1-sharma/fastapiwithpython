from openai.resources.chat.chat import Chat
from sqlalchemy.orm import Session

from app.db.models.chat_memory_model import ChatMemory
from app.db.models.user_model import User
from app.schemas.chat_memory_schema import ChatMemoryCreate


def save_chat_memory(db: Session, chat:ChatMemoryCreate):
    user = db.query(User).filter(User.id == chat.user_id).first()
    if not user:
        raise ValueError("User not found")

    chat = ChatMemory(
        user_id=chat.user_id, 
        question=chat.question, 
        answer=chat.answer
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)


def get_user_chat_memory(db:Session, user_id):
    return db.query(ChatMemory).filter(ChatMemory.user_id == user_id).order_by(ChatMemory.created_at.desc()).all()
