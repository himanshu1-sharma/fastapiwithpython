"""Database session and engine configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# SQLAlchemy engine setup
engine = create_engine(settings.DATABASE_URL, echo=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
