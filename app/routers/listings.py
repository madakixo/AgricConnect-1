from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import cloudinary.uploader
from .. import schemas, dependencies, crud, utils
from ..database import get_db

router = Blueprint("listings", __name__, url_prefix="/api/listings")

@router.route("/", methods=["POST"])
@dependencies.login_required
def create_listing():
    current_user = request.current_user
    db = get_db()
    
    if current_user.role != "seller":
        abort(403, description="Only sellers can create listings")

    # Extract form data
    title = request.form.get("title")
    description = request.form.get("description")
    category_id = request.form.get("category_id")
    price_per_unit = request.form.get("price_per_unit")
    unit = request.form.get("unit")
    quantity_available = request.form.get("quantity_available")
    market_name = request.form.get("market_name")
    harvest_date = request.form.get("harvest_date")
    latitude = request.form.get("latitude")
    longitude = request.form.get("longitude")

    if not all([title, category_id, price_per_unit, unit, quantity_available, latitude, longitude]):
         abort(400, description="Missing required fields")

    # Handle file uploads
    images = request.files.getlist("images")
    image_urls = []
    
    for img in images:
        if img.mimetype.startswith("image/"):
            # Cloudinary upload
            try:
                result = cloudinary.uploader.upload(
                    img,
                    folder="agri-marketplace/northern-nigeria",
                    resource_type="image"
                )
                image_urls.append(result["secure_url"])
            except Exception as e:
                # Log error or handle gracefully
                pass

    try:
        listing_data = schemas.ListingCreate(
            title=title,
            description=description,
            category_id=int(category_id),
            price_per_unit=float(price_per_unit),
            unit=unit,
            quantity_available=float(quantity_available),
            market_name=market_name,
            harvest_date=harvest_date,
            latitude=float(latitude),
            longitude=float(longitude)
        )
    except ValueError as e:
        abort(400, description=f"Invalid data format: {str(e)}")

    new_listing = crud.create_listing(db, listing_data, current_user.id, image_urls)
    
    return jsonify({
        "message": "Kayayyaki an ƙirƙira cikin nasara!",  # Hausa: Listing created successfully!
        "listing_id": new_listing.id
    }), 201
