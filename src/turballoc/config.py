from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file = ".env", env_file_encoding="utf-8", extra="ignore")
    fred_api_key: str = Field(default = "", alias = "FRED_API_KEY")
    groq_api_key: str = Field(default = "", alias = "GROQ_API_KEY")
    tavily_api_key: str = Field(default = "", alias = "TAVILY_API_KEY")
    groq_model: str = Field(default = "llama-3.3-70b-versatile", alias = "GROQ_MODEL")
    data_dir: Path = Field(default = Path("data"), alias = "DATA_DIR")
    feature_store_path: Path = Field(default=Path("data/processed/features_expanded.duckdb"),
                                     alias = "FEATURE_STORE_PATH")
    forecast_ckpt_path: Path = Field(default=Path("checkpoints/forecast.pt"),
                                     alias = "FORECAST_CKPT_PATH")
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
