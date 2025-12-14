from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import UsersTable
from . import hash_verify, schemas
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user_id(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get current user from either:
    1. HTTP-only cookie (for web frontend)
    2. Authorization header (for tests/API clients)
    """
    # Try cookie first (for frontend)
    cookie_token = request.cookies.get("access_token")
    
    # Use cookie if available, otherwise use header token
    final_token = cookie_token if cookie_token else token
    
    if not final_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(final_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UsersTable).filter(UsersTable.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def create_access_token(data: dict):
    to_encrypt = data.copy()
    expiration_date = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encrypt.update({"exp": expiration_date})
    return jwt.encode(to_encrypt, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=schemas.Token)
def login(
    response: Response,
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(UsersTable).filter(
        UsersTable.email == user_credentials.username
    ).first()

    if not user or not hash_verify.verify(
        user_credentials.password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"user_id": user.id})

    # Set cookie for web frontend
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="none",
        max_age=60 * 60,
    )

    # Return token for tests/API clients
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/logout")
def logout(response: Response):
    #Logout user by clearing cookie
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}