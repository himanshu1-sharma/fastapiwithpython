from app.api.dependencies.db_dependency import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.chat_memory_service import chat_with_memory_db
from app.schemas.chat_memory_schema import ChatMemoryResponse
from pydantic import BaseModel
from uuid import UUID
from typing import List

router = APIRouter(prefix="/chat-memory", tags=["Chat Memory"])


class ChatRequest(BaseModel):
    user_id: UUID
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        response = chat_with_memory_db(db, request.user_id, request.question)

        # context is already a list of dicts (serialized safely)
        context = response.get("context", [])

        # Directly rename context to sources for your response
        sources = [{"content": doc.get("content", ""), "metadata": doc.get("metadata", {})} for doc in context]

        return {
            "answer": response.get("answer", ""),
            "sources": sources
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/history/{user_id}", response_model=List[ChatMemoryResponse])
async def get_chat_history(user_id: UUID, db: Session = Depends(get_db)):
    from app.repositories.chat_memory_repository import get_user_chat_memory
    history = get_user_chat_memory(db, user_id)
    return history