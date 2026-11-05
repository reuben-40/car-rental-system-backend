from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #JWT signing
    JWT_SECRET: str = Field(
        default="dev-secret-change-in-production-9f8a7b6c5d4e3f2a1",
        alias="JWT_SECRET",
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7 #7 days

    #cors
    FRONTEND_ORIGIN: str = "*"

    @lru_cache
    def get(self) -> "Settings":
        return self

settings = Settings()