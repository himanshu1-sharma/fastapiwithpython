# app/services/ai_service.py
from app.core.config import settings
from app.repositories.ai_repository import AIRepository
from app.schemas.ai_schema import AIResponseCreate
from sqlalchemy.orm import Session


class AIService:
    @staticmethod
    async def generate_response(db: Session, prompt: str, model_type: str):
        # Select client and model based on type
        if model_type.lower() == "openai":
            response = settings.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            model_name = settings.OPENAI_MODEL
        elif model_type.lower() == "groq":
            response = settings.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            model_name = settings.GROQ_MODEL
        else:
            raise ValueError("Invalid model_type. Use 'openai' or 'groq'.")

        # Extract usage safely
        usage = response.usage if hasattr(response, "usage") else None

        data = AIResponseCreate(
            prompt=prompt,
            response=response.choices[0].message.content,
            model=model_name,
            prompt_tokens=usage.prompt_tokens if usage else None,
            completion_tokens=usage.completion_tokens if usage else None,
            total_tokens=usage.total_tokens if usage else None,
        )

        return AIRepository.create_response(db, data)

    @staticmethod
    async def get_all_responses(db: Session):
        return AIRepository.get_all_responses(db)
