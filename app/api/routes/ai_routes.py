# # app/api/v1/ai_router.py
# from fastapi import APIRouter, HTTPException
# from app.core.config import settings

# router = APIRouter(prefix="/ai", tags=["AI Models"])


# @router.get("/test")
# async def test_ai_connection():
#     """Simple test endpoint to check API keys and connectivity."""
#     return {
#         "message": "AI API is running 🚀",
#         "openai_model": settings.OPENAI_MODEL,
#         "groq_model": settings.GROQ_MODEL,
#     }


# @router.post("/openai")
# async def ask_openai(prompt: str):
#     """Send a prompt to OpenAI and get a response."""
#     try:
#         response = settings.openai_client.chat.completions.create(
#             model=settings.OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#         )
#         usage = response.usage
#         return {
#             "model": settings.OPENAI_MODEL,
#             "response": response.choices[0].message.content,
#             "usage": {
#                 "prompt_tokens": usage.prompt_tokens,
#                 "completion_tokens": usage.completion_tokens,
#                 "total_tokens": usage.total_tokens,
#             },
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")


# @router.post("/groq")
# async def ask_groq(prompt: str):
#     """Send a prompt to Groq and get a response."""
#     try:
#         response = settings.groq_client.chat.completions.create(
#             model=settings.GROQ_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#         )
#         usage = response.usage
#         return {
#             "model": settings.GROQ_MODEL,
#             "response": response.choices[0].message.content,
#             "usage": {
#                 "prompt_tokens": usage.prompt_tokens,
#                 "completion_tokens": usage.completion_tokens,
#                 "total_tokens": usage.total_tokens,
#             },
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Groq error: {e}")


# @router.post("/compare")
# async def compare_models(prompt: str):
#     """Send the same prompt to both models and compare their outputs."""
#     try:
#         openai_resp = settings.openai_client.chat.completions.create(
#             model=settings.OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#         )

#         groq_resp = settings.groq_client.chat.completions.create(
#             model=settings.GROQ_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#         )

#         return {
#             "prompt": prompt,
#             "openai": {
#                 "model": settings.OPENAI_MODEL,
#                 "response": openai_resp.choices[0].message.content,
#                 "usage": {
#                     "prompt_tokens": openai_resp.usage.prompt_tokens,
#                     "completion_tokens": openai_resp.usage.completion_tokens,
#                     "total_tokens": openai_resp.usage.total_tokens,
#                 },
#             },
#             "groq": {
#                 "model": settings.GROQ_MODEL,
#                 "response": groq_resp.choices[0].message.content,
#                 "usage": {
#                     "prompt_tokens": groq_resp.usage.prompt_tokens,
#                     "completion_tokens": groq_resp.usage.completion_tokens,
#                     "total_tokens": groq_resp.usage.total_tokens,
#                 },
#             },
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Comparison error: {e}")


# app/api/routes/ai_routes.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.api.dependencies.db_dependency import get_db
from app.schemas.ai_schema import AIResponseOut
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate", response_model=AIResponseOut)
async def generate_ai_response(prompt: str, model_type: str, db: Session = Depends(get_db)):
    try:
        result = await AIService.generate_response(db, prompt, model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[AIResponseOut])
async def get_all_ai_responses(db: Session = Depends(get_db)):
    try:
        return await AIService.get_all_responses(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
