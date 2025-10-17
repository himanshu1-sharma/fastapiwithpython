# app/core/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # AWS/S3 (defaults prevent startup failure if env vars are missing)
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(f"AWS Configuration:")
        print(f"  AWS_ACCESS_KEY_ID: {self.AWS_ACCESS_KEY_ID}")
        print(f"  AWS_SECRET_ACCESS_KEY: {self.AWS_SECRET_ACCESS_KEY}")
        print(f"  AWS_REGION: {self.AWS_REGION}")
        print(f"  S3_BUCKET_NAME: {self.S3_BUCKET_NAME}")

    

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
