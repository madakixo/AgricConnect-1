import logging

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import settings
from .database import db_session
from .utils.cloudinary import configure_cloudinary

app = Flask(__name__)
app.title = "Agri-Marketplace Northern Nigeria"
app.config.update(
    DEBUG=settings.DEBUG and not settings.is_production,
    MAX_CONTENT_LENGTH=settings.MAX_CONTENT_LENGTH,
    MAX_FORM_MEMORY_SIZE=settings.MAX_FORM_MEMORY_SIZE,
    MAX_FORM_PARTS=settings.MAX_FORM_PARTS,
    SESSION_COOKIE_SECURE=settings.session_cookie_secure,
    SESSION_COOKIE_HTTPONLY=settings.SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE=settings.SESSION_COOKIE_SAMESITE,
    TRUSTED_HOSTS=settings.trusted_hosts if settings.trusted_hosts else None,
)

logging.basicConfig(level=logging.INFO)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
configure_cloudinary()

cors_origins = settings.cors_allowed_origins or []
if cors_origins:
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.after_request
def apply_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'none'; frame-ancestors 'self'; img-src 'self' https: data:; "
        "connect-src 'self' https:; style-src 'self' 'unsafe-inline'; base-uri 'self'; form-action 'self'",
    )
    return response


@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(413)
@app.errorhandler(422)
@app.errorhandler(500)
def handle_json_errors(error):
    status_code = getattr(error, "code", 500)
    description = getattr(error, "description", "Internal server error")
    return jsonify({"detail": description}), status_code


@app.get("/api/health")
def healthcheck():
    return jsonify(
        {
            "status": "ok",
            "environment": settings.APP_ENV,
            "cloudinary_enabled": settings.cloudinary_enabled,
        }
    )

# Import and register blueprints
from .routers import listings, auth
app.register_blueprint(listings.router)
app.register_blueprint(auth.router)
