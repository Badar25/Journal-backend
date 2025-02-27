from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    firebase_credentials_base64: str 
    gemini_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()