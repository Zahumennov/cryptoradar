from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str

    # Redis
    redis_url: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CoinGecko
    coingecko_url: str = "https://api.coingecko.com/api/v3"
    price_update_interval: int = 300  # seconds

    # Telegram
    telegram_token: str
    
    # App
    app_name: str = "CryptoRadar"
    debug: bool = False


settings = Settings()