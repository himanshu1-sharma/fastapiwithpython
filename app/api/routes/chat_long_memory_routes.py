"""
Chat Long-Term Memory API Routes
FastAPI endpoints for memory management
"""
from app.api.dependencies.db_dependency import get_db
from app.db.models.user_model import User
from app.services.chat_long_memory_service import sharmaji_chat
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.schemas.chat_long_memory_schema import (
    ChatLongMemoryCreate,
    ChatLongMemoryUpdate,
    ChatLongMemoryResponse,
    ChatMemoryQueryResponse,
    MemoryStatsResponse,
    MemoryCleanupResponse
)

router = APIRouter(
    prefix="/api/v1/chat/long-memory",
    tags=["Chat Long Memory"]
)

@router.post("/chat-with-sharmaji")
def chat_with_sharmaji(user_id: str, message: str, db: Session = Depends(get_db)):
    """
    Talk to Sharma Ji (AI assistant with memory + realtime data)
    """
    response = sharmaji_chat(db, user_id, message)
    return {
        "success": True,
        "response": response
    }


# def get_current_user(db: Session = Depends(get_db)) -> User:
#     user = db.query(User).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="No user authenticated.")
#     return user




# # ==================== CREATE ====================

# @router.post("/", response_model=ChatLongMemoryResponse, status_code=status.HTTP_201_CREATED)
# async def create_long_memory(
#     content: str = Body(..., description="Memory content", embed=True),
#     role: str = Body(default="system", description="Role: system/human/ai", embed=True),
#     memory_type: str = Body(default="summary", description="Type: summary/fact/reflection/note", embed=True),
#     importance_score: float = Body(default=0.5, ge=0.0, le=1.0, description="Importance (0-1)", embed=True),
#     meta_data: Optional[dict] = Body(default=None, description="Additional metadata", embed=True),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Create a new long-term memory entry
    
#     - **content**: The memory content (summary, fact, reflection, etc.)
#     - **role**: Message role (system/human/ai)
#     - **memory_type**: Type of memory (summary/fact/reflection/note)
#     - **importance_score**: Importance rating from 0.0 to 1.0
#     - **metadata**: Optional additional metadata
#     """
#     try:
#         return chat_long_memory_service.create_memory(
#             db=db,
#             user_id=current_user.id,
#             content=content,
#             role=role,
#             memory_type=memory_type,
#             importance_score=importance_score,
#             meta_data=meta_data
#         )
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to create memory: {str(e)}"
#         )


# # ==================== READ ====================

# @router.get("/{memory_id}", response_model=ChatLongMemoryResponse)
# async def get_memory(
#     memory_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get a single memory by ID
    
#     - **memory_id**: UUID of the memory to retrieve
#     """
#     try:
#         from app.db.models.chat_long_memory_model import ChatLongMemory
        
#         # Verify ownership
#         memory = db.query(ChatLongMemory).filter(
#             ChatLongMemory.id == memory_id,
#             ChatLongMemory.user_id == current_user.id
#         ).first()
        
#         if not memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found or access denied"
#             )
        
#         return chat_long_memory_service.get_memory(db, memory_id)
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch memory: {str(e)}"
#         )


# @router.get("/recent/list", response_model=ChatMemoryQueryResponse)
# async def get_recent_memories(
#     limit: int = Query(default=10, ge=1, le=100, description="Number of recent memories"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get recent long-term memories for the current user
    
#     - **limit**: Number of recent memories to retrieve (1-100)
#     """
#     try:
#         return chat_long_memory_service.get_user_recent_memories(
#             db=db,
#             user_id=current_user.id,
#             limit=limit
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch recent memories: {str(e)}"
#         )


# @router.get("/all/list", response_model=ChatMemoryQueryResponse)
# async def get_all_memories(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get all long-term memories for the current user
#     """
#     try:
#         return chat_long_memory_service.get_all_user_memories(
#             db=db,
#             user_id=current_user.id
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch all memories: {str(e)}"
#         )


# @router.get("/type/{memory_type}", response_model=ChatMemoryQueryResponse)
# async def get_memories_by_type(
#     memory_type: str,
#     limit: Optional[int] = Query(default=None, ge=1, le=100, description="Optional limit"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get memories filtered by type
    
#     - **memory_type**: Type to filter (summary/fact/reflection/note)
#     - **limit**: Optional limit on results (1-100)
#     """
#     # Validate memory type
#     valid_types = ['summary', 'fact', 'reflection', 'note']
#     if memory_type not in valid_types:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Invalid memory type. Must be one of: {', '.join(valid_types)}"
#         )
    
#     try:
#         return chat_long_memory_service.get_memories_by_type(
#             db=db,
#             user_id=current_user.id,
#             memory_type=memory_type,
#             limit=limit
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch memories by type: {str(e)}"
#         )


# @router.get("/important/list", response_model=ChatMemoryQueryResponse)
# async def get_important_memories(
#     min_importance: float = Query(default=0.7, ge=0.0, le=1.0, description="Minimum importance score"),
#     limit: int = Query(default=20, ge=1, le=100, description="Maximum results"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get memories above a certain importance threshold
    
#     - **min_importance**: Minimum importance score (0.0 to 1.0)
#     - **limit**: Maximum number of results (1-100)
#     """
#     try:
#         return chat_long_memory_service.get_important_memories(
#             db=db,
#             user_id=current_user.id,
#             min_importance=min_importance,
#             limit=limit
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch important memories: {str(e)}"
#         )


