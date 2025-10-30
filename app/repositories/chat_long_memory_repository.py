# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime

# from app.db.models.chat_long_memory_model import ChatLongMemory
# from app.schemas.chat_long_memory_schema import ChatLongMemoryCreate

# def create_chat_long_memory(db: Session, data: ChatLongMemoryCreate):
#     new_mem = ChatLongMemory(**data.dict())
#     db.add(new_mem)
#     db.commit()
#     db.refresh(new_mem)
#     return new_mem

# def get_recent_memories(db: Session, user_id, limit: int = 10) -> List[ChatLongMemory]:
#     return (
#         db.query(ChatLongMemory)
#         .filter(ChatLongMemory.user_id == user_id)
#         .order_by(ChatLongMemory.created_at.desc())
#         .limit(limit)
#         .all()
#     )

# def get_all_memories(db: Session, user_id) -> List[ChatLongMemory]:
#     return db.query(ChatLongMemory).filter(ChatLongMemory.user_id == user_id).all()

# def update_last_used(db: Session, memory_id):
#     memory = db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()
#     if memory:
#         memory.last_used_at = datetime.utcnow()
#         db.commit()
#         db.refresh(memory)
#     return memory




"""
Chat Long-Term Memory Repository
Database access layer for long-term memory operations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.db.models.chat_long_memory_model import ChatLongMemory
from app.schemas.chat_long_memory_schema import ChatLongMemoryCreate, ChatLongMemoryUpdate
import logging

logger = logging.getLogger(__name__)


# ==================== CREATE ====================

def create_chat_long_memory(db: Session, data: ChatLongMemoryCreate) -> ChatLongMemory:
    """
    Create a new long-term memory entry
    
    Args:
        db: Database session
        data: ChatLongMemoryCreate schema
    
    Returns:
        Created ChatLongMemory object
    """
    try:
        new_mem = ChatLongMemory(**data.dict(by_alias=True))
        db.add(new_mem)
        db.commit()
        db.refresh(new_mem)
        logger.info(f"Created memory {new_mem.id} for user {new_mem.user_id}")
        return new_mem
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating memory: {e}")
        raise


# ==================== READ ====================

def get_memory_by_id(db: Session, memory_id: UUID) -> Optional[ChatLongMemory]:
    """
    Get a single memory by ID
    
    Args:
        db: Database session
        memory_id: Memory UUID
    
    Returns:
        ChatLongMemory object or None
    """
    return db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()


def get_recent_memories(db: Session, user_id: UUID, limit: int = 10) -> List[ChatLongMemory]:
    """
    Get recent memories for a user
    
    Args:
        db: Database session
        user_id: User UUID
        limit: Number of memories to retrieve
    
    Returns:
        List of ChatLongMemory objects
    """
    return (
        db.query(ChatLongMemory)
        .filter(ChatLongMemory.user_id == user_id)
        .order_by(ChatLongMemory.created_at.desc())
        .limit(limit)
        .all()
    )


def get_all_memories(db: Session, user_id: UUID) -> List[ChatLongMemory]:
    """
    Get all memories for a user
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        List of all ChatLongMemory objects for the user
    """
    return (
        db.query(ChatLongMemory)
        .filter(ChatLongMemory.user_id == user_id)
        .order_by(ChatLongMemory.created_at.desc())
        .all()
    )


def get_memories_by_type(
    db: Session, 
    user_id: UUID, 
    memory_type: str, 
    limit: Optional[int] = None
) -> List[ChatLongMemory]:
    """
    Get memories filtered by type
    
    Args:
        db: Database session
        user_id: User UUID
        memory_type: Type to filter (summary/fact/reflection/note)
        limit: Optional limit on results
    
    Returns:
        List of ChatLongMemory objects
    """
    query = db.query(ChatLongMemory).filter(
        and_(
            ChatLongMemory.user_id == user_id,
            ChatLongMemory.memory_type == memory_type
        )
    ).order_by(ChatLongMemory.created_at.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def get_important_memories(
    db: Session,
    user_id: UUID,
    min_importance: float = 0.7,
    limit: int = 20
) -> List[ChatLongMemory]:
    """
    Get memories above a certain importance threshold
    
    Args:
        db: Database session
        user_id: User UUID
        min_importance: Minimum importance score
        limit: Maximum number of results
    
    Returns:
        List of important ChatLongMemory objects
    """
    return (
        db.query(ChatLongMemory)
        .filter(
            and_(
                ChatLongMemory.user_id == user_id,
                ChatLongMemory.importance_score >= min_importance
            )
        )
        .order_by(
            ChatLongMemory.importance_score.desc(),
            ChatLongMemory.created_at.desc()
        )
        .limit(limit)
        .all()
    )


def search_memories_by_content(
    db: Session,
    user_id: UUID,
    search_term: str,
    limit: int = 20
) -> List[ChatLongMemory]:
    """
    Search memories by content (case-insensitive)
    
    Args:
        db: Database session
        user_id: User UUID
        search_term: Text to search for
        limit: Maximum results
    
    Returns:
        List of matching ChatLongMemory objects
    """
    return (
        db.query(ChatLongMemory)
        .filter(
            and_(
                ChatLongMemory.user_id == user_id,
                ChatLongMemory.content.ilike(f"%{search_term}%")
            )
        )
        .order_by(ChatLongMemory.importance_score.desc())
        .limit(limit)
        .all()
    )


# ==================== UPDATE ====================

def update_last_used(db: Session, memory_id: UUID) -> Optional[ChatLongMemory]:
    """
    Update the last_used_at timestamp
    
    Args:
        db: Database session
        memory_id: Memory UUID
    
    Returns:
        Updated ChatLongMemory object or None
    """
    try:
        memory = db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()
        if memory:
            memory.last_used_at = datetime.utcnow()
            db.commit()
            db.refresh(memory)
            logger.info(f"Updated last_used_at for memory {memory_id}")
        return memory
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating last_used: {e}")
        raise


def update_memory_importance(
    db: Session, 
    memory_id: UUID, 
    new_importance: float
) -> Optional[ChatLongMemory]:
    """
    Update memory importance score
    
    Args:
        db: Database session
        memory_id: Memory UUID
        new_importance: New importance score (0.0 to 1.0)
    
    Returns:
        Updated ChatLongMemory object or None
    """
    try:
        memory = db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()
        if memory:
            # Clamp between 0 and 1
            memory.importance_score = max(0.0, min(1.0, new_importance))
            memory.last_used_at = datetime.utcnow()
            db.commit()
            db.refresh(memory)
            logger.info(f"Updated importance for memory {memory_id} to {memory.importance_score}")
        return memory
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating importance: {e}")
        raise


def update_memory(
    db: Session,
    memory_id: UUID,
    update_data: ChatLongMemoryUpdate
) -> Optional[ChatLongMemory]:
    """
    Update memory with partial data
    
    Args:
        db: Database session
        memory_id: Memory UUID
        update_data: ChatLongMemoryUpdate schema
    
    Returns:
        Updated ChatLongMemory object or None
    """
    try:
        memory = db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()
        if not memory:
            return None
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(memory, field, value)
        
        memory.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        logger.info(f"Updated memory {memory_id}")
        return memory
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating memory: {e}")
        raise


# ==================== DELETE ====================

def delete_memory(db: Session, memory_id: UUID) -> bool:
    """
    Delete a single memory
    
    Args:
        db: Database session
        memory_id: Memory UUID
    
    Returns:
        True if deleted, False if not found
    """
    try:
        memory = db.query(ChatLongMemory).filter(ChatLongMemory.id == memory_id).first()
        if memory:
            db.delete(memory)
            db.commit()
            logger.info(f"Deleted memory {memory_id}")
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting memory: {e}")
        raise


def delete_old_memories(
    db: Session,
    user_id: UUID,
    days_old: int = 90,
    min_importance: float = 0.3
) -> int:
    """
    Delete old, low-importance memories (cleanup)
    
    Args:
        db: Database session
        user_id: User UUID
        days_old: Delete memories older than this
        min_importance: Only delete if importance is below this
    
    Returns:
        Number of deleted memories
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted = db.query(ChatLongMemory).filter(
            and_(
                ChatLongMemory.user_id == user_id,
                ChatLongMemory.created_at < cutoff_date,
                ChatLongMemory.importance_score < min_importance
            )
        ).delete()
        
        db.commit()
        logger.info(f"Deleted {deleted} old memories for user {user_id}")
        return deleted
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting old memories: {e}")
        raise


