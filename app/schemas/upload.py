from pydantic import BaseModel
from typing import List


class ImageUploadResponse(BaseModel):
    url: str
    key: str
    size: int
    content_type: str


class UploadConfig(BaseModel):
    max_file_size: int = 5 * 1024 * 1024
    allowed_extensions: List[str] = ['.jpg', '.jpeg', '.png', '.gif', '.webp']