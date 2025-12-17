from fastapi import APIRouter, Depends, status, HTTPException, Response, Request
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import UsersTable
from . import hash_verify, schemas
from jose import JWTError, jwt
from datetime import datetime, timedelta
from .config import settings
from typing import Optional

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)



def get_current_user_id(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    # Prefer cookie, fallback to header token
    cookie_token = request.cookies.get("access_token")
    final_token = cookie_token or token

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
    expire = datetime.utcnow() + timedelta(minutes=1)
    to_encrypt.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encrypt, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encrypt = data.copy()
    expire = datetime.utcnow() + timedelta(days=0.00001)  # 7 days
    to_encrypt.update({"exp": expire, "type": "refresh"})
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
    refresh_token = create_refresh_token(data={"user_id": user.id})

    print(f"🍪 Setting access_token: {access_token[:20]}...")
    print(f"🍪 Setting refresh_token: {refresh_token[:20]}...")

    # ✅ Set cookies with SameSite=lax (works with proxy)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",  # ✅ Changed back to lax
        max_age=1,
        path="/",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",  # ✅ Changed back to lax
        max_age=1 * 0.000001,  # 7 days in seconds
        path="/",
    )
    
    print(f"✅ Both cookies should be set")
    print(f"🔍 Response headers: {response.headers}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
def refresh_token(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    try:
        # Decode and verify
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check it's a refresh token (not access token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("user_id")
        
        # Verify user still exists
        user = db.query(UsersTable).filter(UsersTable.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Create NEW access token
        new_access_token = create_access_token(data={"user_id": user.id})
        
        # ✅ Set the new access token in cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="lax",  # ✅ Changed back to lax
            max_age=1 * 0.000001,
            path="/",
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/logout")
def logout(response: Response):
    """Logout user by clearing cookies"""
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=schemas.UserBase)
def get_current_user(
    current_user: UsersTable = Depends(get_current_user_id)
):
    """Get current authenticated user"""
    return current_user