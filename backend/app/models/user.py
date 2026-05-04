"""用户模型 — 支持 Apple ID 登录 + 游客模式"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class UserRole(str, Enum):
    GUEST = "guest"       # 游客
    USER = "user"         # 注册用户（Apple ID 登录）
    ADMIN = "admin"       # 管理员（CMS）


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    # ── 身份 ──
    apple_user_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True, comment="Apple ID 用户标识"
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), default=UserRole.GUEST, nullable=False
    )

    # ── 购买状态 ──
    is_premium: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="是否已买断（¥5）"
    )
    purchased_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="买断时间"
    )

    # ── 设备 ──
    device_token: Mapped[str | None] = mapped_column(
        String(512), nullable=True, comment="APNs 设备令牌（V2 推送预留）"
    )

    # ── 游客专属 ──
    guest_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, comment="游客身份过期时间"
    )

    # ── 状态 ──
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def is_guest(self) -> bool:
        return self.role == UserRole.GUEST

    def has_purchased(self) -> bool:
        return self.is_premium