def delete_all_user_memories(db: Session, user_id: UUID) -> int:
    """
    Delete all memories for a user (use with caution!)
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        Number of deleted memories
    """
    try:
        deleted = db.query(ChatLongMemory).filter(
            ChatLongMemory.user_id == user_id
        ).delete()
        
        db.commit()
        logger.warning(f"Deleted ALL {deleted} memories for user {user_id}")
        return deleted
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting all memories: {e}")
        raise


# ==================== STATISTICS ====================

def get_memory_count(db: Session, user_id: UUID) -> int:
    """Get total memory count for a user"""
    return db.query(func.count(ChatLongMemory.id)).filter(
        ChatLongMemory.user_id == user_id
    ).scalar()


def get_memory_stats(db: Session, user_id: UUID) -> dict:
    """
    Get comprehensive memory statistics
    
    Args:
        db: Database session
        user_id: User UUID
    
    Returns:
        Dictionary with statistics
    """
    # Total count
    total = db.query(func.count(ChatLongMemory.id)).filter(
        ChatLongMemory.user_id == user_id
    ).scalar()
    
    # Count by type
    type_counts = db.query(
        ChatLongMemory.memory_type,
        func.count(ChatLongMemory.id)
    ).filter(
        ChatLongMemory.user_id == user_id
    ).group_by(ChatLongMemory.memory_type).all()
    
    # Average importance
    avg_importance = db.query(
        func.avg(ChatLongMemory.importance_score)
    ).filter(
        ChatLongMemory.user_id == user_id
    ).scalar() or 0.0
    
    # Most recent memory
    most_recent = db.query(ChatLongMemory).filter(
        ChatLongMemory.user_id == user_id
    ).order_by(ChatLongMemory.created_at.desc()).first()
    
    return {
        "total_memories": total,
        "memory_types": {memory_type: count for memory_type, count in type_counts},
        "average_importance": round(float(avg_importance), 2),
        "most_recent_memory": most_recent.created_at if most_recent else None
    }