from sqlalchemy.orm import Session # type: ignore
from app.db.models.user_model import User
from app.schemas.user_schema import UserCreate

def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    new_user = User(
        name=user.name, 
        email=user.email, 
        number=user.number, 
        age=user.age, 
        country=user.country,
        profile_pic_url=user.profile_pic_url
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete_user(db: Session, user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user

def update_user_profile_pic(db: Session, user_id, profile_pic_url: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None
    user.profile_pic_url = profile_pic_url
    db.add(user)
    db.commit()
    db.refresh(user)
    return user