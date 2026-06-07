from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str

    SECRET_KEY: str

    ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int

    REFRESH_TOKEN_EXPIRE_DAYS: int

    DATABASE_URL: str

    OPENAI_API_KEY: str

    ENCRYPTION_KEY: str

    LOG_LEVEL: str

    class Config:
        env_file = ".env"


settings = Settings()