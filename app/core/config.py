from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Library API"
    debug: bool = False

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
