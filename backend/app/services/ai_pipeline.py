"""AI 内容生成 Pipeline — 日更视听内容的自动生产"""

import random
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.content import Content, ContentMood, ContentStatus
from app.services.color_extractor import extract_color_palette, get_preset_palette
from app.services.oss_service import upload_to_oss

settings = get_settings()

# ── 预设 Prompt 模板 ──

MOOD_PROMPTS = {
    ContentMood.CALM: {
        "image": (
            "A serene minimalist zen garden at dawn, soft morning light filtering through "
            "thin mist, shallow depth of field, pastel color grading, 4K, cinematic, "
            "ethereal atmosphere, no text, no watermark, peaceful solitude"
        ),
        "audio": "calm ambient soundscape with gentle water drops and soft wind chimes",
        "title_templates": ["晨光微露", "静水深流", "片刻安宁", "素白时光", "风起微澜"],
    },
    ContentMood.FOCUS: {
        "image": (
            "A clean minimalist workspace with warm desk lamp, raindrops on window, "
            "cozy interior, soft bokeh background, deep focus, muted colors, "
            "4K, cinematic lighting, no text, no watermark"
        ),
        "audio": "low-fi hip hop instrumental with soft rain ambience, steady rhythm",
        "title_templates": ["深夜书桌", "流动的专注", "无声处", "心流时刻", "灯下"],
    },
    ContentMood.WARM: {
        "image": (
            "Golden hour sunlight streaming through window onto wooden floor, "
            "soft shadows, warm cozy interior, nostalgic film grain, "
            "4K, analog photography style, no text, no watermark"
        ),
        "audio": "warm acoustic guitar melody with soft vinyl crackle, intimate atmosphere",
        "title_templates": ["金色时刻", "午后三点", "温柔的光", "老房子", "暖"],
    },
    ContentMood.MELANCHOLY: {
        "image": (
            "Lonely street lamp in rain at blue hour, wet pavement reflections, "
            "cinematic mood, film noir aesthetic, melancholic beauty, "
            "4K, shallow depth of field, no text, no watermark"
        ),
        "audio": "melancholic piano minimal composition with distant rain, slow tempo",
        "title_templates": ["雨夜独行", "未寄出的信", "空房间", "蓝调时分", "远处"],
    },
    ContentMood.ENERGETIC: {
        "image": (
            "Sunrise over misty mountain peaks, golden rays breaking through clouds, "
            "epic landscape, vibrant natural colors, inspirational atmosphere, "
            "4K, wide angle, no text, no watermark"
        ),
        "audio": "upbeat ambient electronic with nature sounds, birds chirping, inspiring",
        "title_templates": ["破晓", "无尽夏", "向上", "旷野的风", "新生"],
    },
    ContentMood.DREAMY: {
        "image": (
            "Aurora borealis over snow-covered forest, magical night sky, "
            "soft purple and green gradients, dreamlike surreal atmosphere, "
            "4K, long exposure, no text, no watermark"
        ),
        "audio": "dreamy ambient pads with twinkling stars sound effect, slow evolving",
        "title_templates": ["梦境入口", "星尘", "漂浮", "极光之下", "失重"],
    },
    ContentMood.COZY: {
        "image": (
            "Cozy reading nook with cat sleeping by fireplace, warm interior, "
            "bookshelves, soft knitted blanket texture, hygge lifestyle, "
            "4K, warm color palette, no text, no watermark"
        ),
        "audio": "soft jazz piano with fireplace crackling, comfortable home atmosphere",
        "title_templates": ["炉边", "猫与书", "柔软时光", "归处", "慵懒午后"],
    },
}


async def call_ai_image_api(prompt: str) -> bytes:
    """
    调用 AI 图片生成 API (DALL-E / Midjourney / Stable Diffusion)
    当前为模拟实现，生产环境替换为真实调用
    """
    if not settings.AI_IMAGE_API_KEY:
        # 开发环境返回占位
        raise RuntimeError("AI_IMAGE_API_KEY 未配置")

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.AI_IMAGE_API_URL}/images/generations",
            headers={"Authorization": f"Bearer {settings.AI_IMAGE_API_KEY}"},
            json={
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": "1024x1792",  # 竖屏比例
                "quality": "hd",
            },
        )
        data = resp.json()

    # DALL-E 返回 URL，需要下载图片字节
    image_url = data["data"][0]["url"]
    async with httpx.AsyncClient() as client:
        img_resp = await client.get(image_url)
        return img_resp.content


async def call_ai_audio_api(prompt: str, duration_seconds: int = 180) -> bytes:
    """
    调用 AI 音频生成 API (Suno / Mubert / AudioCraft)
    当前为模拟实现，生产环境替换为真实调用
    """
    if not settings.AI_AUDIO_API_KEY:
        raise RuntimeError("AI_AUDIO_API_KEY 未配置")

    # 模拟：返回空字节（生产环境实现真实调用）
    # async with httpx.AsyncClient(timeout=180) as client:
    #     ...
    return b""


async def generate_daily_content(
    db: AsyncSession,
    mood: ContentMood = ContentMood.CALM,
) -> Content:
    """
    每日内容生成主流程：
    1. 根据情绪选择 Prompt
    2. 调用 AI 生成视觉图
    3. 调用 AI 生成音频
    4. 色板提取
    5. 上传 OSS
    6. 创建 Content 记录
    """
    prompt_config = MOOD_PROMPTS.get(mood, MOOD_PROMPTS[ContentMood.CALM])
    title = random.choice(prompt_config["title_templates"])

    # ── Step 1: 生成视觉图 ──
    try:
        image_bytes = await call_ai_image_api(prompt_config["image"])
    except Exception:
        image_bytes = None

    # ── Step 2: 色板提取 ──
    try:
        if image_bytes:
            palette = extract_color_palette(image_bytes)
        else:
            palette = get_preset_palette(mood)
    except Exception:
        palette = get_preset_palette(mood)

    # ── Step 3: 生成音频 ──
    try:
        audio_bytes = await call_ai_audio_api(prompt_config["audio"], duration_seconds=180)
    except Exception:
        audio_bytes = None

    # ── Step 4: 上传 OSS ──
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y%m%d")
    content_uuid = f"{date_str}_{mood.value}"

    image_url = ""
    audio_url = ""
    image_oss_key = ""
    audio_oss_key = ""

    if image_bytes:
        image_oss_key = f"contents/{date_str}/{content_uuid}_image.png"
        image_url = await upload_to_oss(image_bytes, image_oss_key, content_type="image/png")

    if audio_bytes:
        audio_oss_key = f"contents/{date_str}/{content_uuid}_audio.mp3"
        audio_url = await upload_to_oss(audio_bytes, audio_oss_key, content_type="audio/mpeg")

    # ── Step 5: 创建数据库记录 ──
    content = Content(
        title=title,
        mood=mood,
        description=f"「{title}」— 一份{mood.value}的此刻",
        image_url=image_url or "",
        image_oss_key=image_oss_key or "",
        audio_url=audio_url or "",
        audio_oss_key=audio_oss_key or "",
        audio_duration_seconds=180,
        color_palette=palette,
        palette_source="ai" if image_bytes else "preset",
        glass_params={
            "blur": 25.0,
            "saturation": 1.1,
            "tint": palette.get("primary", "#FFFFFF"),
        },
        ai_prompt=prompt_config["image"],
        ai_model="dall-e-3",
        status=ContentStatus.DRAFT,
        publish_date=now,
        expire_at=now + settings.CONTENT_EXPIRE_HOURS,
    )

    db.add(content)
    await db.flush()
    return content
