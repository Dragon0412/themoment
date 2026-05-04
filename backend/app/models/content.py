"""内容模型 — 每日AI生成的视听内容（阅后即逝）"""

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ContentMood(str, Enum):
    """情绪标签"""
    CALM = "calm"           # 平静
    FOCUS = "focus"         # 专注
    WARM = "warm"           # 温暖
    MELANCHOLY = "melancholy"  # 忧伤
    ENERGETIC = "energetic"  # 活力
    DREAMY = "dreamy"       # 梦幻
    COZY = "cozy"           # 舒适


class ContentStatus(str, Enum):
    DRAFT = "draft"           # 草稿
    PUBLISHED = "published"   # 已发布
    EXPIRED = "expired"       # 已过期
    ARCHIVED = "archived"     # 永久归档


class Content(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "contents"

    # ── 基本信息 ──
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    mood: Mapped[ContentMood] = mapped_column(
        SAEnum(ContentMood, name="content_mood"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="一句话描述")

    # ── 视觉资源 ──
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False, comment="主视觉图 CDN URL")
    image_oss_key: Mapped[str] = mapped_column(String(512), nullable=False, comment="OSS存储路径")
    thumbnail_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # ── 音频资源 ──
    audio_url: Mapped[str] = mapped_column(String(1024), nullable=False, comment="音频 CDN URL")
    audio_oss_key: Mapped[str] = mapped_column(String(512), nullable=False, comment="OSS存储路径")
    audio_duration_seconds: Mapped[int] = mapped_column(Integer, default=180)

    # ── 色板（自适应配色） ──
    color_palette: Mapped[dict] = mapped_column(
        JSONB, nullable=False, comment="AI提取或预设的色板 {primary, secondary, accent, background, text}"
    )
    palette_source: Mapped[str] = mapped_column(
        String(20), default="ai", comment="色板来源: ai / preset"
    )

    # ── Liquid Glass 参数 ──
    glass_params: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True, comment="{blur: float, saturation: float, tint: hex}"
    )

    # ── AI 生成元数据 ──
    ai_prompt: Mapped[str | None] = mapped_column(Text, nullable=True, comment="生成视觉的Prompt")
    ai_model: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="使用的AI模型")
    ai_quality_score: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="AI质检评分 0-100"
    )

    # ── 生命周期 ──
    status: Mapped[ContentStatus] = mapped_column(
        SAEnum(ContentStatus, name="content_status"), default=ContentStatus.DRAFT
    )
    publish_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="发布日期"
    )
    expire_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, comment="过期时间（24h后）"
    )

    # ── 统计 ──
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    share_count: Mapped[int] = mapped_column(Integer, default=0)
