"""Env config. Single source of truth for model + constants."""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Settings(BaseModel):
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-5.5"))
    openai_model_reasoning: str = Field(
        default_factory=lambda: os.getenv("OPENAI_MODEL_REASONING", "gpt-5.5")
    )

    max_weight_per_asset: float = Field(
        default_factory=lambda: float(os.getenv("MAX_WEIGHT_PER_ASSET", "0.20"))
    )
    min_assets: int = Field(default_factory=lambda: int(os.getenv("MIN_ASSETS", "5")))
    risk_free_rate: float = Field(
        default_factory=lambda: float(os.getenv("RISK_FREE_RATE", "0.035"))
    )

    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
