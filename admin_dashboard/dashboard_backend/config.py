from pydantic import BaseModel, Field
# from pydantic_settings import BaseSettings
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DATABASE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()
