"""OSS/CDN 存储服务 — 支持阿里云 OSS / AWS S3"""

import hashlib
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import get_settings

settings = get_settings()


async def upload_to_oss(
    data: bytes,
    object_key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """
    上传文件到 OSS，返回 CDN 访问 URL

    支持：
    - 阿里云 OSS (oss2)
    - AWS S3 (boto3)
    - 本地文件系统（开发环境回退）

    CDN URL 格式: {CDN_BASE_URL}/{object_key}
    """
    if not data:
        return ""

    # ── 开发环境：存本地 ──
    if settings.APP_ENV == "development" or not settings.OSS_ENDPOINT:
        return await _upload_local(data, object_key)

    # ── 生产环境：OSS ──
    try:
        # 阿里云 OSS
        if "aliyun" in settings.OSS_ENDPOINT or "oss-cn" in settings.OSS_ENDPOINT:
            return await _upload_aliyun_oss(data, object_key, content_type)
        # AWS S3
        else:
            return await _upload_s3(data, object_key, content_type)
    except Exception:
        # 回退本地
        return await _upload_local(data, object_key)


async def _upload_local(data: bytes, object_key: str) -> str:
    """本地文件存储（开发环境）"""
    import os

    upload_dir = "media"
    file_path = os.path.join(upload_dir, object_key)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(data)

    return f"/media/{object_key}"


async def _upload_aliyun_oss(data: bytes, object_key: str, content_type: str) -> str:
    """阿里云 OSS 上传"""
    import oss2

    auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)

    bucket.put_object(object_key, data, headers={"Content-Type": content_type})

    return f"{settings.CDN_BASE_URL}/{object_key}"


async def _upload_s3(data: bytes, object_key: str, content_type: str) -> str:
    """AWS S3 上传"""
    import boto3

    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.OSS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.OSS_ACCESS_KEY_SECRET,
        endpoint_url=f"https://{settings.OSS_ENDPOINT}" if settings.OSS_ENDPOINT else None,
        region_name=settings.OSS_REGION,
    )

    s3.put_object(
        Bucket=settings.OSS_BUCKET,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )

    return f"{settings.CDN_BASE_URL}/{object_key}"


async def delete_expired_objects(object_keys: list[str]) -> int:
    """
    批量删除 OSS 对象（CDN 过期清理）
    返回成功删除的数量
    """
    if not object_keys:
        return 0

    if settings.APP_ENV == "development" or not settings.OSS_ENDPOINT:
        import os
        deleted = 0
        for key in object_keys:
            path = os.path.join("media", key)
            if os.path.exists(path):
                os.remove(path)
                deleted += 1
        return deleted

    try:
        if "aliyun" in settings.OSS_ENDPOINT or "oss-cn" in settings.OSS_ENDPOINT:
            import oss2
            auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
            bucket = oss2.Bucket(auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET)
            for key in object_keys:
                bucket.delete_object(key)
            return len(object_keys)
        else:
            import boto3
            s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.OSS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.OSS_ACCESS_KEY_SECRET,
            )
            objects = [{"Key": k} for k in object_keys]
            s3.delete_objects(Bucket=settings.OSS_BUCKET, Delete={"Objects": objects})
            return len(object_keys)
    except Exception:
        return 0


def generate_object_key(user_id: str, content_type: str, extension: str) -> str:
    """生成 OSS 对象键名"""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%Y/%m/%d")
    content_hash = hashlib.md5(f"{user_id}{now.timestamp()}".encode()).hexdigest()[:8]
    return f"{content_type}/{date_str}/{content_hash}.{extension}"
