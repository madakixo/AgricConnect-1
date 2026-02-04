from sqlalchemy import Column, Integer, String, Float, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import TIMESTAMP
from geoalchemy2 import Geography
from ..database import Base


class ProduceListing(Base):
    __tablename__ = "produce_listings"

    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title = Column(String, nullable=False, index=True)
    description = Column(String)
    price_per_unit = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # e.g. "kg", "basket", "bag"
    quantity_available = Column(Float, nullable=False)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    market_name = Column(String(100))
    images = Column(ARRAY(String))  # list of Cloudinary URLs
    harvest_date = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")
