from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', case_sensitive=False)
    app_name: str = 'CrewOS API'
    environment: str = 'development'
    debug: bool = False
    api_v1_prefix: str = '/api/v1'
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_database: str = 'crewos'
    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cors_origins: str = 'http://localhost:5173'
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_api_version: str | None = None
    azure_gpt_deployment: str | None = None
    @property
    def cors_origin_list(self) -> list[str]: return [origin.strip() for origin in self.cors_origins.split(',')]

@lru_cache
def get_settings() -> Settings: return Settings()
