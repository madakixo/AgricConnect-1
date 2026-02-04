from flask import request, abort
from functools import wraps
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from . import schemas, crud, models
from .database import get_db
from .config import settings
from .utils.security import verify_password


def get_current_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
         abort(401, description="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
             abort(401, description="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
        token_data = schemas.TokenData(username=username)
    except JWTError:
         abort(401, description="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    db = get_db()
    user = crud.user.get_user_by_username(db, username=token_data.username)
    if user is None:
         abort(401, description="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    return user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        request.current_user = current_user
        return f(*args, **kwargs)
    return decorated_function
