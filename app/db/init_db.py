from app.db.session import engine, Base
from app.db.models import user_model

def init_db():
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")
