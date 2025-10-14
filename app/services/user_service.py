from sqlalchemy.orm import Session # type: ignore
from app.schemas.user_schema import UserCreate
from app.repositories import user_repository

def list_users(db: Session):
    return user_repository.get_users(db)

def create_user(db: Session, user_data: UserCreate):
    return user_repository.create_user(db, user_data)
