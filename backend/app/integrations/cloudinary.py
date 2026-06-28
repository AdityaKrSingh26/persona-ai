import cloudinary
import cloudinary.uploader

from app.config import settings

# Configure once at import time — credentials come from settings
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


async def upload_pdf(file_bytes: bytes, filename: str) -> str:
    """Upload PDF bytes to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        file_bytes,
        resource_type="raw",  # raw = non-image files (PDFs, docs, etc.)
        folder="ai-call/resumes",
        public_id=filename,
        overwrite=True,
    )
    return result["secure_url"]
