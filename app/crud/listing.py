from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from .. import models, schemas


def create_listing(db: Session, listing: schemas.ListingCreate, seller_id: int, image_urls: list[str]):
    point = Point(listing.longitude, listing.latitude)
    geo_point = from_shape(point, srid=4326)

    db_listing = models.ProduceListing(
        seller_id=seller_id,
        category_id=listing.category_id,
        title=listing.title,
        description=listing.description or "",
        price_per_unit=listing.price_per_unit,
        unit=listing.unit,
        quantity_available=listing.quantity_available,
        location=geo_point,
        market_name=listing.market_name,
        images=image_urls,
        harvest_date=listing.harvest_date
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing
