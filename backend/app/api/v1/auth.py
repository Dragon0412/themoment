"""认证 API — Apple ID 登录 + 游客模式 + JWT 签发"""

from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas import AppleSignInRequest, GuestLoginRequest, TokenResponse

router = APIRouter()
settings = get_settings()


# ── JWT 工具函数 ──

def create_access_token(user_id: str, is_guest: bool = False) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "is_guest": is_guest,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的访问令牌")


async def get_current_user(
    authorization: str = Header(..., description="Bearer {token}"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """从 Authorization Header 中解析当前用户"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="认证格式错误")
    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="令牌无效")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user


# ── Apple ID 登录 ──

@router.post("/apple", response_model=TokenResponse)
async def apple_sign_in(body: AppleSignInRequest, db: AsyncSession = Depends(get_db)):
    """
    Apple ID 登录
    1. 验证 Apple identity_token（此处为简化版，生产需全量验证）
    2. 创建/查找用户
    3. 返回 JWT
    """
    # 简化版：解析 identity_token 获取 user_identifier
    # 生产环境应使用 apple-sign-in-auth 库或 Apple 公钥验证
    try:
        # 不验证签名，仅解码 base64 payload
        import base64, json
        payload_b64 = body.identity_token.split(".")[1]
        # 补齐 padding
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_b64))
        apple_user_id = payload.get("sub")
    except Exception:
        apple_user_id = body.user_identifier

    if not apple_user_id:
        raise HTTPException(status_code=400, detail="无法获取 Apple 用户标识")

    # 查找或创建用户
    result = await db.execute(
        select(User).where(User.apple_user_id == apple_user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            apple_user_id=apple_user_id,
            role=UserRole.USER,
        )
        db.add(user)
        await db.flush()

    token = create_access_token(str(user.id), is_guest=False)
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        is_premium=user.is_premium,
        is_guest=False,
    )


# ── 游客登录 ──

@router.post("/guest", response_model=TokenResponse)
async def guest_login(body: GuestLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    游客登录 — 基于设备ID创建临时身份
    游客可免费体验，但身份有时效限制
    """
    # 检查是否已有该设备的游客
    result = await db.execute(
        select(User).where(
            User.role == UserRole.GUEST,
            User.device_token == body.device_id,
            User.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            role=UserRole.GUEST,
            device_token=body.device_id,
            guest_expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        db.add(user)
        await db.flush()

    # 检查游客是否过期
    if user.guest_expires_at and user.guest_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="游客体验已过期，请使用 Apple ID 登录")

    token = create_access_token(str(user.id), is_guest=True)
    return TokenResponse(
        access_token=token,
        user_id=str(user.id),
        is_premium=False,
        is_guest=True,
    )


# ── 用户信息 ──

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return {
        "user_id": str(current_user.id),
        "role": current_user.role.value,
        "is_premium": current_user.is_premium,
        "is_guest": current_user.role == UserRole.GUEST,
    }
