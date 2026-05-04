"""CMS API — 内容管理（管理员）"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.db.session import get_db
from app.models.content import Content, ContentMood, ContentStatus
from app.models.user import User, UserRole
from app.schemas import DailyContentResponse, ColorPalette, GlassParams, PaginatedResponse
from app.services.ai_pipeline import generate_daily_content

router = APIRouter()


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


@router.get("/contents", response_model=PaginatedResponse)
async def list_contents(
    page: int = 1,
    page_size: int = 20,
    status: ContentStatus | None = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """列出所有内容（分页）"""
    query = select(Content)
    count_query = select(func.count(Content.id))

    if status:
        query = query.where(Content.status == status)
        count_query = count_query.where(Content.status == status)

    query = query.order_by(Content.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query)
    contents = result.scalars().all()

    items = [
        {
            "id": str(c.id),
            "title": c.title,
            "mood": c.mood.value,
            "status": c.status.value,
            "publish_date": c.publish_date.isoformat() if c.publish_date else None,
            "expire_at": c.expire_at.isoformat(),
            "view_count": c.view_count,
            "ai_quality_score": c.ai_quality_score,
        }
        for c in contents
    ]

    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/contents/generate", response_model=dict)
async def trigger_content_generation(
    mood: ContentMood = ContentMood.CALM,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    触发 AI 内容生成
    生成视觉图 + 音频 + 色板提取 → 存入 OSS → 录入数据库（DRAFT状态）
    """
    try:
        content = await generate_daily_content(db, mood=mood)
        return {
            "success": True,
            "content_id": str(content.id),
            "title": content.title,
            "mood": content.mood.value,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 内容生成失败: {str(e)}")


@router.post("/contents/{content_id}/publish")
async def publish_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """发布内容 — 设为 PUBLISHED，设置过期时间"""
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    now = datetime.now(timezone.utc)
    content.status = ContentStatus.PUBLISHED
    content.publish_date = now
    content.expire_at = now + timedelta(hours=24)
    await db.flush()

    return {"success": True, "message": f"内容「{content.title}」已发布", "expire_at": content.expire_at.isoformat()}


@router.post("/contents/{content_id}/archive")
async def archive_content(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """归档内容 — 永久保存"""
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    content.status = ContentStatus.ARCHIVED
    await db.flush()

    return {"success": True, "message": f"内容「{content.title}」已归档"}


@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """获取统计数据"""
    # 总用户数
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0
    # 总内容数
    content_count = (await db.execute(select(func.count(Content.id)))).scalar() or 0
    # 总浏览量
    view_result = await db.execute(select(func.sum(Content.view_count)))
    total_views = view_result.scalar() or 0
    # Premium 用户数
    premium_result = await db.execute(
        select(func.count(User.id)).where(User.is_premium == True)
    )
    premium_count = premium_result.scalar() or 0

    return {
        "total_users": user_count,
        "premium_users": premium_count,
        "total_contents": content_count,
        "total_views": total_views,
        "conversion_rate": f"{(premium_count / user_count * 100):.1f}%" if user_count > 0 else "0%",
    }
