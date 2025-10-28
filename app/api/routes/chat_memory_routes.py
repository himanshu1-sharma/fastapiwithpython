from sqlalchemy.orm import Session
from app.api.dependencies.db_dependency import get_db
from app.services.chat_memory_service import chat_with_memory_db
from fastapi import APIRouter, Depends, HTTPException # type: ignore
from app.services.ai_memory_service import chat_with_memory

router = APIRouter(prefix="/chat-memory", tags=["Chat Memory"])

chat_history = []  # Temporary memory (we’ll persist it later)

@router.post("/chat/{user_id}")
async def chat_with_memory(user_id: str, prompt: str, db: Session = Depends(get_db)):
    try:
        response = chat_with_memory_db(db, user_id, prompt)
        return {"answer": response["answer"], "sources": response.get("context", [])}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
