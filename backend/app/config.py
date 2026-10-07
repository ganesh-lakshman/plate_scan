from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/plate_scan_db"
    SECRET_KEY: str = "case-study-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ELIGIBILITY_SERVICE_URL: str = "http://localhost:8000/mock/partner-network/eligibility"

    class Config:
        env_file = ".env"


settings = Settings()
