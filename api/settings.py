from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_host: str = "0.0.0.0"
    app_port: int = 80000

    jwt_secret: str = "SECRET"

    db_url: str = "postgresql+asyncpg://user:pass@localhost/dbname"

    project_root: Path = Path(__name__).parent.resolve()

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
