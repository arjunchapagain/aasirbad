"""
Storage service.

Supports local filesystem storage (for development) and AWS S3 (for production).
The backend is selected via the STORAGE_BACKEND env var.
"""

import io
import os
import shutil
import uuid
from pathlib import Path

from app.config import get_settings

settings = get_settings()


# ── Abstract-ish interface ───────────────────────────────────────────────────

class StorageService:
    """Base storage interface."""

    def upload_audio(self, file_bytes: bytes, voice_profile_id: str, filename: str, content_type: str = "audio/wav") -> str:
        raise NotImplementedError

    def upload_processed_audio(self, file_bytes: bytes, voice_profile_id: str) -> str:
        raise NotImplementedError

    def upload_model(self, model_bytes: bytes, voice_profile_id: str) -> str:
        raise NotImplementedError

    def download_file(self, key: str, bucket: str | None = None) -> bytes:
        raise NotImplementedError

    def download_model(self, key: str) -> bytes:
        raise NotImplementedError

    def get_presigned_url(self, key: str, bucket: str | None = None, expires_in: int = 3600) -> str:
        raise NotImplementedError

    def delete_file(self, key: str, bucket: str | None = None) -> None:
        raise NotImplementedError

    def list_recordings(self, voice_profile_id: str) -> list[str]:
        raise NotImplementedError

    def file_exists(self, key: str, bucket: str | None = None) -> bool:
        raise NotImplementedError


# ── Local Filesystem Storage ─────────────────────────────────────────────────

class LocalStorageService(StorageService):
    """Stores files on the local filesystem — ideal for development."""

    def __init__(self):
        self.base_dir = Path(settings.local_storage_dir).resolve()
        self.audio_dir = self.base_dir / "audio"
        self.model_dir = self.base_dir / "models"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def _write(self, rel_key: str, data: bytes, base: Path | None = None) -> str:
        dest = (base or self.audio_dir) / rel_key
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return rel_key

    def upload_audio(self, file_bytes: bytes, voice_profile_id: str, filename: str, content_type: str = "audio/wav") -> str:
        ext = Path(filename).suffix or ".wav"
        key = f"recordings/{voice_profile_id}/{uuid.uuid4().hex}{ext}"
        return self._write(key, file_bytes)

    def upload_processed_audio(self, file_bytes: bytes, voice_profile_id: str) -> str:
        key = f"processed/{voice_profile_id}/{uuid.uuid4().hex}.wav"
        return self._write(key, file_bytes)

    def upload_model(self, model_bytes: bytes, voice_profile_id: str) -> str:
        key = f"models/{voice_profile_id}/voice_model.pth"
        return self._write(key, model_bytes, base=self.model_dir)

    def download_file(self, key: str, bucket: str | None = None) -> bytes:
        base = self.model_dir if bucket == "models" else self.audio_dir
        path = base / key
        if not path.exists():
            raise FileNotFoundError(f"File not found: {key}")
        return path.read_bytes()

    def download_model(self, key: str) -> bytes:
        return self.download_file(key, bucket="models")

    def get_presigned_url(self, key: str, bucket: str | None = None, expires_in: int = 3600) -> str:
        # For local dev, return a URL that the FastAPI static file endpoint serves
        return f"/api/v1/files/{key}"

    def delete_file(self, key: str, bucket: str | None = None) -> None:
        base = self.model_dir if bucket == "models" else self.audio_dir
        path = base / key
        if path.exists():
            path.unlink()

    def list_recordings(self, voice_profile_id: str) -> list[str]:
        folder = self.audio_dir / "processed" / voice_profile_id
        if not folder.exists():
            return []
        return [f"processed/{voice_profile_id}/{f.name}" for f in folder.iterdir() if f.is_file()]

    def file_exists(self, key: str, bucket: str | None = None) -> bool:
        base = self.model_dir if bucket == "models" else self.audio_dir
        return (base / key).exists()


# ── AWS S3 Storage ───────────────────────────────────────────────────────────

class S3StorageService(StorageService):
    """Production storage using AWS S3."""

    def __init__(self):
        import boto3
        from botocore.config import Config

        self._client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            ),
        )

    def upload_audio(self, file_bytes: bytes, voice_profile_id: str, filename: str, content_type: str = "audio/wav") -> str:
        ext = Path(filename).suffix or ".wav"
        key = f"recordings/{voice_profile_id}/{uuid.uuid4().hex}{ext}"
        self._client.put_object(
            Bucket=settings.s3_bucket_name, Key=key, Body=file_bytes,
            ContentType=content_type,
            Metadata={"voice_profile_id": voice_profile_id, "original_filename": filename},
        )
        return key

    def upload_processed_audio(self, file_bytes: bytes, voice_profile_id: str) -> str:
        key = f"processed/{voice_profile_id}/{uuid.uuid4().hex}.wav"
        self._client.put_object(Bucket=settings.s3_bucket_name, Key=key, Body=file_bytes, ContentType="audio/wav")
        return key

    def upload_model(self, model_bytes: bytes, voice_profile_id: str) -> str:
        key = f"models/{voice_profile_id}/voice_model.pth"
        self._client.put_object(Bucket=settings.s3_model_bucket, Key=key, Body=model_bytes, ContentType="application/octet-stream")
        return key

    def download_file(self, key: str, bucket: str | None = None) -> bytes:
        bucket = bucket or settings.s3_bucket_name
        response = self._client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()

    def download_model(self, key: str) -> bytes:
        return self.download_file(key, bucket=settings.s3_model_bucket)

    def get_presigned_url(self, key: str, bucket: str | None = None, expires_in: int = 3600) -> str:
        bucket = bucket or settings.s3_bucket_name
        return self._client.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=expires_in)

    def delete_file(self, key: str, bucket: str | None = None) -> None:
        bucket = bucket or settings.s3_bucket_name
        self._client.delete_object(Bucket=bucket, Key=key)

    def list_recordings(self, voice_profile_id: str) -> list[str]:
        prefix = f"processed/{voice_profile_id}/"
        response = self._client.list_objects_v2(Bucket=settings.s3_bucket_name, Prefix=prefix)
        return [obj["Key"] for obj in response.get("Contents", [])]

    def file_exists(self, key: str, bucket: str | None = None) -> bool:
        from botocore.exceptions import ClientError
        bucket = bucket or settings.s3_bucket_name
        try:
            self._client.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError:
            return False


# ── Factory ──────────────────────────────────────────────────────────────────

_storage_service: StorageService | None = None


def get_storage_service() -> StorageService:
    """Get or create the storage service singleton (local or S3 based on config)."""
    global _storage_service
    if _storage_service is None:
        if settings.storage_backend == "s3":
            try:
                import boto3  # noqa: F401
            except ImportError:
                raise RuntimeError(
                    "boto3 is required for S3 storage. "
                    "Install it with: pip install 'voiceforge[s3]'"
                )
            _storage_service = S3StorageService()
        else:
            _storage_service = LocalStorageService()
    return _storage_service
