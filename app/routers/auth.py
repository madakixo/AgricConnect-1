from flask import Blueprint, request, jsonify, abort
from sqlalchemy.orm import Session
from datetime import timedelta
from .. import schemas, crud, dependencies
from ..database import get_db
from ..config import settings
from ..utils.security import create_access_token, verify_password

router = Blueprint("auth", __name__, url_prefix="/api/auth")

@router.route("/register", methods=["POST"])
def register():
    db = get_db()
    data = request.get_json()
    # Simple validation manually since we dropped Pydantic at the request level
    # Ideally should use Marshmallow or Pydantic manually
    if not data:
        abort(400, description="Invalid body")
        
    try:
        user_in = schemas.UserCreate(**data)
    except Exception as e:
        abort(400, description=str(e))

    db_user = crud.user.get_user_by_username(db, user_in.username)
    if db_user:
        return jsonify({"detail": "Username already registered"}), 400
    db_email = crud.user.get_user_by_email(db, user_in.email)
    if db_email:
        return jsonify({"detail": "Email already registered"}), 400
    
    new_user = crud.user.create_user(db, user_in)
    # Serialize manually or use Pydantic's .dict/.model_dump if available
    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "is_active": new_user.is_active
    }), 201


@router.route("/token", methods=["POST"])
def login_for_access_token():
    # OAuth2PasswordRequestForm expects form-data 'username' and 'password'
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
         # Fallback to json if form not sent (API flexibility)
         json_data = request.get_json(silent=True)
         if json_data:
             username = json_data.get("username")
             password = json_data.get("password")

    db = get_db()
    user = crud.user.get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return jsonify({"detail": "Incorrect username or password"}), 401, {"WWW-Authenticate": "Bearer"}
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return jsonify({"access_token": access_token, "token_type": "bearer"})
