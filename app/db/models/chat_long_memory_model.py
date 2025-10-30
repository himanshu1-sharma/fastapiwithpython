# from sqlalchemy import Column, String, Text, DateTime, Float, JSON, ForeignKey, func
# from app.db.base_class import Base
# from sqlalchemy.dialects.postgresql import UUID
# import uuid


# class ChatLongMemory(Base):
#     __tablename__ = "chat_long_memory"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
#     user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
#     memory_type = Column(String(50), default="summary")  # summary / fact / reflection / note
#     role = Column(String(20), nullable=False, default="system")  # system/human/ai
#     content = Column(Text, nullable=False)  # summarized memory content
#     embedding = Column(JSON, nullable=True)  # optional — can store vector here if not using vector DB
#     importance_score = Column(Float, default=0.5)
#     metadata = Column(JSON, default={})
#     created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
#     last_used_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)




"""
Chat Long-Term Memory Model
Stores summarized conversation memories, facts, and reflections
"""
from sqlalchemy import Column, String, Text, DateTime, Float, JSON, ForeignKey, func
from app.db.base_class import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid


class ChatLongMemory(Base):
    """
    Long-term memory storage for chat conversations
    
    Stores:
    - Conversation summaries
    - User facts/preferences
    - Bot reflections
    - Important notes
    """
    __tablename__ = "chat_long_memory"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True  # Index for faster queries
    )
    
    memory_type = Column(
        String(50), 
        default="summary",
        index=True  # Index for type-based filtering
    )  # Options: summary, fact, reflection, note
    
    role = Column(
        String(20), 
        nullable=False, 
        default="system"
    )  # Options: system, human, ai
    
    content = Column(
        Text, 
        nullable=False
    )  # The actual memory content
    
    embedding = Column(
        JSON, 
        nullable=True
    )  # Optional: store vector embeddings if not using separate vector DB
    
    importance_score = Column(
        Float, 
        default=0.5,
        index=True  # Index for importance-based queries
    )  # Range: 0.0 to 1.0
    
    meta_data = Column(
        'metadata',  # column name in DB
        JSON, 
        default={}
    )  # Additional metadata (tags, source, context, etc.)
    
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    
    last_used_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    def __repr__(self):
        return f"<ChatLongMemory(id={self.id}, user_id={self.user_id}, type={self.memory_type})>"