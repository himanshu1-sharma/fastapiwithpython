from fastapi import FastAPI # type: ignore
from app.api.routes import ai_routes, user_routes
from app.db.init_db import init_db
from app.core.config import settings
from app.core.logging_config import logger

# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME)

# Create DB tables
init_db()

# Register routes
app.include_router(user_routes.router)
app.include_router(ai_routes.router)

@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to FastAPI + PostgreSQL Backend!"}