# @router.get("/search/query", response_model=ChatMemoryQueryResponse)
# async def search_memories(
#     q: str = Query(..., description="Search term", min_length=1),
#     limit: int = Query(default=20, ge=1, le=100, description="Maximum results"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Search memories by content (case-insensitive)
    
#     - **q**: Search term (minimum 1 character)
#     - **limit**: Maximum number of results (1-100)
#     """
#     try:
#         return chat_long_memory_service.search_memories(
#             db=db,
#             user_id=current_user.id,
#             search_term=q,
#             limit=limit
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to search memories: {str(e)}"
#         )


# @router.get("/stats/summary", response_model=MemoryStatsResponse)
# async def get_memory_stats(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Get statistics about user's long-term memories
    
#     Returns counts by type, average importance, etc.
#     """
#     try:
#         return chat_long_memory_service.get_memory_statistics(
#             db=db,
#             user_id=current_user.id
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to fetch memory stats: {str(e)}"
#         )


# # ==================== UPDATE ====================

# @router.patch("/{memory_id}/importance", response_model=ChatLongMemoryResponse)
# async def update_memory_importance(
#     memory_id: UUID,
#     new_importance: float = Body(..., ge=0.0, le=1.0, description="New importance score", embed=True),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Update the importance score of a specific memory
    
#     - **memory_id**: UUID of the memory to update
#     - **new_importance**: New importance score (0.0 to 1.0)
#     """
#     try:
#         from app.db.models.chat_long_memory_model import ChatLongMemory
        
#         # Verify ownership
#         memory = db.query(ChatLongMemory).filter(
#             ChatLongMemory.id == memory_id,
#             ChatLongMemory.user_id == current_user.id
#         ).first()
        
#         if not memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found or access denied"
#             )
        
#         updated_memory = chat_long_memory_service.update_memory_importance(
#             db=db,
#             memory_id=memory_id,
#             new_importance=new_importance
#         )
        
#         if not updated_memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found"
#             )
        
#         return updated_memory
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to update memory importance: {str(e)}"
#         )


# @router.patch("/{memory_id}", response_model=ChatLongMemoryResponse)
# async def update_memory(
#     memory_id: UUID,
#     update_data: ChatLongMemoryUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Update memory content, type, or metadata
    
#     - **memory_id**: UUID of the memory to update
#     - **update_data**: Fields to update (all optional)
#     """
#     try:
#         from app.db.models.chat_long_memory_model import ChatLongMemory
        
#         # Verify ownership
#         memory = db.query(ChatLongMemory).filter(
#             ChatLongMemory.id == memory_id,
#             ChatLongMemory.user_id == current_user.id
#         ).first()
        
#         if not memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found or access denied"
#             )
        
#         updated_memory = chat_long_memory_service.update_memory_content(
#             db=db,
#             memory_id=memory_id,
#             update_data=update_data
#         )
        
#         if not updated_memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found"
#             )
        
#         return updated_memory
        
#     except HTTPException:
#         raise
#     except ValueError as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=str(e)
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to update memory: {str(e)}"
#         )


# # ==================== DELETE ====================

# @router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_memory(
#     memory_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Delete a specific memory
    
#     - **memory_id**: UUID of the memory to delete
#     """
#     try:
#         from app.db.models.chat_long_memory_model import ChatLongMemory
        
#         # Verify ownership
#         memory = db.query(ChatLongMemory).filter(
#             ChatLongMemory.id == memory_id,
#             ChatLongMemory.user_id == current_user.id
#         ).first()
        
#         if not memory:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found or access denied"
#             )
        
#         deleted = chat_long_memory_service.delete_memory(db, memory_id)
        
#         if not deleted:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Memory not found"
#             )
        
#         return None  # 204 No Content
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete memory: {str(e)}"
#         )


# @router.delete("/cleanup/old", response_model=MemoryCleanupResponse)
# async def cleanup_old_memories(
#     days_old: int = Query(default=90, ge=1, description="Delete memories older than N days"),
#     min_importance: float = Query(default=0.3, ge=0.0, le=1.0, description="Only delete if importance < N"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Delete old, low-importance memories (memory cleanup)
    
#     - **days_old**: Delete memories older than this many days (minimum 1)
#     - **min_importance**: Only delete if importance is below this threshold (0.0-1.0)
    
#     Returns the number of deleted memories
#     """
#     try:
#         return chat_long_memory_service.delete_old_memories(
#             db=db,
#             user_id=current_user.id,
#             days_old=days_old,
#             min_importance=min_importance
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to cleanup memories: {str(e)}"
#         )


# @router.delete("/cleanup/all", response_model=MemoryCleanupResponse)
# async def delete_all_memories(
#     confirm: bool = Query(..., description="Must be true to confirm deletion"),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """
#     Delete ALL memories for the current user (DANGEROUS!)
    
#     - **confirm**: Must be set to true to confirm this destructive action
    
#     This action cannot be undone. Use with extreme caution.
#     """
#     if not confirm:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Must set confirm=true to delete all memories"
#         )
    
#     try:
#         return chat_long_memory_service.delete_all_memories(
#             db=db,
#             user_id=current_user.id
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to delete all memories: {str(e)}"
#         )