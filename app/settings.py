from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: AnyUrl = "postgres://user:pass@localhost:5432/special_bot"
    ROBOKASSA_LOGIN: str | None = None
    ROBOKASSA_PASSWORD1: str | None = None
    ROBOKASSA_PASSWORD2: str | None = None
    ROBOKASSA_TEST_PASSWORD1: str | None = None
    ROBOKASSA_TEST_PASSWORD2: str | None = None
    ROBOKASSA_URL: str = "https://auth.robokassa.ru/Merchant/Index.aspx"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8082
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str | None = None
    INFO_CHAT: str | None = None
    
    # Backend settings
    BACKEND_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()


