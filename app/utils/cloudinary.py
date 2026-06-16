import logging

import cloudinary
import cloudinary.uploader

from ..config import settings

logger = logging.getLogger(__name__)


def configure_cloudinary() -> None:
    if not settings.cloudinary_enabled:
        logger.info("Cloudinary uploads disabled")
        return

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def upload_image(file_storage, folder: str = "agri-marketplace/northern-nigeria") -> str:
    if not settings.cloudinary_enabled:
        raise RuntimeError("Cloudinary uploads are disabled")

    result = cloudinary.uploader.upload(
        file_storage,
        folder=folder,
        resource_type="image",
    )
    return result["secure_url"]
