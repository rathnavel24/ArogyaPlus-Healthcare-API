from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "mysql+pymysql://arogyaplus:arogyaplus@localhost:3306/arogyaplus"

    # JWT
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Single admin account (used by seed script)
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@arogyaplus.health"
    ADMIN_PASSWORD: str = "change-this-strong-password"

    # WhatsApp Business API
    WHATSAPP_API_URL: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_DESTINATION_NUMBER: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
