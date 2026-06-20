from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")
    fred_api_key: str = Field(default = "", alias = "FRED_API_KEY")
    reddit_client_id: str = Field(default = "", alias = "REDDIT_CLIENT_ID")
    reddit_client_secret: str = Field(default = "", alias = "REDDIT_CLIENT_SECRET")
    reddit_user_agent: str = Field(default = "turballoc/0.1", alias = "REDDIT_USER_AGENT")
    newsapi_key: str = Field(default = "", alias = "NEWSAPI_KEY")
    data_dir: Path = Field(default = Path("data"), alias = "DATA_DIR")
    feature_store_path: Path = Field(default=Path("data/processed/features.duckdb"),
                                     alias = "FEATURE_STORE_PATH")
    log_level: str = Field(default = "INFO", alias = "LOG_LEVEL")
    random_seed: int = Field(default = 42, alias = "RANDOM_SEED")

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"
    
    @property
    def processed_dir(self) -> Path:
        return self.data_dir / "processed"
    
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
