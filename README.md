# 此刻 (The Moment)

> 沉浸式氛围应用 — 你的数字精神避难所

「此刻」是一款 iOS 沉浸式氛围应用。每天 AI 生成一份独一无二的视听内容（Liquid Glass 视觉 + 氛围音频），阅后即焚，过时不候。没有历史，没有推送——用户因内容品质和 FOMO 效应主动每天回来。

---

## 🎯 MVP 核心功能

| 功能 | 说明 |
|------|------|
| **每日一境** | AI 生成视觉图 + 氛围音频，24h 阅后即逝 |
| **Liquid Glass UI** | iOS 26 新设计语言，视觉与内容融合 |
| **自适应配色** | AI 从视觉图提取色板，UI 自动适配 |
| **音频后台播放** | 锁屏控制 / 后台播放 |
| **横屏 StandBy** | 充电横屏时钟 + 氛围模式 |
| **Apple ID 登录** | Sign in with Apple + 游客模式 |
| **买断内购** | ¥5 一次性解锁（首发 ¥3） |

## 🏗 技术架构

```
┌─────────────────────────────────────────────┐
│                  iOS Client                  │
│        SwiftUI + Liquid Glass + AVKit        │
└──────────────────┬──────────────────────────┘
                   │ REST API (HTTPS)
┌──────────────────▼──────────────────────────┐
│            FastAPI Backend (Python)           │
│  ┌─────────┬──────────┬──────────┬────────┐ │
│  │  Auth   │ Content  │ Purchase │  CMS   │ │
│  └────┬────┴────┬─────┴────┬─────┴───┬────┘ │
│       │         │          │         │       │
│  ┌────▼─────────▼──────────▼─────────▼────┐ │
│  │           AI Pipeline                   │ │
│  │  Image Gen → Color Extract → Audio Gen  │ │
│  └────────────────┬───────────────────────┘ │
└───────────────────┼─────────────────────────┘
                    │
┌───────────────────▼─────────────────────────┐
│          Infrastructure                      │
│  PostgreSQL │ Redis │ OSS/S3 │ CDN          │
└─────────────────────────────────────────────┘
```

## 📁 项目结构

```
themoment/
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/           # REST API 路由
│   │   │   ├── auth.py       # Apple ID 登录 + 游客 + JWT
│   │   │   ├── content.py    # 每日内容获取
│   │   │   ├── purchase.py   # Apple IAP 收据验证
│   │   │   └── cms.py        # 内容管理后台
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── services/         # 业务逻辑层
│   │   │   ├── ai_pipeline.py     # AI 内容生成流水线
│   │   │   ├── color_extractor.py # 色板提取
│   │   │   ├── audio_service.py   # 音频处理
│   │   │   └── oss_service.py     # OSS/CDN 存储
│   │   ├── db/               # 数据库会话 + 基础模型
│   │   ├── config.py         # 配置管理
│   │   └── main.py           # FastAPI 入口
│   ├── alembic/              # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml        # 开发环境一键启动
└── docs/
    └── PRD_V3.0.md           # 产品需求文档
```

## 🚀 快速开始

### 环境要求

- Docker & Docker Compose
- Python 3.12+ (本地开发)
- PostgreSQL 16
- Redis 7

### Docker 一键启动

```bash
# 启动全部服务（PostgreSQL + Redis + API）
docker compose up -d

# 运行数据库迁移
docker compose exec api alembic upgrade head

# 访问 API 文档
open http://localhost:8000/docs
```

### 本地开发

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 启动服务
uvicorn app.main:app --reload --port 8000
```

## 📡 API 文档

启动服务后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 核心接口

| Method | Path | 说明 |
|--------|------|------|
| POST | `/api/v1/auth/apple` | Apple ID 登录 |
| POST | `/api/v1/auth/guest` | 游客登录 |
| GET | `/api/v1/auth/me` | 当前用户信息 |
| GET | `/api/v1/content/today` | 获取今日内容 |
| GET | `/api/v1/content/{id}` | 内容详情 |
| POST | `/api/v1/purchase/verify` | IAP 收据验证 |
| GET | `/api/v1/cms/contents` | CMS 内容列表 |
| POST | `/api/v1/cms/contents/generate` | 触发 AI 生成 |
| POST | `/api/v1/cms/contents/{id}/publish` | 发布内容 |
| GET | `/api/v1/cms/stats` | 统计数据 |

## 🧪 环境变量

参考 `backend/.env.example`，关键配置：

```env
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/themoment

# AI 生成 (OpenAI / DALL-E)
AI_IMAGE_API_KEY=sk-xxx
AI_AUDIO_API_KEY=sk-xxx

# OSS 存储 (阿里云 / AWS S3)
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_ACCESS_KEY_ID=xxx
OSS_BUCKET=themoment-content

# Apple IAP
APP_STORE_SHARED_SECRET=xxx
```

## 📋 MVP 里程碑

- [x] 项目骨架 + 数据库设计
- [x] Auth 模块（Apple ID + 游客 + JWT）
- [x] Content API（每日内容获取）
- [x] IAP 购买验证
- [x] CMS 内容管理
- [x] AI Pipeline（视觉 + 音频 + 色板）
- [x] OSS/CDN 存储服务
- [ ] CI/CD 部署
- [ ] 定时内容发布（Celery）
- [ ] iOS 客户端开发

## 📄 许可

Proprietary — All rights reserved.
