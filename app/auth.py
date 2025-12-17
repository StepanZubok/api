from datetime import datetime, timedelta
from typing import Optional
import logging

from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .database import get_db
from .models import UsersTable
from . import hash_verify, schemas
from .config import settings

# Config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

logger = logging.getLogger(__name__)


def get_current_user_id(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Resolve user from cookie first, then Authorization header."""
    cookie_token = request.cookies.get("access_token")
    final_token = cookie_token or token

    logger.info(f"Cookie token: {'present' if cookie_token else 'missing'}")
    logger.info(f"Auth header token: {'present' if token else 'missing'}")
    logger.info(f"All cookies: {request.cookies}")

    if not final_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(final_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UsersTable).filter(UsersTable.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    payload.update({"exp": expire, "type": "refresh"})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=schemas.Token)
def login(
    response: Response,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user, set access and refresh cookies, return access token."""
    user = db.query(UsersTable).filter(UsersTable.email == user_credentials.username).first()

    if not user or not hash_verify.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

    access_token = create_access_token(data={"user_id": user.id})
    refresh_token = create_refresh_token(data={"user_id": user.id})

    logger.info("Setting authentication cookies for user_id=%s", user.id)

    # CRITICAL: Do NOT set domain, let it default to the request origin
    # This allows cookies to work through proxy
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
        # domain is NOT set - this is critical!
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/",
        # domain is NOT set - this is critical!
    )

    logger.info("Login successful for user_id=%s", user.id)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh")
def refresh_token(response: Response, request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh_token cookie."""
    refresh_token = request.cookies.get("refresh_token")
    
    logger.info(f"Refresh request cookies: {request.cookies}")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("user_id")
        user = db.query(UsersTable).filter(UsersTable.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(data={"user_id": user.id})

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/",
        )

        logger.info("Access token refreshed for user_id=%s", user.id)

        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        logger.warning("Invalid refresh token")
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing auth cookies."""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    logger.info("User logged out; cookies cleared")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=schemas.UserBase)
def get_current_user(current_user: UsersTable = Depends(get_current_user_id)):
    """Return the current authenticated user."""
    return current_user