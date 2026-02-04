from flask import Flask
from flask_cors import CORS
import cloudinary
from .config import settings
from .database import engine, db_session
from . import models
# from .routers import listings, auth # Import these later after converting them to avoid circular imports or errors during transition

# Create tables (use Alembic in production!)
models.Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.title = "Agri-Marketplace Northern Nigeria" # Flask doesn't have title arg in init, setting as attribute if needed or just metadata

# CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Cloudinary setup
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

# Import and register blueprints
from .routers import listings, auth
app.register_blueprint(listings.router)
app.register_blueprint(auth.router)
