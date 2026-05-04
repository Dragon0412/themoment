"""Pydantic Schemas — 请求/响应模型"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ══════════════════════════════════════════════
# 通用
# ══════════════════════════════════════════════

class PaginatedResponse(BaseModel):
    """分页响应"""
    items: list
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    detail: str


# ══════════════════════════════════════════════
# Auth
# ══════════════════════════════════════════════

class AppleSignInRequest(BaseModel):
    """Apple ID 登录请求"""
    identity_token: str = Field(..., description="Apple 返回的 identityToken (JWT)")
    authorization_code: str = Field(..., description="Apple 返回的 authorizationCode")
    user_identifier: str | None = Field(None, description="Apple 用户唯一标识")


class GuestLoginRequest(BaseModel):
    """游客登录请求"""
    device_id: str = Field(..., description="设备唯一标识")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    is_premium: bool
    is_guest: bool


# ══════════════════════════════════════════════
# Content
# ══════════════════════════════════════════════

class ColorPalette(BaseModel):
    primary: str = Field(..., description="主色 HEX")
    secondary: str = Field(..., description="辅色 HEX")
    accent: str = Field(..., description="强调色 HEX")
    background: str = Field(..., description="背景色 HEX")
    text: str = Field(..., description="文字色 HEX")


class GlassParams(BaseModel):
    blur: float = Field(20.0, ge=0, le=50)
    saturation: float = Field(1.0, ge=0, le=3)
    tint: str = Field("#FFFFFF")


class DailyContentResponse(BaseModel):
    """客户端获取每日内容的响应"""
    id: str
    title: str
    mood: str
    description: str | None
    image_url: str
    thumbnail_url: str | None
    audio_url: str
    audio_duration_seconds: int
    color_palette: ColorPalette
    glass_params: GlassParams | None
    publish_date: datetime | None
    expire_at: datetime
    view_count: int


# ══════════════════════════════════════════════
# Purchase
# ══════════════════════════════════════════════

class PurchaseVerifyRequest(BaseModel):
    """iOS 客户端提交的收据验证请求"""
    receipt_data: str = Field(..., description="Base64 编码的 App Store 收据")
    transaction_id: str = Field(..., description="Apple 交易ID")
    product_id: str = Field(..., description="商品ID")


class PurchaseVerifyResponse(BaseModel):
    success: bool
    message: str
    is_premium: bool = False
