from app.database import engine
from app.models import user, produce_listing
user.Base.metadata.create_all(bind=engine)
produce_listing.Base.metadata.create_all(bind=engine)
