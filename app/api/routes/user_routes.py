from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.api.dependencies.db_dependency import get_db
from app.schemas.user_schema import UserCreate, UserOut
from app.repositories import user_repository
from app.services.s3_service import upload_user_profile_picture
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return user_repository.get_users(db)

@router.post("/", response_model=UserOut)
def create_user(
    user: str = Form(...),
    file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    try:
        user_in = UserCreate.model_validate_json(user)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid user payload: {e}")

    if file is not None:
        file_bytes = file.file.read()
        try:
            profile_url = upload_user_profile_picture(file_bytes, file.filename, file.content_type)
            user_in.profile_pic_url = profile_url
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

    return user_repository.create_user(db, user_in)

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

@router.post("/{user_id}/profile-picture", response_model=UserOut)
def upload_profile_picture(user_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = user_repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    file_bytes = file.file.read()
    try:
        url = upload_user_profile_picture(file_bytes, file.filename, file.content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

    updated = user_repository.update_user_profile_pic(db, user_id, url)
    return updated
