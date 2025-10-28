from fastapi import APIRouter
from app.services.ai_memory_service import chat_with_memory

router = APIRouter(prefix="/ai-memory", tags=["AI Memory"])

chat_history = []  # Temporary memory (we’ll persist it later)

@router.post("/chat")
async def chat_endpoint(prompt: str):
    global chat_history
    response = chat_with_memory(prompt, chat_history)
    chat_history.append((prompt, response["answer"]))
    return {"answer": response["answer"], "sources": response.get("context", [])}
