from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    api_key: str = os.getenv("WATCHDOG_API_KEY", "dev-watchdog-key")
    env: str = os.getenv("WATCHDOG_ENV", "dev")
    database_url: str = os.getenv("WATCHDOG_DATABASE_URL", "sqlite:///./data/watchdog.db")
    monitor_interval_sec: int = int(os.getenv("WATCHDOG_MONITOR_INTERVAL_SEC", "15"))
    synthetics_interval_sec: int = int(os.getenv("WATCHDOG_SYNTHETICS_INTERVAL_SEC", "30"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
