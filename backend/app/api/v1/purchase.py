"""内购 API — Apple IAP 收据验证"""

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.config import get_settings
from app.db.session import get_db
from app.models.purchase import Purchase
from app.models.user import User
from app.schemas import PurchaseVerifyRequest, PurchaseVerifyResponse

router = APIRouter()
settings = get_settings()


async def verify_receipt_with_apple(receipt_data: str, is_sandbox: bool = False) -> dict:
    """
    向 Apple 服务器验证收据
    返回解析后的收据信息
    """
    verify_url = (
        settings.APP_STORE_VERIFY_RECEIPT_SANDBOX_URL
        if is_sandbox
        else settings.APP_STORE_VERIFY_RECEIPT_URL
    )

    payload = {
        "receipt-data": receipt_data,
        "password": settings.APP_STORE_SHARED_SECRET,
        "exclude-old-transactions": True,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(verify_url, json=payload)
        result = resp.json()

    # Apple 返回 21007 = 沙箱收据发到了生产环境，需要重试
    if result.get("status") == 21007 and not is_sandbox:
        return await verify_receipt_with_apple(receipt_data, is_sandbox=True)

    return result


@router.post("/verify", response_model=PurchaseVerifyResponse)
async def verify_purchase(
    body: PurchaseVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    验证 Apple 内购收据
    1. 向 Apple 服务器验证收据
    2. 记录购买信息
    3. 更新用户 Premium 状态
    """
    # 检查重复交易
    existing = await db.execute(
        select(Purchase).where(Purchase.transaction_id == body.transaction_id)
    )
    if existing.scalar_one_or_none():
        return PurchaseVerifyResponse(
            success=True,
            message="该交易已验证过",
            is_premium=current_user.is_premium,
        )

    # 验证收据
    try:
        apple_result = await verify_receipt_with_apple(body.receipt_data)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Apple 验证服务不可用: {str(e)}")

    if apple_result.get("status") != 0:
        return PurchaseVerifyResponse(
            success=False,
            message=f"收据验证失败 (status={apple_result.get('status')})",
        )

    # 创建购买记录
    receipt_info = apple_result.get("receipt", {})
    purchase = Purchase(
        user_id=current_user.id,
        transaction_id=body.transaction_id,
        product_id=body.product_id,
        amount=5.0,  # 首发 ¥3，正式 ¥5；这里默认 ¥5
        receipt_data=body.receipt_data,
        is_sandbox=(apple_result.get("environment") == "Sandbox"),
        is_verified=True,
    )
    db.add(purchase)

    # 更新用户 Premium 状态
    current_user.is_premium = True
    from datetime import datetime, timezone
    current_user.purchased_at = datetime.now(timezone.utc)
    await db.flush()

    return PurchaseVerifyResponse(
        success=True,
        message="购买验证成功，已解锁全部体验",
        is_premium=True,
    )
