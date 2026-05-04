"""购买记录模型 — Apple IAP 收据验证"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Purchase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "purchases"

    # ── 关联 ──
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("users.id"), nullable=False, index=True
    )

    # ── 交易信息 ──
    transaction_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="Apple 交易ID"
    )
    product_id: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="商品ID (e.g. com.themoment.premium)"
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False, comment="实际支付金额（元）")
    currency: Mapped[str] = mapped_column(String(10), default="CNY")

    # ── 收据 ──
    receipt_data: Mapped[str] = mapped_column(Text, nullable=False, comment="Base64 编码的收据")
    is_sandbox: Mapped[bool] = mapped_column(Boolean, default=False, comment="沙箱环境？")

    # ── 验证状态 ──
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, comment="Apple 验证通过？")
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
