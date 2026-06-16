from datetime import timedelta

from flask import Blueprint, Response, g, jsonify, request
from pydantic import ValidationError

from .. import crud, dependencies, schemas
from ..database import get_db
from ..config import settings
from ..utils.security import create_access_token

router = Blueprint("auth", __name__, url_prefix="/api/auth")


def serialize_user(user) -> dict:
    role = user.role.value if hasattr(user.role, "value") else str(user.role)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def build_token_response(user) -> Response:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    response = jsonify(
        {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": serialize_user(user),
        }
    )
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response

@router.route("/register", methods=["POST"])
def register():
    db = get_db()
    data = request.get_json(silent=True)
    if not data:
        dependencies.abort_json(400, "Invalid JSON body")

    try:
        user_in = schemas.UserCreate(**data)
    except ValidationError as exc:
        dependencies.abort_json(400, exc.errors()[0]["msg"])

    db_user = crud.user.get_user_by_username(db, user_in.username)
    if db_user:
        return jsonify({"detail": "Username already registered"}), 400
    db_email = crud.user.get_user_by_email(db, user_in.email)
    if db_email:
        return jsonify({"detail": "Email already registered"}), 400

    new_user = crud.user.create_user(db, user_in)
    return jsonify(serialize_user(new_user)), 201


def _get_login_payload() -> schemas.LoginRequest:
    if request.is_json:
        payload = request.get_json(silent=True) or {}
    else:
        payload = {
            "username": request.form.get("username", ""),
            "password": request.form.get("password", ""),
        }
    try:
        return schemas.LoginRequest(**payload)
    except ValidationError as exc:
        dependencies.abort_json(400, exc.errors()[0]["msg"])


@router.route("/login", methods=["POST"])
@router.route("/token", methods=["POST"])
def login_for_access_token():
    login_data = _get_login_payload()
    db = get_db()
    user = crud.user.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        dependencies.abort_json(401, "Incorrect username or password", {"WWW-Authenticate": "Bearer"})
    return build_token_response(user)


@router.route("/me", methods=["GET"])
@dependencies.login_required
def current_user():
    return jsonify(serialize_user(g.current_user))
