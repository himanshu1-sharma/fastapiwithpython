# from datetime import datetime
# from typing import Any, List, Optional
# from uuid import UUID
# from pydantic import BaseModel


# class ChatLongMemoryBase(BaseModel):
#     user_id:UUID
#     role: str
#     content: str
#     memory_type: Optional[str] = "raw"
#     importance_score: Optional[float] = 0.5
#     metadata: Optional[Any] = {}

# class ChatLongMemoryCreate(ChatLongMemoryBase):
#     pass
    
# class ChatLongMemoryResponse(ChatLongMemoryBase):
#     id:UUID
#     created_at: datetime
#     last_used_at: datetime

#     class Config:
#         orm_mode = True

# class ChatMemoryQueryResponse(BaseModel):
#     memories: List[ChatLongMemoryResponse]



"""
Chat Long-Term Memory Schemas
Pydantic models for validation and serialization
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator


class ChatLongMemoryBase(BaseModel):
    """Base schema with common fields"""
    user_id: UUID
    role: str = Field(
        default="system",
        description="Message role: system, human, or ai"
    )
    content: str = Field(
        ..., 
        min_length=1,
        description="The memory content"
    )
    memory_type: Optional[str] = Field(
        default="summary",
        description="Type: summary, fact, reflection, or note"
    )
    importance_score: Optional[float] = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Importance score from 0.0 to 1.0"
    )
    meta_data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        alias="metadata",
        description="Additional metadata"
    )

    @validator('role')
    def validate_role(cls, v):
        """Validate role is one of allowed values"""
        allowed_roles = ['system', 'human', 'ai']
        if v not in allowed_roles:
            raise ValueError(f'Role must be one of: {", ".join(allowed_roles)}')
        return v

    @validator('memory_type')
    def validate_memory_type(cls, v):
        """Validate memory_type is one of allowed values"""
        allowed_types = ['summary', 'fact', 'reflection', 'note']
        if v not in allowed_types:
            raise ValueError(f'Memory type must be one of: {", ".join(allowed_types)}')
        return v


class ChatLongMemoryCreate(ChatLongMemoryBase):
    """Schema for creating a new memory"""
    pass


class ChatLongMemoryUpdate(BaseModel):
    """Schema for updating an existing memory"""
    content: Optional[str] = Field(None, min_length=1)
    memory_type: Optional[str] = None
    importance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    meta_data: Optional[Dict[str, Any]] = Field(
        None,
        alias="metadata",
        description="Additional metadata update"
    )

    @validator('memory_type')
    def validate_memory_type(cls, v):
        """Validate memory_type if provided"""
        if v is not None:
            allowed_types = ['summary', 'fact', 'reflection', 'note']
            if v not in allowed_types:
                raise ValueError(f'Memory type must be one of: {", ".join(allowed_types)}')
        return v


class ChatLongMemoryResponse(ChatLongMemoryBase):
    """Schema for returning memory data"""
    id: UUID
    created_at: datetime
    last_used_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                "role": "system",
                "content": "User prefers cricket and loves IPL updates",
                "memory_type": "fact",
                "importance_score": 0.8,
                "meta_data": {"source": "conversation", "tags": ["sports", "preferences"]},
                "created_at": "2025-10-30T10:30:00Z",
                "last_used_at": "2025-10-30T10:30:00Z"
            }
        }


class ChatMemoryQueryResponse(BaseModel):
    """Schema for returning multiple memories"""
    memories: List[ChatLongMemoryResponse]
    total_count: Optional[int] = Field(
        None,
        description="Total count of memories (if pagination is used)"
    )

    class Config:
        schema_extra = {
            "example": {
                "memories": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "987fcdeb-51a2-43d7-9012-345678901234",
                        "role": "system",
                        "content": "User prefers cricket",
                        "memory_type": "fact",
                        "importance_score": 0.8,
                        "meta_data": {},
                        "created_at": "2025-10-30T10:30:00Z",
                        "last_used_at": "2025-10-30T10:30:00Z"
                    }
                ],
                "total_count": 1
            }
        }


class MemoryStatsResponse(BaseModel):
    """Schema for memory statistics"""
    total_memories: int
    memory_types: Dict[str, int]
    average_importance: float
    most_recent_memory: Optional[datetime]

    class Config:
        schema_extra = {
            "example": {
                "total_memories": 45,
                "memory_types": {
                    "summary": 20,
                    "fact": 15,
                    "reflection": 8,
                    "note": 2
                },
                "average_importance": 0.65,
                "most_recent_memory": "2025-10-30T10:30:00Z"
            }
        }


class MemoryCleanupResponse(BaseModel):
    """Schema for cleanup operation response"""
    message: str
    deleted_count: int

    class Config:
        schema_extra = {
            "example": {
                "message": "Successfully deleted 12 old memories",
                "deleted_count": 12
            }
        }