# app/services/memory_service.py
from sqlalchemy.orm import Session
from app.db.repositories.chat_long_memory_repository import (
    create_chat_long_memory,
    get_recent_memories,
    update_last_used
)
from app.schemas.chat_long_memory_schema import ChatLongMemoryCreate

class ChatLongMemoryService:
    @staticmethod
    def create_memory(db: Session, user_id: str, role: str, content: str, memory_type: str = "row"):
        print(f"🧠 [MEMORY] Creating memory: role={role}, type={memory_type}")
        data = ChatLongMemoryCreate(
            user_id=user_id,
            role=role,
            content=content,
            memory_type=memory_type,
            answer=content  # store same content for compatibility
        )
        new_mem = create_chat_long_memory(db, data)
        print("✅ [MEMORY] Memory saved successfully")
        return new_mem

    @staticmethod
    def get_user_recent_memories(db: Session, user_id: str, limit: int = 10):
        print(f"📜 [MEMORY] Fetching last {limit} memories for user_id={user_id}")
        memories = get_recent_memories(db, user_id, limit)
        print(f"✅ [MEMORY] Retrieved {len(memories)} past memories")
        return {"count": len(memories), "memories": memories}

    @staticmethod
    def touch_memory(db: Session, memory_id):
        print(f"🕒 [MEMORY] Updating last_used_at for memory_id={memory_id}")
        update_last_used(db, memory_id)
