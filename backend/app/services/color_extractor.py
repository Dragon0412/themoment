"""色板提取服务 — 从视觉图中提取自适应配色方案

工作原理：
1. 主方案：使用 K-Means 聚类提取主导色（5色）
2. 兜底方案：7套预设色板，由设计师调校
"""

import io
from typing import Optional

from PIL import Image

from app.models.content import ContentMood

# ── 7套预设色板（设计师调校兜底） ──

PRESET_PALETTES = {
    ContentMood.CALM: {
        "primary": "#6B9080",
        "secondary": "#A4C3B2",
        "accent": "#CCE3DE",
        "background": "#F6FFF8",
        "text": "#2D3A32",
    },
    ContentMood.FOCUS: {
        "primary": "#4A5568",
        "secondary": "#718096",
        "accent": "#A0AEC0",
        "background": "#EDF2F7",
        "text": "#1A202C",
    },
    ContentMood.WARM: {
        "primary": "#DD6B4D",
        "secondary": "#E8927C",
        "accent": "#F5C4B3",
        "background": "#FFF5F0",
        "text": "#3D2015",
    },
    ContentMood.MELANCHOLY: {
        "primary": "#5B6E8A",
        "secondary": "#8A9BB5",
        "accent": "#B8C5D6",
        "background": "#E8ECF1",
        "text": "#1E2533",
    },
    ContentMood.ENERGETIC: {
        "primary": "#E8923F",
        "secondary": "#F4B86B",
        "accent": "#FFE0A3",
        "background": "#FFF8EC",
        "text": "#3A2A10",
    },
    ContentMood.DREAMY: {
        "primary": "#7C5CBF",
        "secondary": "#A78BDB",
        "accent": "#D4BFFF",
        "background": "#F5F0FF",
        "text": "#2A1F42",
    },
    ContentMood.COZY: {
        "primary": "#C0885A",
        "secondary": "#D4A87C",
        "accent": "#E8CCB0",
        "background": "#FDF6EE",
        "text": "#3D2B1A",
    },
}


def extract_color_palette(image_bytes: bytes, num_colors: int = 5) -> dict[str, str]:
    """
    从图片中提取主导色板
    使用 Pillow + 简单量化（生产环境可换 colorgram.py 或 K-Means）

    Returns:
        {"primary": "#XXXXXX", "secondary": "...", "accent": "...", "background": "...", "text": "..."}
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB")

        # 缩放到 200x200 加速处理
        img_small = img.resize((200, 200), Image.LANCZOS)

        # 量化到 16 色
        img_quantized = img_small.quantize(colors=num_colors + 2)
        palette_img = img_quantized.convert("RGB")

        # 获取调色板
        palette = img_quantized.getpalette()[: num_colors * 3]
        colors = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i], palette[i + 1], palette[i + 2]
            colors.append(f"#{r:02X}{g:02X}{b:02X}")

        # 按亮度排序：暗色 → 文字色，亮色 → 背景色
        def brightness(hex_color: str) -> float:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            return 0.299 * r + 0.587 * g + 0.114 * b

        colors.sort(key=brightness)

        return {
            "primary": colors[-1] if len(colors) > 0 else "#6B9080",
            "secondary": colors[-2] if len(colors) > 1 else "#A4C3B2",
            "accent": colors[-3] if len(colors) > 2 else "#CCE3DE",
            "background": colors[0] if len(colors) > 3 else "#F6FFF8",
            "text": colors[1] if len(colors) > 4 else "#2D3A32",
        }
    except Exception:
        raise


def get_preset_palette(mood: ContentMood) -> dict[str, str]:
    """获取预设色板（兜底方案）"""
    return PRESET_PALETTES.get(mood, PRESET_PALETTES[ContentMood.CALM])
