from fastapi import APIRouter, HTTPException, status, Depends
from app import hash_verify, schemas, models, database
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id : int, db : Session = Depends(database.get_db)):
    user = db.query(models.UsersTable).filter(models.UsersTable.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user : schemas.UserCreate, db : Session = Depends(database.get_db)):

    hashed_password = hash_verify.hash(user.password)

    user.password = hashed_password
    new_user = models.UsersTable(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

