from sqlalchemy import Column, DateTime, Text, func, ForeignKey # type: ignore
from app.db.base_class import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ChatMemory(Base):
    __tablename__ = "chat_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
