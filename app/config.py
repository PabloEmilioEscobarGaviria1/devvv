from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_url: str = "redis://redis:6379/0"
    upload_dir: str = "/data/uploads"
    output_dir: str = "/data/outputs"
    max_upload_mb: int = 500

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
