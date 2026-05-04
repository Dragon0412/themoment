"""此刻 API — FastAPI Application"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期管理"""
    # 启动时
    yield
    # 关闭时 — 释放数据库连接池等
    from app.db.session import engine
    await engine.dispose()


app = FastAPI(
    title="此刻 API",
    description="沉浸式氛围应用 — 后端服务",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS — 允许 iOS 客户端和 CMS 前端
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://themoment.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.APP_ENV}


# ── 注册路由 ──
from app.api.v1 import auth, content, purchase, cms  # noqa: E402

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(purchase.router, prefix="/api/v1/purchase", tags=["Purchase"])
app.include_router(cms.router, prefix="/api/v1/cms", tags=["CMS"])
