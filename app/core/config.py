# app/core/config.py
from pydantic_settings import BaseSettings
from openai import OpenAI
from groq import Groq


class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str

    # Database configuration
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # AWS/S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str

    # AI API Keys
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    GROQ_API_KEY: str  # 👈 Added GROQ key
    GROQ_MODEL: str

    # AI clients as properties to avoid Pydantic field validation errors
    @property
    def openai_client(self):
        return OpenAI(api_key=self.OPENAI_API_KEY)

    @property
    def groq_client(self):
        return Groq(api_key=self.GROQ_API_KEY)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Optional startup diagnostics
        print("🔧 Configuration Summary:")
        print(f"  Environment: {self.APP_ENV}")
        print(f"  Database Host: {self.DB_HOST}")
        print(f"  AWS Region: {self.AWS_REGION}")
        print(f"  S3 Bucket: {self.S3_BUCKET_NAME}")
        print(f"  OpenAI Key Configured: {'✅' if self.OPENAI_API_KEY else '❌'}")
        print(f"  Groq Key Configured: {'✅' if self.GROQ_API_KEY else '❌'}")

    # @property
    # def DATABASE_URL(self) -> str:
    #     return (
    #         f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
    #         f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    #     )

    @property
    def DATABASE_URL(self) -> str:
        # Using your Neon connection string
        return (
            "postgresql://neondb_owner:npg_B63EmIputcSz"
            "@ep-wispy-base-adrsh2bz-pooler.c-2.us-east-1.aws.neon.tech/"
            "neondb?sslmode=require&channel_binding=require"
        )

    class Config:
        env_file = ".env"


settings = Settings()
