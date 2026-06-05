import os
import uuid
import shutil
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {
    "resume": {".pdf", ".docx"},
    "audio": {".mp3", ".wav", ".m4a", ".webm", ".ogg"},
    "document": {".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg"},
    "image": {".png", ".jpg", ".jpeg", ".gif", ".webp"},
}


def validate_file(file: UploadFile, file_category: str = "document") -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    ext = Path(file.filename).suffix.lower()
    allowed = ALLOWED_EXTENSIONS.get(file_category, ALLOWED_EXTENSIONS["document"])
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Allowed: {', '.join(allowed)}"
        )
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB"
        )


async def save_file(file: UploadFile, folder: str) -> str:
    upload_dir = Path(settings.UPLOAD_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    logger.info(f"File saved: {file_path}")
    return f"/uploads/{folder}/{unique_name}"


def get_file_url(path: str) -> str:
    return path


def delete_file(path: str) -> bool:
    try:
        full_path = Path(path.lstrip("/"))
        if full_path.exists():
            full_path.unlink()
            return True
    except Exception as e:
        logger.error(f"Error deleting file {path}: {e}")
    return False
