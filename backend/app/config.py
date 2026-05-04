"""应用配置 — 基于 pydantic-settings，从环境变量/.env 读取"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──
    APP_NAME: str = "此刻"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-a-random-secret-key"

    # ── Database ──
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/themoment"
    DATABASE_URL_SYNC: str = ""

    @field_validator("DATABASE_URL_SYNC", mode="before")
    @classmethod
    def build_sync_url(cls, v: str, info) -> str:
        """自动由异步 DSN 推导同步 DSN（供 Alembic 使用）"""
        if v:
            return v
        raw = info.data.get("DATABASE_URL", "")
        return raw.replace("+asyncpg", "+psycopg2")

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── OSS ──
    OSS_ENDPOINT: str = ""
    OSS_ACCESS_KEY_ID: str = ""
    OSS_ACCESS_KEY_SECRET: str = ""
    OSS_BUCKET: str = "themoment-content"
    OSS_REGION: str = "cn-hangzhou"

    # ── CDN ──
    CDN_BASE_URL: str = "https://cdn.themoment.app"
    CDN_EXPIRE_HOURS: int = 24
    CONTENT_EXPIRE_HOURS: int = 24
    CLEANUP_INTERVAL_MINUTES: int = 30

    # ── AI Pipeline ──
    AI_IMAGE_API_URL: str = ""
    AI_IMAGE_API_KEY: str = ""
    AI_AUDIO_API_URL: str = ""
    AI_AUDIO_API_KEY: str = ""

    # ── Apple Sign In ──
    APPLE_TEAM_ID: str = ""
    APPLE_SERVICE_ID: str = "com.themoment.app"
    APPLE_KEY_ID: str = ""
    APPLE_PRIVATE_KEY_PATH: str = ""

    # ── IAP ──
    APP_STORE_SHARED_SECRET: str = ""
    APP_STORE_VERIFY_RECEIPT_URL: str = "https://buy.itunes.apple.com/verifyReceipt"
    APP_STORE_VERIFY_RECEIPT_SANDBOX_URL: str = "https://sandbox.itunes.apple.com/verifyReceipt"

    # ── CMS Admin ──
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # ── JWT ──
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # ── Content ──
    DAILY_CONTENT_PUBLISH_HOUR: int = 6  # 每日内容发布时间（UTC+8 06:00）
    PRESET_COLOR_PALETTES: int = 7  # 预设色板数量（兜底）


@lru_cache()
def get_settings() -> Settings:
    return Settings()
