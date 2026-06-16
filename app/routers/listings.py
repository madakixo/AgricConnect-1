import json

from flask import Blueprint, current_app, g, jsonify, request
from pydantic import ValidationError

from .. import crud, dependencies, schemas
from ..database import get_db
from ..config import settings
from ..utils.cloudinary import upload_image

router = Blueprint("listings", __name__, url_prefix="/api/listings")


def _get_listing_payload() -> dict:
    if request.is_json:
        return request.get_json(silent=True) or {}

    payload = {}
    for field in (
        "title",
        "description",
        "category_id",
        "price_per_unit",
        "unit",
        "quantity_available",
        "market_name",
        "harvest_date",
        "latitude",
        "longitude",
    ):
        value = request.form.get(field)
        if value not in (None, ""):
            payload[field] = value
    return payload


def _get_external_image_urls() -> list[str]:
    image_urls = request.form.get("image_urls")
    if not image_urls:
        return []
    try:
        parsed = json.loads(image_urls)
    except json.JSONDecodeError:
        dependencies.abort_json(400, "image_urls must be a JSON array")
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        dependencies.abort_json(400, "image_urls must be a JSON array of strings")
    return parsed


def _upload_images() -> list[str]:
    files = request.files.getlist("images")
    if not files:
        return _get_external_image_urls()
    if len(files) > settings.MAX_IMAGE_COUNT:
        dependencies.abort_json(400, f"A maximum of {settings.MAX_IMAGE_COUNT} images is allowed")
    if not settings.cloudinary_enabled:
        dependencies.abort_json(
            400,
            "Image uploads require Cloudinary configuration. Disable uploads or provide hosted image_urls instead.",
        )

    image_urls = []
    for image in files:
        mimetype = (image.mimetype or "").lower()
        if mimetype not in settings.allowed_image_mime_types:
            dependencies.abort_json(400, f"Unsupported image type: {mimetype or 'unknown'}")
        try:
            image_urls.append(upload_image(image))
        except Exception:
            current_app.logger.exception("Cloudinary upload failed")
            dependencies.abort_json(502, "Image upload failed")
    return image_urls


@router.route("/", methods=["POST"])
@dependencies.roles_required("seller", "admin")
def create_listing():
    current_user = g.current_user
    db = get_db()
    payload = _get_listing_payload()
    image_urls = _upload_images()
    try:
        listing_data = schemas.ListingCreate(**payload)
    except ValidationError as exc:
        dependencies.abort_json(400, exc.errors()[0]["msg"])

    new_listing = crud.create_listing(db, listing_data, current_user.id, image_urls)

    return jsonify({
        "message": "Listing created successfully",
        "listing_id": new_listing.id
    }), 201
