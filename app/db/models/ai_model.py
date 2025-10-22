

import uuid
from sqlalchemy import Column, String, Text, Integer, DateTime, func # type: ignore
from sqlalchemy.dialects.postgresql import UUID # type: ignore
from app.db.base_class import Base


class AIResponse(Base):
    __tablename__ = "ai_response"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    model = Column(String(100), nullable=False)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
