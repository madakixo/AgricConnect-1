from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    APP_ENV: str = "development"
    DEBUG: bool = False

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ISSUER: str = "agricconnect-api"
    JWT_AUDIENCE: str = "agricconnect-clients"

    CORS_ALLOWED_ORIGINS: str = ""
    TRUSTED_HOSTS: str = ""

    MAX_CONTENT_LENGTH: int = 8 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE: int = 2 * 1024 * 1024
    MAX_FORM_PARTS: int = 50
    MAX_IMAGE_COUNT: int = 5
    ALLOWED_IMAGE_MIME_TYPES: str = "image/jpeg,image/png,image/webp"

    SESSION_COOKIE_SECURE: bool = False
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    ENABLE_CLOUDINARY: bool = False
    CLOUDINARY_CLOUD_NAME: str | None = None
    CLOUDINARY_API_KEY: str | None = None
    CLOUDINARY_API_SECRET: str | None = None

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        normalized = value.strip().lower()
        allowed = {"development", "staging", "production", "test"}
        if normalized not in allowed:
            raise ValueError(f"APP_ENV must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("SESSION_COOKIE_SAMESITE")
    @classmethod
    def validate_samesite(cls, value: str) -> str:
        normalized = value.strip().capitalize()
        allowed = {"Lax", "Strict", "None"}
        if normalized not in allowed:
            raise ValueError(f"SESSION_COOKIE_SAMESITE must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def trusted_hosts(self) -> list[str]:
        return [host.strip() for host in self.TRUSTED_HOSTS.split(",") if host.strip()]

    @property
    def allowed_image_mime_types(self) -> set[str]:
        return {item.strip().lower() for item in self.ALLOWED_IMAGE_MIME_TYPES.split(",") if item.strip()}

    @property
    def session_cookie_secure(self) -> bool:
        return self.SESSION_COOKIE_SECURE or self.is_production

    @property
    def cloudinary_enabled(self) -> bool:
        required_values = (
            self.CLOUDINARY_CLOUD_NAME,
            self.CLOUDINARY_API_KEY,
            self.CLOUDINARY_API_SECRET,
        )
        return self.ENABLE_CLOUDINARY and all(required_values)


settings = Settings()
