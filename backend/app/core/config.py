from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "Eco Monitoring API"
    api_prefix: str = "/api"
    debug: bool = False

    db_host: str = "mysql"
    db_port: int = 3306
    db_name: str = "eco_monitoring"
    db_user: str = "eco_user"
    db_password: str = "eco_password"

    backend_cors_origins: str = "http://localhost:4200"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

