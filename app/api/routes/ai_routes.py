# app/api/v1/ai_router.py
from fastapi import APIRouter, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/ai", tags=["AI Models"])


@router.get("/test")
async def test_ai_connection():
    """Simple test endpoint to check API keys and connectivity."""
    return {
        "message": "AI API is running 🚀",
        "openai_model": settings.OPENAI_MODEL,
        "groq_model": settings.GROQ_MODEL,
    }


@router.post("/openai")
async def ask_openai(prompt: str):
    """Send a prompt to OpenAI and get a response."""
    try:
        response = settings.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return {
            "model": settings.OPENAI_MODEL,
            "response": response.choices[0].message.content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI error: {e}")


@router.post("/groq")
async def ask_groq(prompt: str):
    """Send a prompt to Groq and get a response."""
    try:
        response = settings.groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return {
            "model": settings.GROQ_MODEL,
            "response": response.choices[0].message.content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq error: {e}")


@router.post("/compare")
async def compare_models(prompt: str):
    """Send the same prompt to both models and compare their outputs."""
    try:
        openai_resp = settings.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        groq_resp = settings.groq_client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        return {
            "prompt": prompt,
            "openai": {
                "model": settings.OPENAI_MODEL,
                "response": openai_resp.choices[0].message.content,
            },
            "groq": {
                "model": settings.GROQ_MODEL,
                "response": groq_resp.choices[0].message.content,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {e}")
