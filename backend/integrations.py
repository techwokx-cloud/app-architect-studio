"""
Optional external integrations.

Every integration is configured exclusively through environment variables so the
repository can be deployed first and secrets can be added later.
"""

from __future__ import annotations

import base64
import os
import time
from typing import Any, Optional

import requests


def _configured(*names: str) -> bool:
    return all(bool(os.getenv(name)) for name in names)


def _env(*names: str, default: Optional[str] = None) -> Optional[str]:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _storage_configured() -> bool:
    return bool(
        _env("VULTR_OBJECT_STORAGE_ENDPOINT", "CLOUDFLARE_R2_ENDPOINT")
        and _env("VULTR_OBJECT_STORAGE_ACCESS_KEY", "CLOUDFLARE_R2_ACCESS_KEY_ID")
        and _env("VULTR_OBJECT_STORAGE_SECRET_KEY", "CLOUDFLARE_R2_SECRET_ACCESS_KEY")
        and _env("VULTR_OBJECT_STORAGE_BUCKET", "CLOUDFLARE_R2_BUCKET")
    )


def integration_status() -> dict[str, Any]:
    return {
        "watsonx": _configured("WATSONX_API_KEY", "WATSONX_PROJECT_ID"),
        "speechmatics": _configured("SPEECHMATICS_API_KEY"),
        "google": _configured("GOOGLE_API_KEY"),
        "vultr_object_storage": _storage_configured(),
    }


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value


def transcribe_with_speechmatics(
    audio_base64: str,
    language: str = "en",
    audio_format: str = "wav",
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    """Submit base64 audio to Speechmatics and poll for a transcript."""
    api_key = require_env("SPEECHMATICS_API_KEY")
    audio_bytes = base64.b64decode(audio_base64)

    headers = {"Authorization": f"Bearer {api_key}"}
    config = {
        "type": "transcription",
        "transcription_config": {
            "language": language,
            "operating_point": "enhanced",
        },
    }
    files = {
        "data_file": (f"audio.{audio_format}", audio_bytes),
        "config": (None, __import__("json").dumps(config), "application/json"),
    }

    job_response = requests.post(
        "https://asr.api.speechmatics.com/v2/jobs",
        headers=headers,
        files=files,
        timeout=30,
    )
    job_response.raise_for_status()
    job_id = job_response.json()["id"]

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        status_response = requests.get(
            f"https://asr.api.speechmatics.com/v2/jobs/{job_id}",
            headers=headers,
            timeout=15,
        )
        status_response.raise_for_status()
        status = status_response.json()["job"]["status"]
        if status == "done":
            transcript_response = requests.get(
                f"https://asr.api.speechmatics.com/v2/jobs/{job_id}/transcript",
                headers=headers,
                params={"format": "txt"},
                timeout=30,
            )
            transcript_response.raise_for_status()
            return {"job_id": job_id, "transcript": transcript_response.text}
        if status == "rejected":
            raise RuntimeError(f"Speechmatics rejected job {job_id}")
        time.sleep(3)

    raise TimeoutError(f"Speechmatics job {job_id} did not finish in time")


def generate_with_google(prompt: str, model: Optional[str] = None) -> dict[str, Any]:
    """Generic Google Gemini text generation hook."""
    api_key = require_env("GOOGLE_API_KEY")
    model_name = model or os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model_name}:generateContent"
    )
    response = requests.post(
        url,
        params={"key": api_key},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    text = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )
    return {"model": model_name, "text": text, "raw": data}


def save_to_vultr_object_storage(
    key: str,
    content: str,
    content_type: str = "text/plain",
) -> dict[str, Any]:
    """Save text content to Vultr Object Storage (S3-compatible)."""
    import boto3

    endpoint = _env("VULTR_OBJECT_STORAGE_ENDPOINT", "CLOUDFLARE_R2_ENDPOINT")
    access_key = _env(
        "VULTR_OBJECT_STORAGE_ACCESS_KEY",
        "CLOUDFLARE_R2_ACCESS_KEY_ID",
    )
    secret_key = _env(
        "VULTR_OBJECT_STORAGE_SECRET_KEY",
        "CLOUDFLARE_R2_SECRET_ACCESS_KEY",
    )
    bucket = _env("VULTR_OBJECT_STORAGE_BUCKET", "CLOUDFLARE_R2_BUCKET")
    region = _env("VULTR_OBJECT_STORAGE_REGION", "CLOUDFLARE_R2_REGION", default="ewr1")

    if not endpoint or not access_key or not secret_key or not bucket:
        raise RuntimeError("Vultr Object Storage is not configured")

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
    )
    client.put_object(
        Bucket=bucket,
        Key=key,
        Body=content.encode("utf-8"),
        ContentType=content_type,
    )
    return {"bucket": bucket, "key": key, "endpoint": endpoint}


