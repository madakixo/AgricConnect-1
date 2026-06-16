from functools import wraps

from flask import abort, g, jsonify, request
from jose import JWTError

from . import crud
from .database import get_db
from .utils.security import decode_access_token


def abort_json(status_code: int, detail: str, headers: dict | None = None):
    response = jsonify({"detail": detail})
    response.status_code = status_code
    if headers:
        response.headers.update(headers)
    abort(response)


def extract_bearer_token() -> str:
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        abort_json(401, "Missing or invalid bearer token", {"WWW-Authenticate": "Bearer"})
    return parts[1].strip()


def get_current_user():
    token = extract_bearer_token()

    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            abort_json(401, "Could not validate credentials", {"WWW-Authenticate": "Bearer"})
    except JWTError:
        abort_json(401, "Could not validate credentials", {"WWW-Authenticate": "Bearer"})

    db = get_db()
    user = crud.user.get_user_by_username(db, username=username)
    if user is None:
        abort_json(401, "Could not validate credentials", {"WWW-Authenticate": "Bearer"})
    if not user.is_active:
        abort_json(403, "Inactive users cannot access this resource")
    return user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        g.current_user = get_current_user()
        return f(*args, **kwargs)

    return decorated_function


def roles_required(*allowed_roles: str):
    normalized_roles = {role.lower() for role in allowed_roles}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            g.current_user = current_user
            current_role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
            if current_role.lower() not in normalized_roles:
                abort_json(403, "You do not have permission to access this resource")
            return f(*args, **kwargs)

        return decorated_function

    return decorator
