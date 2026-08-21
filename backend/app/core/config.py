from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    DEBUG: bool

    HOST: str
    PORT: int

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # LLM provider switch
    LLM_PROVIDER: str = "ollama"   # "ollama" or "gemini"

    OLLAMA_URL: str
    LLM_MODEL: str
    LLM_TIMEOUT: int = 120

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    LLM_CONFIDENCE_THRESHOLD: float | None = None

    coolify_base_url: str
    coolify_api_token: str
    coolify_verify_ssl: bool = True
    coolify_timeout: int = 30

    DUPLICATE_LOG_WINDOW_MINUTES: int = 10

    monitoring_api_key: str

    class Config:
        env_file = ".env"


settings = Settings()