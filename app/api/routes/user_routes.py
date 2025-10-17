from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form # type: ignore
from sqlalchemy.orm import Session # type: ignore
from app.api.dependencies.db_dependency import get_db
from app.schemas.user_schema import UserCreate, UserOut
from app.repositories import user_repository
from app.services.s3_service import upload_user_profile_picture
from app.core.logging_config import logger
import uuid

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    return user_repository.get_users(db)

@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_repository.create_user(db, user)

# @router.post("/", response_model=UserOut)
# def create_user(
#     # Option A: send a JSON string with all fields
#     user: str | None = Form(None),
#     # Option B: send individual fields
#     name: str | None = Form(None),
#     email: str | None = Form(None),
#     number: str | None = Form(None),
#     age: int | None = Form(None),
#     country: str | None = Form(None),
#     # Optional file for profile picture (accept either 'file' or 'profile_pic')
#     file: UploadFile | None = File(None),
#     profile_pic: UploadFile | None = File(None),
#     db: Session = Depends(get_db),
# ):
#     logger.info("[Users] Starting create_user handler")

#     user_in: UserCreate | None = None

#     if user is not None:
#         try:
#             logger.info("[Users] Parsing 'user' JSON form field")
#             user_in = UserCreate.model_validate_json(user)
#         except Exception as e:
#             raise HTTPException(status_code=422, detail=f"Invalid user JSON in form field 'user': {e}")
#     else:
#         logger.info("[Users] Using individual form fields")
#         missing = [k for k, v in {
#             "name": name, "email": email, "number": number, "age": age, "country": country
#         }.items() if v is None]
#         if missing:
#             raise HTTPException(
#                 status_code=422,
#                 detail=f"Missing required form fields: {', '.join(missing)}. Either provide 'user' JSON or all fields."
#             )
#         user_in = UserCreate(
#             name=name, email=email, number=number, age=age, country=country, profile_pic_url=None
#         )

#     upload = file or profile_pic
#     if upload is not None:
#         logger.info("[Users] File received for upload: filename=%s content_type=%s", upload.filename, upload.content_type)
#         file_bytes = upload.file.read()
#         size = len(file_bytes)
#         logger.info("[Users] Read file bytes: size=%s", size)
#         if size == 0:
#             raise HTTPException(status_code=422, detail="Uploaded file is empty")
#         try:
#             profile_url = upload_user_profile_picture(file_bytes, upload.filename, upload.content_type)
#             user_in.profile_pic_url = profile_url
#             logger.info("[Users] S3 upload completed. URL stored on user payload")
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {e}")

#     created = user_repository.create_user(db, user_in)
#     logger.info("[Users] User created in DB with id=%s profile_pic_url=%s", created.id, created.profile_pic_url)
#     return created

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
