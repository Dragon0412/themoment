"""内容 API — 每日一境的获取与互动"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.content import Content, ContentStatus
from app.models.user import User, UserRole
from app.schemas import DailyContentResponse, ColorPalette, GlassParams

router = APIRouter()


@router.get("/today", response_model=DailyContentResponse | None)
async def get_today_content(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取今日内容（阅后即逝核心接口）
    - 游客：可看到今日内容
    - 未购买用户：可看到今日内容（买断制，所有人可看内容）
    - 内容过期时间由 expire_at 字段控制
    """
    now = datetime.now(timezone.utc)

    # 查找今天发布的且未过期的内容
    result = await db.execute(
        select(Content)
        .where(
            Content.status == ContentStatus.PUBLISHED,
            Content.expire_at > now,
        )
        .order_by(Content.publish_date.desc())
        .limit(1)
    )
    content = result.scalar_one_or_none()

    if not content:
        return None  # 今天还没有内容发布

    # 异步更新浏览量（不阻塞响应）
    await db.execute(
        update(Content)
        .where(Content.id == content.id)
        .values(view_count=Content.view_count + 1)
    )

    return DailyContentResponse(
        id=str(content.id),
        title=content.title,
        mood=content.mood.value,
        description=content.description,
        image_url=content.image_url,
        thumbnail_url=content.thumbnail_url,
        audio_url=content.audio_url,
        audio_duration_seconds=content.audio_duration_seconds,
        color_palette=ColorPalette(**content.color_palette),
        glass_params=GlassParams(**content.glass_params) if content.glass_params else None,
        publish_date=content.publish_date,
        expire_at=content.expire_at,
        view_count=content.view_count + 1,
    )


@router.get("/{content_id}", response_model=DailyContentResponse)
async def get_content_by_id(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取指定内容详情（用于分享链接）"""
    result = await db.execute(
        select(Content).where(Content.id == content_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在或已过期")

    return DailyContentResponse(
        id=str(content.id),
        title=content.title,
        mood=content.mood.value,
        description=content.description,
        image_url=content.image_url,
        thumbnail_url=content.thumbnail_url,
        audio_url=content.audio_url,
        audio_duration_seconds=content.audio_duration_seconds,
        color_palette=ColorPalette(**content.color_palette),
        glass_params=GlassParams(**content.glass_params) if content.glass_params else None,
        publish_date=content.publish_date,
        expire_at=content.expire_at,
        view_count=content.view_count,
    )
