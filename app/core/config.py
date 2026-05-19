from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file.

    Requires DATABASE_URL to be set (e.g. sqlite:///./data/db.sqlite3).
    """

    DATABASE_URL: str

    model_config = {"env_file": ".env"}


settings = Settings()
