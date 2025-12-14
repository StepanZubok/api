from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
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

# Create router WITHOUT tags in the decorator - add them here
router = APIRouter(
    prefix="",  # No prefix, routes at root level
    tags=["Authentication"]
)

def get_current_user_id(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


@router.post("/login")
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(data={"user_id": user.id})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="none",
        max_age=60 * 60,
    )

    return {
    "access_token": "token",
    "token_type": "bearer"
}



@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}