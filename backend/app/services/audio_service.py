"""音频处理服务 — AI 音频生成与格式转换"""

from typing import Optional


async def generate_ambient_audio(
    prompt: str,
    duration_seconds: int = 180,
    output_format: str = "mp3",
) -> Optional[bytes]:
    """
    生成环境音乐/白噪音
    当前为接口预留，实际由 ai_pipeline 统一调度

    支持的生成方式：
    - Suno API (音乐)
    - Mubert API (电子氛围)
    - AudioCraft / Stable Audio (开源方案)
    """
    # 生产环境实现
    return None


def convert_audio_format(audio_bytes: bytes, target_format: str = "mp3") -> bytes:
    """
    音频格式转换 (使用 pydub)
    e.g. WAV → MP3, AAC → MP3 等
    """
    try:
        from pydub import AudioSegment
        import io

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        output = io.BytesIO()
        audio.export(output, format=target_format)
        return output.getvalue()
    except ImportError:
        # pydub 未安装时原样返回
        return audio_bytes
    except Exception:
        return audio_bytes


def get_audio_duration(audio_bytes: bytes) -> float:
    """获取音频时长（秒）"""
    try:
        from pydub import AudioSegment
        import io

        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        return len(audio) / 1000.0
    except Exception:
        return 0.0
