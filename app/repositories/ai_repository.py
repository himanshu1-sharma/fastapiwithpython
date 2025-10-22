# app/repositories/ai_repository.py
from sqlalchemy.orm import Session
from app.db.models.ai_model import AIResponse
from app.schemas.ai_schema import AIResponseCreate


class AIRepository:
    @staticmethod
    def create_response(db: Session, data: AIResponseCreate) -> AIResponse:
        ai_response = AIResponse(**data.dict())
        db.add(ai_response)
        db.commit()
        db.refresh(ai_response)
        return ai_response

    @staticmethod
    def get_all_responses(db: Session):
        return db.query(AIResponse).order_by(AIResponse.created_at.desc()).all()
