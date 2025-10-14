from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.api.dependencies.db_dependency import get_db
from app.schemas.user_schema import UserCreate, UserOut
from app.repositories import user_repository
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return user_repository.get_users(db)

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_repository.create_user(db, user)

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id, db: Session = Depends(get_db)):
    user = user_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
def delete_user(user_id, db: Session = Depends(get_db)):
    deleted = user_repository.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
