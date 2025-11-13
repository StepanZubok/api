from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db
from .models import UsersTable
from . import hash_verify, schemas
from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter(tags = ["Authentication"])
auth_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user_id(token : str = Depends(auth_scheme), db : Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id : int = payload.get("user_id")
        if id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        token_data = schemas.TokenData(id = id)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    user = db.query(UsersTable).filter(UsersTable.id == token_data.id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    return user.id

def create_access_token(data : dict):
    to_encrypt = data.copy()
    expiration_date = datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encrypt.update({"exp" : expiration_date})

    return jwt.encode(to_encrypt, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=schemas.Token)
def login(user_credentials : OAuth2PasswordRequestForm = Depends() ,db : Session = Depends(get_db)):
    user = db.query(UsersTable).filter(UsersTable.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    if not hash_verify.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    access_token = create_access_token(data = {"user_id" : user.id})

    return {"access_token" : access_token} 

