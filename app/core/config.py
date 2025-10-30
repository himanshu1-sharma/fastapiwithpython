from openai import OpenAI
from groq import Groq
import requests
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str
    APP_ENV: str

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    S3_BUCKET_NAME: str

    # AI Keys
    OPENAI_API_KEY: str
    OPENAI_MODEL: str
    GROQ_API_KEY: str
    GROQ_MODEL: str
    TAVILY_API_KEY: str

    # Bot Info
    BOT_NAME: str
    CREATOR_NAME: str

    # Clients
    @property
    def openai_client(self):
        return OpenAI(api_key=self.OPENAI_API_KEY)

    @property
    def groq_client(self):
        return Groq(api_key=self.GROQ_API_KEY)

    @property
    def tavily_client(self):
        class TavilyClient:
            def __init__(self, api_key: str):
                self.api_key = api_key
                self.base_url = "https://api.tavily.com/search"

            def search(self, query: str):
                payload = {"query": query, "api_key": self.api_key}
                try:
                    response = requests.post(self.base_url, json=payload)
                    return response.json().get("results", [])
                except Exception as e:
                    print(f"❌ Tavily client error: {e}")
                    return []

        return TavilyClient(api_key=self.TAVILY_API_KEY)

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
