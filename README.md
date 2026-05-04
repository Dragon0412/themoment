# 此刻 (The Moment)

> 沉浸式氛围应用 — 你的数字精神避难所

「此刻」是一款 iOS 沉浸式氛围应用。每天 AI 生成一份独一无二的视听内容（Liquid Glass 视觉 + 氛围音频），阅后即焚，过时不候。没有历史，没有推送——用户因内容品质和 FOMO 效应主动每天回来。

---

## 🎯 MVP 核心功能

| 功能 | 说明 |
|------|------|
| **每日一境** | AI 生成视觉图 + 氛围音频，24h 阅后即逝 |
| **Liquid Glass UI** | 毛玻璃叠加层，视觉与内容融合 |
| **自适应配色** | AI 从视觉图提取色板，UI 自动适配 |
| **音频后台播放** | 锁屏控制 / 后台播放 |
| **横屏 StandBy** | 充电横屏时钟 + 氛围模式 |
| **Apple ID 登录** | Sign in with Apple + 游客模式 |
| **买断内购** | ¥5 一次性解锁（首发 ¥3） |

## 🏗 技术架构

```
┌─────────────────────────────────────────────┐
│             iOS Client (SwiftUI)              │
│     Liquid Glass + AVKit + StoreKit           │
└──────────────────┬──────────────────────────┘
                   │ REST API (HTTPS)
┌──────────────────▼──────────────────────────┐
│           FastAPI Backend (Python)            │
│  Auth │ Content │ Purchase │ CMS            │
│  AI Pipeline │ Color Extract │ OSS/CDN      │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│     PostgreSQL │ Redis │ OSS/S3 │ CDN        │
└─────────────────────────────────────────────┘
```

## 📁 项目结构

```
themoment/
├── ios/                       # iOS 原生客户端 (SwiftUI)
│   └── TheMoment/
│       ├── App.swift          # App 入口 + 导航路由 + 充电检测
│       ├── Info.plist         # 应用配置 (后台音频, 横竖屏)
│       ├── Models/            # Content, User, Config
│       ├── Services/          # APIClient, AuthService, AudioService
│       ├── Views/
│       │   ├── DailyContent/  # 每日一境 + LiquidGlassOverlay
│       │   ├── Auth/          # Apple ID / 游客登录
│       │   ├── StandBy/       # 横屏充电时钟
│       │   └── Purchase/      # ¥5 买断内购页
│       └── Utils/             # Hex颜色, Liquid Glass ViewModifier
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/            # auth, content, purchase, cms
│   │   ├── models/            # User, Content, Purchase
│   │   ├── schemas/           # Pydantic 请求/响应模型
│   │   ├── services/          # AI Pipeline, 色板提取, OSS, 音频
│   │   ├── db/                # 数据库会话 + 基础模型
│   │   └── main.py
│   ├── alembic/               # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
└── docker-compose.yml         # PG + Redis + API 一键启动
```

## 🚀 快速开始

### 后端 (Linux 服务器 / Mac 均可)

```bash
# Docker 一键启动 PostgreSQL + Redis + API
docker compose up -d

# 数据库迁移
docker compose exec api alembic upgrade head

# API 文档 → http://localhost:8000/docs
```

### iOS 客户端 (需要 Mac + Xcode 16+)

```bash
# 1. Clone 仓库到 Mac
git clone https://github.com/Dragon0412/themoment.git
cd themoment

# 2. Xcode → File → New → Project → iOS → App
#    Product Name: TheMoment
#    Interface: SwiftUI
#    Language: Swift
#    保存到 ios/ 同级目录

# 3. 把 ios/TheMoment/ 下所有 .swift 文件拖入 Xcode 项目
#    (Models/, Services/, Views/, Utils/, App.swift)

# 4. 修改 ios/TheMoment/Models/Config.swift 中的 baseURL
#    static let baseURL = "https://你的服务器地址/api/v1"

# 5. ⌘R 运行！
```

> ⚠️ **Swift 5.10 兼容性**: 若编译报 `'Actor' cannot be used as a type`，将 `Services/APIClient.swift` 中的 `actor APIClient` 改为 `final class APIClient`，并删除 `private init()` 前的 `private`（或给 class 内方法加 `@MainActor`）。

## 📡 API 接口

| Method | Path | 说明 |
|--------|------|------|
| POST | `/api/v1/auth/apple` | Apple ID 登录 |
| POST | `/api/v1/auth/guest` | 游客登录 |
| GET | `/api/v1/auth/me` | 当前用户信息 |
| GET | `/api/v1/content/today` | **获取今日内容**（核心） |
| GET | `/api/v1/content/{id}` | 内容详情（分享） |
| POST | `/api/v1/purchase/verify` | IAP 收据验证 |
| GET | `/api/v1/cms/contents` | CMS 内容列表 |
| POST | `/api/v1/cms/contents/generate` | 触发 AI 生成 |
| POST | `/api/v1/cms/contents/{id}/publish` | 发布内容 |
| GET | `/api/v1/cms/stats` | 统计面板 |

## 🧪 环境变量

参考 `backend/.env.example`，关键配置：

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/themoment
AI_IMAGE_API_KEY=sk-xxx        # DALL-E / 图片生成
AI_AUDIO_API_KEY=sk-xxx        # 音频生成
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
APP_STORE_SHARED_SECRET=xxx    # Apple IAP 验证
```

## 📋 开发进度

- [x] FastAPI 后端 (Auth / Content / Purchase / CMS)
- [x] AI Pipeline (图片 + 音频生成 + 色板提取)
- [x] OSS/CDN 存储 (阿里云 / AWS S3 / 本地)
- [x] iOS 客户端 (SwiftUI) — Models / Services / Views
- [x] Liquid Glass 毛玻璃效果
- [x] 横屏 StandBy 时钟模式
- [x] 音频后台播放 + 锁屏控制
- [ ] Xcode 项目配置 + 真机调试
- [ ] StoreKit 内购完整对接
- [ ] CI/CD 部署
- [ ] TestFlight 灰度测试

## 📄 许可

Proprietary — All rights reserved.
